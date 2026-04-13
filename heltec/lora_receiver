/* Heltec LoRa Receiver
 *
 * Receives LoRa packets and shows them on Serial and OLED.

 * Abigale Tucker
 */

#include "LoRaWan_APP.h"
#include "Arduino.h"
#include "HT_SSD1306Wire.h"

extern SSD1306Wire display;

#define RF_FREQUENCY                                915000000 // Hz

#define TX_OUTPUT_POWER                             14

#define LORA_BANDWIDTH                              0
#define LORA_SPREADING_FACTOR                       7
#define LORA_CODINGRATE                             1
#define LORA_PREAMBLE_LENGTH                        8
#define LORA_SYMBOL_TIMEOUT                         0
#define LORA_FIX_LENGTH_PAYLOAD_ON                  false
#define LORA_IQ_INVERSION_ON                        false

#define RX_TIMEOUT_VALUE                            1000
#define BUFFER_SIZE                                 64

char rxpacket[BUFFER_SIZE];

static RadioEvents_t RadioEvents;

int16_t packetRssi, rxSize;
bool lora_idle = true;

// Forward declaration
void OnRxDone(uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr);

// Turn on OLED power rail
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
    display.drawString(0, 0, "Receiver Ready");
    display.drawString(0, 12, "Waiting for GH0...");
    display.display();

    packetRssi = 0;
    rxSize = 0;

    RadioEvents.RxDone = OnRxDone;
    Radio.Init(&RadioEvents);
    Radio.SetChannel(RF_FREQUENCY);
    Radio.SetRxConfig(
        MODEM_LORA,
        LORA_BANDWIDTH,
        LORA_SPREADING_FACTOR,
        LORA_CODINGRATE,
        0,
        LORA_PREAMBLE_LENGTH,
        LORA_SYMBOL_TIMEOUT,
        LORA_FIX_LENGTH_PAYLOAD_ON,
        0,
        true,
        0,
        0,
        LORA_IQ_INVERSION_ON,
        true
    );

    Serial.println("Receiver ready.");
}

void loop()
{
    if (lora_idle)
    {
        lora_idle = false;
        Serial.println("Entering RX mode...");
        Radio.Rx(0);
    }

    Radio.IrqProcess();
}

void OnRxDone(uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr)
{
    packetRssi = rssi;
    rxSize = size;

    memcpy(rxpacket, payload, size);
    rxpacket[size] = '\0';

    display.clear();
    display.setFont(ArialMT_Plain_10);
    display.setTextAlignment(TEXT_ALIGN_LEFT);
    display.drawString(0, 0, "I hear you, GH0:");
    display.drawString(0, 12, String(rxpacket));
    display.display();

    Radio.Sleep();
    Serial.printf("\r\nReceiving from GH0: %s | RSSI: %d | Length: %d\r\n", rxpacket, packetRssi, rxSize);

    lora_idle = true;
}
