import serial
import struct
import time
import sqlite3
from digi.xbee.devices import XBeeDevice

# XBee serial port
PORT = "/dev/tty.usbserial-0001"
BAUD_RATE = 9600  # Match your XBee settings
MAX_RETRIES = 10  # Maximum attempts to open the device
DB_FILE = "wind_data.db"  # SQLite DB file

# Initialize SQLite DB
def init_db():
    """Creates the SQLite database and table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wind_speed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (datetime('now', 'localtime')),
            sender TEXT,
            speed_mps REAL,
            speed_mph REAL,
            speed_knots REAL
        )
    ''')
    
    conn.commit()
    conn.close()

# Insert Wind Speed Data into DB
def insert_wind_speed(sender, speed_mps, speed_mph, speed_knots):
    """Insert wind speed data into SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO wind_speed (sender, speed_mps, speed_mph, speed_knots) VALUES (?, ?, ?, ?)",
        (sender, speed_mps, speed_mph, speed_knots),
    )
    
    conn.commit()
    conn.close()

# Open XBee Device with Retries
def open_xbee_device(port, baud_rate, max_retries=10):
    """Attempts to open the XBee device, retrying if needed."""
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

# Callback Function for Receiving XBee Data
def data_received_callback(xbee_message):
    sender = str(xbee_message.remote_device.get_64bit_addr())  # Convert sender address to string
    raw_data = xbee_message.data  # Received binary data

    # Ensure correct data length
    if len(raw_data) != 7:
        print(f"⚠️ Malformed packet received from {sender}")
        return  # Ignore malformed packets

    # Extract and unpack wind speed (Little-Endian float)
    wind_speed = struct.unpack("<f", raw_data[1:5])[0]
    wind_mph = wind_speed * 2.23694  # Convert to mph
    wind_knots = wind_speed * 1.94384  # Convert to knots

    # Store in DB
    insert_wind_speed(sender, wind_speed, wind_mph, wind_knots)

    # ✅ Print rx data
    print(f"📡 From {sender}:")
    print(f"   🌬️ Wind Speed: {wind_speed:.2f} m/s")
    print(f"   🌬️ Wind Speed: {wind_mph:.2f} mph")
    print(f"   🌬️ Wind Speed: {wind_knots:.2f} knots")
    print(f"✅ Data saved to database.\n")

# Initialize DB
init_db()

# Attempt to Open XBee Device
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