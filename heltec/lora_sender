/* Heltec LoRa Sender with DHT22
 *
 * Reads temperature and humidity from a DHT22 sensor,
 * shows them on the OLED, and sends them over LoRa.

 * Abigale Tucker
 */

#include "LoRaWan_APP.h"
#include "Arduino.h"
#include "HT_SSD1306Wire.h"
#include "DHT.h"

extern SSD1306Wire display;

#define DHTPIN   4
#define DHTTYPE  DHT22
DHT dht(DHTPIN, DHTTYPE);

#define RF_FREQUENCY               915000000
#define TX_OUTPUT_POWER            5
#define LORA_BANDWIDTH             0
#define LORA_SPREADING_FACTOR      7
#define LORA_CODINGRATE            1
#define LORA_PREAMBLE_LENGTH       8
#define LORA_SYMBOL_TIMEOUT        0
#define LORA_FIX_LENGTH_PAYLOAD_ON false
#define LORA_IQ_INVERSION_ON       false

#define BUFFER_SIZE 64

char txpacket[BUFFER_SIZE];
bool lora_idle = true;

static RadioEvents_t RadioEvents;

void OnTxDone(void);
void OnTxTimeout(void);

void VextON(void)
{
    pinMode(Vext, OUTPUT);
    digitalWrite(Vext, LOW);
}

void setup() {
    Serial.begin(115200);
    Mcu.begin(HELTEC_BOARD, SLOW_CLK_TPYE);

    VextON();
    delay(100);

    display.init();
    display.clear();
    display.setFont(ArialMT_Plain_10);
    display.setTextAlignment(TEXT_ALIGN_LEFT);
    display.drawString(0, 0, "Starting...");
    display.display();

    dht.begin();

    RadioEvents.TxDone = OnTxDone;
    RadioEvents.TxTimeout = OnTxTimeout;

    Radio.Init(&RadioEvents);
    Radio.SetChannel(RF_FREQUENCY);
    Radio.SetTxConfig(
        MODEM_LORA,
        TX_OUTPUT_POWER,
        0,
        LORA_BANDWIDTH,
        LORA_SPREADING_FACTOR,
        LORA_CODINGRATE,
        LORA_PREAMBLE_LENGTH,
        LORA_FIX_LENGTH_PAYLOAD_ON,
        true,
        0,
        0,
        LORA_IQ_INVERSION_ON,
        3000
    );

    Serial.println("Sender ready.");
}

void loop() {
    if (lora_idle) {
        // delay(2000);
        delay(1800000); // 30 minutes = 30 * 60 * 1000 ms

        float tempF = dht.readTemperature(true);
        float humidity = dht.readHumidity();

        if (isnan(tempF) || isnan(humidity)) {
            Serial.println("Failed to read from DHT22!");

            display.clear();
            display.drawString(0, 0, "Sensor Error");
            display.drawString(0, 12, "Check wiring");
            display.display();
            return;
        }

        // snprintf(txpacket, BUFFER_SIZE, "T:%.1fF H:%.1f%%", tempF, humidity);
        snprintf(txpacket, BUFFER_SIZE, "GH0,%.1f,%.1f", tempF, humidity);

        Serial.print("Sending: ");
        Serial.println(txpacket);

        display.clear();
        display.setFont(ArialMT_Plain_10);
        display.setTextAlignment(TEXT_ALIGN_LEFT);
        display.drawString(0, 0, "GH0 Sending:");
        display.drawString(0, 12, "Temp: " + String(tempF, 1) + " F");
        display.drawString(0, 24, "Hum:  " + String(humidity, 1) + " %");
        display.display();

        Radio.Send((uint8_t *)txpacket, strlen(txpacket));
        lora_idle = false;
    }

    Radio.IrqProcess();
}

void OnTxDone(void) {
    Serial.println("TX done.");
    lora_idle = true;
}

void OnTxTimeout(void) {
    Radio.Sleep();
    Serial.println("TX timeout.");
    lora_idle = true;
}
