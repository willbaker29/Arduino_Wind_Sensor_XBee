#include <XBee.h>

#define RS485Transmit HIGH
#define RS485Receive  LOW

// RS485 Control Pin
const int rs485ControlPin = 9;

// Wind Sensor Modbus Request (Address 0x02, Read Wind Speed)
const byte windSpeedRequest[] = {0x02, 0x03, 0x00, 0x00, 0x00, 0x01, 0x84, 0x39};
byte response[7];

// XBee Setup
XBee xbee;

// Data Structure for Transmission
typedef struct __attribute__((packed)) {
    uint8_t before_wrapper;  // Padding byte (fixed value)
    float wind_speed;        // Wind Speed (m/s)
    uint8_t after_wrapper;   // Padding byte (fixed value)
    uint8_t checksum;        // Checksum (XOR of all bytes)
} WindData;

// Compute XOR Checksum
uint8_t computeChecksum(WindData *data) {
    uint8_t *ptr = (uint8_t *)data;
    uint8_t checksum = 0;
    for (size_t i = 0; i < sizeof(WindData) - 1; i++) {
        checksum ^= ptr[i];
    }
    return checksum;
}

void setup() {
    Serial.begin(9600);    // USB Serial Monitor
    Serial1.begin(9600);   // RS485 on Serial1
    pinMode(rs485ControlPin, OUTPUT);
    digitalWrite(rs485ControlPin, RS485Receive);
    
    Serial.println("RS485 Wind Sensor & XBee Initialized");
}

void loop() {
    // Step 1: Request Wind Speed from RS485 Sensor
    digitalWrite(rs485ControlPin, RS485Transmit);  // Enable TX mode
    delay(10);  // Short delay for stability

    Serial1.write(windSpeedRequest, sizeof(windSpeedRequest));
    Serial1.flush();

    digitalWrite(rs485ControlPin, RS485Receive);  // Enable RX mode
    delay(100);  // Allow time for response

    // Step 2: Read and Process Wind Speed Data
    if (Serial1.available() >= 7) {
        Serial1.readBytes(response, 7);

        if (response[0] == 0x02 && response[1] == 0x03 && response[2] == 0x02) {
            int windSpeedRaw = (response[3] << 8) | response[4];
            float windSpeed = windSpeedRaw / 10.0;

            Serial.print("🌬️ Wind Speed: ");
            Serial.print(windSpeed);
            Serial.println(" m/s");

            // Step 3: Package Data in Struct
            WindData windData;
            windData.before_wrapper = 6;
            windData.wind_speed = windSpeed;
            windData.after_wrapper = 6;
            windData.checksum = computeChecksum(&windData);

            // Step 4: Send Wind Speed via XBee
            sendWindSpeedXBee(&windData);
        } else {
            Serial.println("Invalid response from sensor");
        }
    } else {
        Serial.println("No response from sensor");
    }

    delay(2000);  // Wait before next request
}

// Function to Send Packed Structure via XBee
void sendWindSpeedXBee(WindData *data) {
    uint8_t *payload = (uint8_t *)data;

    XBeeAddress64 broadcastAddress = XBeeAddress64(0x00000000, 0x0000FFFF);
    Tx64Request txRequest(broadcastAddress, payload, sizeof(WindData));
    xbee.send(txRequest);

    Serial.println("Wind Speed Sent via XBee (Struct Format)");
}
