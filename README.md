# Aston Martin BVAT Project

This project is being developed independently to support one of Aston Martin's ADAS-related initiatives.  
Special thanks to the ADAS team for providing support with test driving, which enables us to collect valuable data and compare the performance of different brands' ADAS features.

The goal is to evaluate and understand how various implementations of Adaptive Cruise Control (ACC) and Autonomous Emergency Braking (AEB) perform across manufacturers.


## Introduction

This project focuses on analysing two key ADAS (Advanced Driver Assistance Systems) features: **Adaptive Cruise Control (ACC)** and **Autonomous Emergency Braking (AEB)**.

The repository contains two main components:
- A **Python script** for logging data from an STM32-based hardware module.
- A **Jupyter Notebook** for analysing the collected data using the logged outputs.

The analysis relies on KPIs that can be measured using a custom-built STM32 hardware setup. While this setup is limited to features measurable via acceleration and speed data from an accelerometer and GPS sensor, it offers a cost-effective alternative to commercial systems. Given the high cost of market-available ADAS testing modules, this project aims to maximize budget efficiency by utilising affordable STM32-based hardware.

> This README provides an introductory overview only.  
> Please refer to the **usage manual** and follow the instructions carefully to ensure proper data collection.

## Using Python Script to Log Data – `BVAT_logger.py`

> [!NOTE] 
> We assume that your USB port has already been configured by IT support to allow the STM32 device to connect properly to your work laptop.

The `BVAT_logger.py` script is designed to log data from the STM32 hardware. While no advanced setup is required at this stage, the script will prompt you to choose:
1. The **serial port** (look for one containing `tty.`).
2. The **baud rate**, which should be set to `115200`.  
   > This value is fixed based on the STM32 hardware configuration and cannot be changed from the software side.

Once these two inputs are provided, the logger will begin running and wait for incoming messages from the STM32 hardware.

### How It Works

- On the **hardware side**, you can toggle logging (start/stop) using a push-button.
- Each logging session will be saved to a separate `.csv` file in the `/log` folder.
- The `/log` directory will be created automatically if it doesn't already exist.

This script provides a simple and reliable way to capture data logs for further analysis.
