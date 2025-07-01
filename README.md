# Aston Martin BVAT Project

## Introduction

This project focuses on analysing two key ADAS (Advanced Driver Assistance Systems) features: **Adaptive Cruise Control (ACC)** and **Autonomous Emergency Braking (AEB)**.

The repository contains two main components:
- A **Python script** for logging data from an STM32-based hardware module.
- A **Jupyter Notebook** for analyzing the collected data using the logged outputs.

The analysis relies on KPIs that can be measured using a custom-built STM32 hardware setup. While this setup is limited to features measurable via acceleration and speed data from an accelerometer and GPS sensor, it offers a cost-effective alternative to commercial systems. Given the high cost of market-available ADAS testing modules, this project aims to maximize budget efficiency by utilizing affordable STM32-based hardware.

> This README provides an introductory overview only.  
> Please refer to the **usage manual** and follow the instructions carefully to ensure proper data collection.
