import serial
import struct
import time
from digi.xbee.devices import XBeeDevice

# XBee serial port
PORT = "/dev/tty.usbserial-0001"
BAUD_RATE = 9600  # Match your XBee settings

# Maximum attempts to open the device
MAX_RETRIES = 10

# Open XBee with retries
def open_xbee_device(port, baud_rate, max_retries=10):
    device = XBeeDevice(port, baud_rate)
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries}: Opening XBee device...")
            device.open()
            print("XBee device opened successfully!")
            return device  # Return the opened device
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(1)  # Wait before retrying
            else:
                print("Failed to open XBee device after multiple attempts.")
                return None
    return None

# Callback Function for Incoming Data
def data_received_callback(xbee_message):
    sender = xbee_message.remote_device.get_64bit_addr()  # Get sender address
    raw_data = xbee_message.data  # Received binary data

    # Ensure correct data length
    if len(raw_data) != 7:
        return  # Ignore malformed packets

    # Extract and unpack wind speed (Little-Endian float)
    wind_speed = struct.unpack("<f", raw_data[1:5])[0]
    wind_mph = wind_speed * 2.23694  # Convert to mph
    wind_knot = wind_speed * 1.94384  # Convert to knots

    # Print only sender address & wind speed
    print(f"From {sender}: Wind Speed =\n{wind_speed:.2f} m/s\n{wind_mph:.2f} mph\n{wind_knot:.2f} knots")

# Try to Open XBee Device
device = open_xbee_device(PORT, BAUD_RATE, MAX_RETRIES)

if device:
    try:
        print("Listening for XBee broadcast messages...")
        device.add_data_received_callback(data_received_callback)
        input("Press Enter to exit...\n")  # Keeps the program running

    except Exception as e:
        print(f"Error: {e}")

    finally:
        device.close()
        print("XBee receiver closed.")
else:
    print("Exiting program due to XBee connection failure.")