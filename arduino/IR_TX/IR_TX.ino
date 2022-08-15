#include <IRremote.h>

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
0 (i/o state) 
0 (fade bool) 
0 (jump bool) 
0 (X) 0 (X) 
0 (BRIGHTNESS BIT 2) 
0 (BRIGHTNESS BIT 1) 
0 (BRIGHTNESS BIT 0)
*/

unsigned int IO_MASK = 0b10000000;
unsigned int FADE_MASK = 0b01000000;
unsigned int JUMP_MASK = 0b00100000;
unsigned int BRIGHTNESS_MASK = 0b00000111;

void LED_ON(){
  if (LED_STATE & IO_MASK){
    IrSender.sendNEC(0x0102, LED_IO, true, 0);
  }
}

void LED_OFF(){
  if (LED_STATE & IO_MASK){
    return;
  }else{
    IrSender.sendNEC(0x0102, LED_IO, true, 0);
  }
}

void SET_LED_BRIGHTNESS(int brightness){
  if(brightness > 7 || brightness < 0){
    return;
  }

  if(brightness == 0){
    LED_OFF();
  }else{
    LED_ON();
  }
  
  int curr_lvl = (LED_STATE & BRIGHTNESS_MASK);
  int diff = (curr_lvl - brightness);

  //if diff is negative brightness was higher, repeat brightness cmd until correct level
  if(diff <= 0){
    while(diff <= 0){
      IrSender.sendNEC(0x0102, LED_IO, true, 0);
      delay(500);
      diff++;
    }
  }
    
  //if diff is pos, curr lvl was higher, repeat dim cmd until correct level
  if(diff >= 0){
    while(diff >= 0){
      IrSender.sendNEC(0x0102, LED_IO, true, 0);
      delay(500);
      diff--;
    }
  }
}

void ALERT(unsigned int color, int freq, int seconds){
  //freq = i/o's per second
  //interval = ms per state
  int interval = (int) (1000 / (freq*2));
  IrSender.sendNEC(0x0102, color, true, 0);
  for(int i=0; i<seconds; i++){
    LED_OFF();
    delay(interval);
    LED_ON();
  }
}

void my_blink(int blink_speed, int blink_length) {
  /*
     BLINK_SPEED: can be 'RED' 'GREEN' or 'BLUE' (WIP: ADD all colors available)
     BLINK_LENGTH: delay between flashing the color

     creates a pulse for a given perion and amount of loops
  */
  for (int i = 0; i < blink_length; i++) {
    digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
    delay(blink_speed);                       // wait for a second
    digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
    delay(blink_speed);                       // wait for a second
  }
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT); //for blink
  IrSender.begin(3, ENABLE_LED_FEEDBACK);
}

void loop() {
  my_blink(100, 10);
  delay(1000);
  LED_ON();
  delay(1000);
  SET_LED_BRIGHTNESS(4);
  delay(1000);
  LED_OFF();
}
