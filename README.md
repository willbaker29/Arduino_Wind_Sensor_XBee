# Arduino Wind Sensor + XBee Project

This project reads wind speed from an RS485 wind sensor and transmits it wirelessly via an XBee module.

## Features
- Reads wind speed via RS485 (Modbus RTU) using DFRobot SEN0483.
- Packages data with padding and checksum
- Transmits structured data over XBee
- Receives and decodes package at backend

## Hardware Requirements
- Arduino Mega 2560
- RS485 MAX485 Module
- DFRobot RS485 Wind Speed Sensor (SEN0483)
- XBee Module (Configured in API Mode)
- 12V Power Supply for Sensor
- XBee to USB module

## Wiring Diagram
| **Device**   | **Arduino Mega** |
|-------------|----------------|
| RS485 RO    | Pin 19 (RX1) |
| RS485 DI    | Pin 18 (TX1) |
| RS485 DE/RE | Pin 9 |
| XBee TX/RX  | Serial (Pins 0, 1) |
| Sensor VCC  | 12V |
| Sensor GND  | GND |

![Arduino Build](Images/arduinoMegaSender.png)

![Full Sensor](Images/windSensor.png)

The Python Code uses the Digi XBee library: https://xbplib.readthedocs.io/en/latest/index.html

Pip command: pip install digi-xbee

## To Do
- 3D print enclosure
- Store data in Database
- Create display 
- Add direction sensor
- Pull additional data from web (tides and met office)