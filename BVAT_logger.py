import serial
import serial.tools.list_ports
import csv
import os
import sys
import signal
import re
from datetime import datetime
import time

# --- Global Variables ---
# These will be managed by the start/stop logging functions
ser = None
csv_file = None
csv_writer = None
is_logging = False
current_csv_filename = ""

def parse_data_line(line):
    """
    Parses a 'DATA' line from the STM32 using regular expressions for robustness.
    --- UPDATED --- Now matches the format without Latitude and Longitude.
    Expected format: DATA, Accel(X:..., Y:..., Z:...), GPS(Fix:..., Spd:...)
    """
    # --- FIX ---: The regex pattern has been simplified to match your device's output.
    pattern = re.compile(
        r"DATA, Accel\(X: *(-?[\d.]+), Y: *(-?[\d.]+), Z: *(-?[\d.]+)\), "
        r"GPS\(Fix: *(\d), Spd: *(-?[\d.]+)\)"
    )
    
    match = pattern.search(line)
    
    if not match:
        # This will happen for the [PARSING_RMC] lines, which is normal.
        return None

    try:
        # --- FIX ---: Group indices are updated to match the new regex.
        return {
            "accel_x": float(match.group(1)),
            "accel_y": float(match.group(2)),
            "accel_z": float(match.group(3)),
            "gps_fix": int(match.group(4)),
            "gps_speed": float(match.group(5))
        }
    except (ValueError, IndexError) as e:
        print(f"⚠️  Error parsing matched values: {line} | Error: {e}")
        return None

def start_logging():
    """Creates a new timestamped CSV file and prepares it for writing."""
    global csv_file, csv_writer, is_logging, current_csv_filename
    
    if is_logging:
        stop_logging()
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("logs", exist_ok=True)
    current_csv_filename = os.path.join("logs", f"datalog_{timestamp}.csv")
    
    try:
        csv_file = open(current_csv_filename, 'w', newline='', encoding='utf-8')
        csv_writer = csv.writer(csv_file)
        
        # --- FIX ---: CSV header updated to remove Lat/Lon columns.
        csv_writer.writerow([
            "Timestamp", 
            "Accel_X_g", "Accel_Y_g", "Accel_Z_g", 
            "GPS_Fix", "Speed_kmh"
        ])
        
        is_logging = True
        print(f"\n🟢 Logging started → {current_csv_filename}")
        
    except IOError as e:
        print(f"❌ Error creating log file: {e}")
        csv_file = None
        is_logging = False

def stop_logging():
    """Stops the current logging session and closes the CSV file."""
    global csv_file, is_logging, csv_writer
    
    if csv_file:
        csv_file.close()
        print(f"\n🛑 Logging stopped. File saved: {current_csv_filename}")
        csv_file = None
        csv_writer = None

    is_logging = False

def process_serial_line(line):
    """
    Processes a single line of text received from the serial port.
    This function acts as a controller, deciding what to do with the incoming line.
    """
    global csv_writer
    
    if "=== Data Logging STARTED ===" in line:
        start_logging()
    elif "=== Data Logging STOPPED ===" in line:
        stop_logging()
    elif line.startswith("DATA,") and is_logging:
        parsed_data = parse_data_line(line)
        if parsed_data and csv_writer:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # --- FIX ---: Data writing updated to match the new parsed data structure.
            csv_writer.writerow([
                timestamp,
                parsed_data["accel_x"],
                parsed_data["accel_y"],
                parsed_data["accel_z"],
                parsed_data["gps_fix"],
                parsed_data["gps_speed"]
            ])
            csv_file.flush()

def list_serial_ports():
    """Lists available serial ports and returns them."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
        return None
    print("Available serial ports:")
    for i, port_info in enumerate(ports):
        print(f"  [{i}]: {port_info.device} - {port_info.description or 'N/A'}")
    return ports

def select_serial_port(ports):
    """Prompts the user to select a serial port, with auto-detection."""
    if not ports: return None
    
    default_port = None
    for port_info in ports:
        if "stlink" in (port_info.description or "").lower() or \
           "st-link" in (port_info.manufacturer or "").lower():
            default_port = port_info.device
            print(f"\n✨ Auto-detected ST-Link on port: {default_port}")
            break
    
    try:
        prompt = f"Enter port number or full name (default: {default_port}): " if default_port else "Enter port number or full name: "
        choice = input(prompt).strip()
        
        if not choice and default_port:
            return default_port
        
        try:
            port_idx = int(choice)
            if 0 <= port_idx < len(ports):
                return ports[port_idx].device
            else:
                print("Invalid port number.")
                return None
        except ValueError:
            return choice
            
    except (KeyboardInterrupt, EOFError):
        print("\nSelection cancelled.")
        return None

def get_baud_rate(default=115200):
    """Prompts the user for a baud rate."""
    try:
        baud_str = input(f"⚙️  Enter baud rate (default: {default}): ").strip()
        return int(baud_str) if baud_str else default
    except ValueError:
        print("Invalid number, using default.")
        return default
    except (KeyboardInterrupt, EOFError):
        print("\nSelection cancelled.")
        return None

def signal_handler(sig, frame):
    """Handles Ctrl+C presses for a graceful shutdown."""
    print("\n\n🔌 Disconnecting and cleaning up...")
    stop_logging()
    if ser and ser.is_open:
        ser.close()
        print("Serial port closed.")
    sys.exit(0)

def main():
    """Main function to set up and run the data logger."""
    global ser
    signal.signal(signal.SIGINT, signal_handler)

    print("--- STM32 Combined Data Logger ---")
    
    available_ports = list_serial_ports()
    if not available_ports: return

    port = select_serial_port(available_ports)
    if not port:
        print("No serial port selected. Exiting.")
        return

    baud = get_baud_rate()
    if not baud:
        print("No baud rate selected. Exiting.")
        return

    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"\n✅ Connected to {port} at {baud} baud.")
    except serial.SerialException as e:
        print(f"❌ Failed to connect: {e}")
        return

    print("📡 Listening for STM32 output... Press the device button to start/stop logging.")
    print("   Press Ctrl+C in this window to exit.")
    
    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"STM32 → {line}")
                        process_serial_line(line)
                except serial.SerialException as e:
                    print(f"❌ Serial Error: {e}. Disconnecting.")
                    break
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        signal_handler(None, None)
    finally:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
