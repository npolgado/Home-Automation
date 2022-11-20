#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "DHT.h"
#include <IRremote.h>
#include <SoftwareSerial.h>

#define DHTPIN 2
#define DHTTYPE DHT11
#define TIMEOUT 5000 // mS
#define MAX_PAYLOAD_SIZE 100
#define SENSOR_TIMEOUT 10000    // 30 second timeout for sensor readings

SoftwareSerial mySerial(7, 6); // RX, TX
DHT dht(DHTPIN, DHTTYPE);
IRsend irsend; // automatically on D3 pin

unsigned int LED_IO = 0x40;
unsigned int LED_FADE = 0x7;
unsigned int LED_JUMP = 0x5;
unsigned int LED_BLUE = 0x59;
unsigned int LED_RED = 0x45;
unsigned int LED_GREEN = 0x58;
unsigned int LED_WHITE = 0x44;
unsigned int LED_BRIGHTEN = 0x5C;
unsigned int LED_DIM = 0x5D;

unsigned int LED_STATE = 0b00000111;
/*
0 (i/o state) 1 is HIGH
0 (fade bool) 1 is HIGH
0 (jump bool) 1 is HIGH
0 (enable Color bit 0)
0 (enable Color bit 1)
0 (BRIGHTNESS BIT 2)
0 (BRIGHTNESS BIT 1)
0 (BRIGHTNESS BIT 0)
*/

unsigned int IO_MASK = 0b10000000;
unsigned int FADE_MASK = 0b01000000;
unsigned int JUMP_MASK = 0b00100000;
unsigned int COLOR_MASK = 0b00011000;
unsigned int BRIGHTNESS_MASK = 0b00000111;

int LED_TIMEOUT = 250;
long last_reading_time;

void do_blink(int blink_speed, int blink_length)
{
    /*
       BLINK_SPEED: can be 'RED' 'GREEN' or 'BLUE' (WIP: ADD all colors available)
       BLINK_LENGTH: delay between flashing the color

       creates a pulse for a given perion and amount of loops
    */
    for (int i = 0; i < blink_length; i++)
    {
        digitalWrite(LED_BUILTIN, HIGH); // turn the LED on (HIGH is the voltage level)
        delay(blink_speed);              // wait for a second
        digitalWrite(LED_BUILTIN, LOW);  // turn the LED off by making the voltage LOW
        delay(blink_speed);              // wait for a second
    }
}

void printResponse()
{
    while (mySerial.available())
    {
        Serial.println(mySerial.readStringUntil('\n'));
    }
}

boolean echoFind(String keyword)
{
    byte current_char = 0;
    byte keyword_length = keyword.length();
    long deadline = millis() + TIMEOUT;
    while (millis() < deadline)
    {
        if (mySerial.available())
        {
            char ch = mySerial.read();
            if (ch == keyword[current_char])
            {
                if (++current_char == keyword_length)
                {
                    return true;
                }
            }else{
                Serial.print(ch);
            }
        }
    }
    Serial.println("SERIAL TIMED OUT");
    return false; // Timed out
}

boolean SerialCommand(String cmd, String ack)
{
    mySerial.println(cmd); // Send "AT+" command to module
    if (!echoFind(ack)){
      return true;       // ack blank or ack found
    }else{
      Serial.println("SERIAL TIMED OUT");
      return false;
    }
    return false;        
}

void update_flask_server(float h, float f, float hif){
    char dataCommand[256];
    char d_prefix[] = "GET /esp/";
    char dash[] = "-";
    char ending[] = " HTTP/1.1";
    char hs[100], fs[100], hifs[100];
    dtostrf(h, 4, 2, hs);
    dtostrf(f, 4, 2, fs);
    dtostrf(hif, 4, 2, hifs);
    sprintf(dataCommand, "%s%s%s%s%s%s%s", d_prefix, hs, dash, fs, dash, hifs, ending);
    Serial.println("WILL SEND ");
    Serial.println(dataCommand);

    Serial.println("OPENING CONNECTION WITH ");
    Serial.println("AT+CIPSTART=4,\"TCP\",\"192.168.1.78\",5000");
    SerialCommand("AT+CIPSTART=4,\"TCP\",\"192.168.1.78\",5000", "OK");

    int len = strlen(dataCommand);
    char lens[5];
    sprintf(lens, "%d", len);
    Serial.print("LEN ");
    Serial.println(lens);

    char sendCommand[20];
    char s_prefix[] = "AT+CIPSEND=4,";
    // char s_end[] = "\r";
    sprintf(sendCommand, "%s%s%s", s_prefix, lens); //, s_end);

    Serial.print("send Command ");
    Serial.println(sendCommand);
    SerialCommand(sendCommand, ">");

    mySerial.print(dataCommand);
    delay(100);
    SerialCommand("AT+CIPCLOSE=4", "OK");
}

void send_command(int command)
{
    IrSender.sendNEC(0x0102, command, true, 0);
    delay(LED_TIMEOUT);
}

void process_change(uint8_t val)
{
    int io = (val & IO_MASK) >> 7;
    int party = (val & JUMP_MASK) >> 5;
    int fade = (val & FADE_MASK) >> 6;
    int color = (val & COLOR_MASK) >> 3;
    int brightness = (val & BRIGHTNESS_MASK);

    // check if on / off matches
    if (io)
    {
        LED_ON();
    }
    else
    {
        LED_OFF();
        return;
    }

    // check for fade first
    if (fade)
    {
        FADE();
        return;
    }

    // check for jump
    if (party)
    {
        PARTY();
        return;
    }

    if (!fade && !party)
    {
        if (color == 1)
        {
            ALERT(LED_BLUE, 100, 3);
        }
        else if (color == 2)
        {
            ALERT(LED_RED, 100, 3);
        }
        else if (color == 3)
        {
            ALERT(LED_GREEN, 100, 3);
        }
        else if (color == 4)
        {
            ALERT(LED_WHITE, 100, 3);
        }

        LED_STATE |= COLOR_MASK;
        LED_STATE &= ~(JUMP_MASK | FADE_MASK);
    }
    SET_LED_BRIGHTNESS(brightness);
}

