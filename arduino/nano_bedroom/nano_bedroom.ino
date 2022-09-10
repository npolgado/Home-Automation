#include <IRremote.h>
#include <SPI.h>  // spi library for connecting nrf
#include <RF24.h> // nrf library

RF24 radio(9, 10); // ce, csn pins
IRsend irsend;

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

    SET_LED_BRIGHTNESS(brightness);

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

    // check for alert
    if (alert)
    {
        SET_LED_BRIGHTNESS(7);
        if (color == 0){
            ALERT(LED_BLUE, 60, 10);
        }
        else if (color == 1){
            ALERT(LED_RED, 60, 10);
        }
        else if (color == 2){
            ALERT(LED_GREEN, 60, 10);
        }
        else if (color == 3){
            ALERT(LED_WHITE, 60, 10);
        }

        LED_STATE &= ~COLOR_MASK;
        LED_STATE |= (color << 3);
    }
}

void LED_ON()
{
    if ((LED_STATE & IO_MASK) != 0) // returns non zero if mask and led state match on i/o bit
    {
        return:
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

void setup(void)
{
    pinMode(LED_BUILTIN, OUTPUT); // for blink
    IrSender.begin(3, ENABLE_LED_FEEDBACK);

    while (!Serial);
    Serial.begin(9600);
    Serial.println("Starting.. Setting Up.. Radio on..");
    radio.begin();
    radio.setPALevel(RF24_PA_MAX);
    radio.setDataRate(RF24_1MBPS);
    radio.setChannel(0x76);
    const uint64_t pipe = 0xE0E0F1F1E0;

    radio.openReadingPipe(1, pipe);
    radio.enableDynamicPayloads();
    radio.powerUp();
}

void loop(void)
{
    radio.startListening();
    char receivedMessage[32] = {0};
    while (True)
    {
        Serial.println(LED_STATE);
        if (radio.available())
        {
            radio.read(receivedMessage, sizeof(receivedMessage));
            Serial.println(receivedMessage);

            // if __ send this command
            uint8_t val = atoi(receivedMessage);
            Serial.println(val);
            if ((val - LED_STATE) == 0)
            {
                Serial.println("no state change");
                return;
            }
            else
            {
                Serial.println("looking at change");
                process_change(val);
            }

            receivedMessage = {0}; // clear recieved
        }
        delay(LED_TIMEOUT);
    }
}
