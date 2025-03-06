import serial
import struct
from digi.xbee.devices import XBeeDevice

# ✅ Set your XBee serial port
PORT = "/dev/tty.usbserial-0001"
BAUD_RATE = 9600  # Match your XBee settings

# ✅ Open XBee Device
device = XBeeDevice(PORT, BAUD_RATE)

def data_received_callback(xbee_message):
    sender = xbee_message.remote_device.get_64bit_addr()  # Get sender address
    raw_data = xbee_message.data  # Received binary data

    # ✅ Ensure correct data length
    if len(raw_data) != 7:
        return  # Ignore malformed packets

    # ✅ Extract and unpack wind speed (Little-Endian float)
    wind_speed = struct.unpack("<f", raw_data[1:5])[0]

    # ✅ Print only sender address & wind speed
    print(f"📡 From {sender}: Wind Speed = {wind_speed:.2f} m/s")

try:
    device.open()
    print("✅ Listening for XBee broadcast messages...")
    device.add_data_received_callback(data_received_callback)
    input("Press Enter to exit...\n")  # Keeps the program running

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    device.close()
    print("🔴 XBee receiver closed.")