void LED_ON()
{
    if ((LED_STATE & IO_MASK) != 0) // returns non zero if mask and led state match on i/o bit
    {
        return;
    }
    else
    {
        send_command(LED_IO);
        LED_STATE |= IO_MASK;
    }
}

void LED_OFF()
{
    if ((LED_STATE & IO_MASK) != 0) // returns non zero if mask and led state match on i/o bit
    {
        send_command(LED_IO);
        LED_STATE &= ~IO_MASK;
    }
    return;
}

void PARTY()
{
    if ((LED_STATE & JUMP_MASK) == 0)
    {
        send_command(LED_JUMP); // led state jump function not on currently
        LED_STATE |= JUMP_MASK;
        LED_STATE &= ~FADE_MASK;
    }
    else
    {
        return;
    }
}

void FADE()
{
    if ((LED_STATE & FADE_MASK) == 0)
    {
        send_command(LED_FADE);
        LED_STATE |= FADE_MASK;
        LED_STATE &= ~JUMP_MASK;
    }
    else
    {
        return;
    }
}

void ALERT(unsigned int color, int freq, int seconds)
{
    // freq = i/o's per second
    // interval = ms per state
    int interval = (int)(1000 / (freq * 2));
    LED_ON();
    send_command(color);
    for (int i = 0; i < seconds; i++)
    {
        IrSender.sendNEC(0x0102, LED_IO, true, 0);
        delay(interval);
        IrSender.sendNEC(0x0102, LED_IO, true, 0);
        delay(interval);
    }
    delay(LED_TIMEOUT);
}

void SET_LED_BRIGHTNESS(unsigned int brightness)
{
    if (brightness > 7 || brightness < 0)
    {
        return;
    }

    if (brightness == 0)
    {
        LED_OFF();
    }
    else
    {
        LED_ON();
    }

    int curr_lvl = (LED_STATE & BRIGHTNESS_MASK);
    int diff = (curr_lvl - brightness);

    LED_STATE &= 0b11111000;
    LED_STATE |= brightness;

    // if diff is negative brightness was higher, repeat brightness cmd until correct level
    if (diff <= 0)
    {
        while (diff < 0)
        {
            send_command(LED_BRIGHTEN);
            diff++;
        }
    }

    // if diff is pos, curr lvl was higher, repeat dim cmd until correct level
    if (diff >= 0)
    {
        while (diff >= 0)
        {
            send_command(LED_DIM);
            diff--;
        }
    }
}

void setup()
{
    while (!Serial);
    Serial.begin(9600);
    Serial.println("Initializing Uno IoT");

    // while (!mySerial);
    // mySerial.begin(115200);
    // Serial.println("Initializing Communication");
    // Serial.print("...");
    
    // SerialCommand("AT+RST", "ready"); // RESTART
    // Serial.print("...");

    // SerialCommand("AT+CWMODE=3", "OK"); // CHMOD STA
    // Serial.print("...");

    // mySerial.print("AT+CWLAP"); // INIT STA
    // delay(3000);
    // Serial.print("...");

    // SerialCommand("AT+CIPMUX=1", "OK"); // ENABLE MULTIPLE CONNECTIONS
    // Serial.print("...");

    // SerialCommand("AT+CWJAP=\"mancave\",\"rudeFaMoxer50\"", "OK"); // CONNECT TO AP
    // Serial.print("...");

    // SerialCommand("AT+CIPSERVER=1,80", "OK"); // CREATE SERVER
    // Serial.println("...");

    dht.begin();
    pinMode(LED_BUILTIN, OUTPUT); // for blink
    IrSender.begin(3, ENABLE_LED_FEEDBACK);
    last_reading_time = millis();
}

void loop()
{
    // Serial.println(SerialCommand("AT", "OK"));
    // delay(2000);

    // Serial.println("LED_STATE");
    // Serial.println(LED_STATE, BIN);

    // // READING DHT
    // float h, t, f, hif, hic;
    // h = dht.readHumidity();
    // t = dht.readTemperature();
    // f = dht.readTemperature(true);
    // if (isnan(h) || isnan(t) || isnan(f))
    // {
    //     Serial.println(F("Failed to read from DHT sensor!"));
    // }
    // else
    // {
    //     hif = dht.computeHeatIndex(f, h);
    //     hic = dht.computeHeatIndex(t, h, false);
    // }

    // // SENDOUT SENSOR DATA TO FLASK
    // uint32_t poll_time = millis();
    // if((poll_time - last_reading_time) > SENSOR_TIMEOUT){
    //     update_flask_server(h, f, hif);
    //     last_reading_time = millis();
    // }

    // // Serial.println(data);
    // Serial.print(F(" "));
    // Serial.print(h);
    // Serial.print(F(" "));
    // Serial.print(t);
    // Serial.print(F(" "));
    // Serial.print(f);
    // Serial.print(F(" "));
    // Serial.print(hic);
    // Serial.print(F(" "));
    // Serial.print(hif);
    // Serial.println(F(" "));
    // delay(2000);
}
