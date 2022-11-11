#include "DHT.h"
#include <IRremote.h>
#include <SoftwareSerial.h>

#define DHTPIN 2  
#define DHTTYPE DHT11 
#define TIMEOUT 5000 // mS

SoftwareSerial mySerial(7, 6); // RX, TX
DHT dht(DHTPIN, DHTTYPE);
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

boolean echoFind(String keyword){
 byte current_char = 0;
 byte keyword_length = keyword.length();
 long deadline = millis() + TIMEOUT;
 while(millis() < deadline){
  if (mySerial.available()){
    char ch = mySerial.read();
    Serial.write(ch);
    if (ch == keyword[current_char])
      if (++current_char == keyword_length){
       Serial.println();
       return true;
    }
   }
  }
 return false; // Timed out
}

boolean SerialCommand(String cmd, String ack){
  mySerial.println(cmd); // Send "AT+" command to module
  if (!echoFind(ack)) // timed out waiting for ack string
    return true; // ack blank or ack found
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

    if(!fade && !party){
      if(color == 1){
        send_command(LED_BLUE);
      }else if(color == 2){
        send_command(LED_RED);
      }else if(color == 3){
        send_command(LED_GREEN);
      }else if(color == 4){
        send_command(LED_WHITE);
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

void setup() {
  while (!Serial);
  Serial.begin(9600);
  Serial.println("Initializing Uno IoT");
  
  mySerial.begin(115200);
  Serial.println("Initalizing Communication");
  Serial.print("...");
  
  SerialCommand("AT+RST", "Ready"); // RESTART
  Serial.print("...");
  
  SerialCommand("AT+CWMODE=1","OK"); // CHMOD STA
  mySerial.println("AT+CWMODE=1");
  delay(200);  
  Serial.print("...");
  
  mySerial.println("AT+CWLAP"); // INIT STA
  delay(200);
  Serial.print("...");

  mySerial.println("AT+CIPMUX=1"); // ENABLE MULTIPLE CONNECTIONS
  echoFind("OK");
  delay(200);
  Serial.print("...");

  SerialCommand("AT+CWJAP=\"WIFI_NETWORK\",\"WIFI_PASSWORD\"", "OK"); // CONNECT TO AP
  Serial.println("...");

  mySerial.println("AT+CIPSERVER=1,80");
  bool init_server = echoFind("OK");
  Serial.print("...");
  Serial.println(init_server);
  
  dht.begin();
  pinMode(LED_BUILTIN, OUTPUT); // for blink
  IrSender.begin(3, ENABLE_LED_FEEDBACK);
}

void loop() {
  Serial.println(LED_STATE, BIN);
  float h, t, f, hif, hic;
  delay(2000);

  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  h = dht.readHumidity();
  // as Celsius (the default)
  t = dht.readTemperature();
  // as Fahrenheit (isFahrenheit = true)
  f = dht.readTemperature(true);

  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }else{
    // Compute heat index
    hif = dht.computeHeatIndex(f, h);
    hic = dht.computeHeatIndex(t, h, false);
  }

  Serial.print(F("Humidity: "));
  Serial.print(h);
  Serial.print(F("%  Temperature: "));
  Serial.print(t);
  Serial.print(F("°C "));
  Serial.print(f);
  Serial.print(F("°F  Heat index: "));
  Serial.print(hic);
  Serial.print(F("°C "));
  Serial.print(hif);
  Serial.println(F("°F"));
}
