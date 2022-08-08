#include <IRremote.h>

//#include <SPI.h>
//#include <Wire.h>
//#include <Adafruit_GFX.h>
//#include <Adafruit_SSD1306.h>
//
//#define SCREEN_WIDTH 128 // OLED display width, in pixels
//#define SCREEN_HEIGHT 32 // OLED display height, in pixels
//
//// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
//// The pins for I2C are defined by the Wire-library.
//// On an arduino NANO:       A4(SDA), A5(SCL)
//#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
//#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
////#define SCREEN_ADDRESS 0x78
//Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
//
//#define LOGO_HEIGHT   16
//#define LOGO_WIDTH    16
//
//#define TV_VOL_OFFSET 16
//#define MIN_LED_DELAY 500

IRsend irsend;

byte FLAGS = 0xF; //first 4 significant bits are tv volume (0-16 unless scaled)
byte mask_monitor = 0x10; //5th bit is for Monitor state
byte mask_monitor_mute = 0x20;  //6th bit is for Monitor Mute State
byte mask_LED = 0x40; //7th bit is for LED state
byte mask_LED_mode = 0x40;  //8th bit is for LED Mode (solid, or party)

//unsigned int study_monitor[68] = {9000, 4400, 650, 450, 650, 500, 600, 1650, 600, 500, 650, 500, 600, 500, 600, 500, 650, 500, 600, 1650, 600, 1600, 650, 500, 600, 1650, 600, 1600, 650, 1650, 600, 1600, 650, 1600, 600, 500, 650, 500, 600, 500, 650, 1600, 650, 450, 650, 500, 600, 500, 650, 500, 600, 1600, 650, 1600, 650, 1600, 650, 500, 600, 1650, 600, 1600, 650, 1600, 650, 1600, 600,};
//unsigned int study_tv_on[68] = {8900, 4450, 600, 500, 600, 500, 600, 1650, 550, 550, 550, 550, 550, 550, 600, 500, 600, 500, 600, 1650, 550, 1650, 550, 550, 600, 1600, 600, 1650, 550, 1650, 550, 1650, 600, 1600, 600, 550, 550, 550, 550, 550, 600, 1600, 600, 500, 600, 500, 600, 550, 550, 550, 550, 1650, 600, 1600, 600, 1650, 550, 550, 550, 1650, 600, 1600, 600, 1650, 550, 1650, 600,};
//unsigned int study_tv_vol_up[68] = {8900, 4450, 600, 500, 550, 550, 600, 1600, 600, 500, 600, 550, 600, 500, 600, 500, 550, 550, 600, 1600, 600, 1650, 600, 500, 550, 1650, 600, 1600, 600, 1650, 550, 1650, 600, 1600, 600, 500, 600, 1650, 600, 500, 600, 500, 550, 550, 600, 500, 600, 500, 600, 550, 550, 1650, 550, 550, 600, 1600, 600, 1600, 600, 1650, 600, 1600, 600, 1600, 600, 1650, 600,};
//unsigned int study_tv_vol_down[68] = {8900, 4450, 600, 500, 600, 500, 600, 1650, 550, 550, 550, 550, 550, 550, 600, 500, 600, 500, 600, 1650, 550, 1650, 550, 550, 600, 1600, 600, 1650, 550, 1650, 550, 1650, 600, 1600, 600, 1650, 550, 1650, 600, 500, 600, 500, 600, 500, 600, 550, 550, 550, 550, 550, 550, 550, 600, 500, 600, 1600, 600, 1650, 550, 1650, 600, 1600, 600, 1650, 550, 1650, 600,};
//unsigned int study_monitor_mute[68] = {8900, 4450, 600, 500, 550, 550, 600, 1600, 600, 500, 600, 550, 550, 550, 550, 550, 600, 500, 600, 1600, 600, 1650, 550, 550, 550, 1650, 600, 1600, 600, 1650, 550, 1650, 600, 1600, 600, 1600, 600, 550, 550, 550, 550, 1650, 600, 500, 600, 500, 600, 550, 550, 550, 550, 550, 550, 1650, 600, 1600, 600, 550, 550, 1650, 550, 1650, 600, 1600, 600, 1650, 550,};
//unsigned int study_light_on[68] = {8950, 4450, 600, 550, 500, 600, 650, 500, 550, 550, 500, 600, 650, 500, 500, 600, 500, 600, 650, 1600, 500, 1700, 550, 1650, 650, 1600, 550, 550, 650, 1600, 500, 1750, 600, 1600, 650, 500, 550, 600, 500, 1650, 600, 550, 550, 550, 650, 500, 550, 550, 550, 550, 650, 1600, 550, 1650, 600, 550, 550, 1650, 600, 1650, 600, 1600, 600, 1650, 600, 1600, 650,};
//unsigned int study_light_off[68] = {8950, 4450, 600, 550, 550, 550, 650, 500, 550, 550, 500, 600, 650, 500, 550, 550, 500, 600, 650, 1550, 550, 1700, 600, 1600, 650, 1600, 600, 500, 650, 1600, 600, 1600, 650, 1600, 650, 1600, 550, 550, 650, 1600, 550, 550, 650, 500, 550, 550, 550, 550, 650, 500, 550, 550, 550, 1650, 600, 550, 550, 1650, 600, 1600, 650, 1600, 600, 1650, 600, 1600, 650,};
//unsigned int study_light_cool[68] = {9050, 4400, 600, 500, 600, 500, 650, 500, 600, 500, 600, 500, 650, 500, 600, 550, 550, 500, 650, 1600, 600, 1650, 600, 1600, 650, 1600, 550, 550, 650, 1600, 550, 1650, 600, 1650, 650, 500, 550, 550, 550, 550, 650, 1600, 550, 550, 600, 550, 550, 550, 550, 550, 650, 1550, 550, 1700, 600, 1600, 650, 500, 550, 1650, 650, 1600, 550, 1650, 600, 1650, 650,};
//unsigned int study_light_soft[68] = {9000, 4400, 600, 550, 550, 550, 650, 500, 550, 600, 500, 550, 650, 500, 550, 550, 550, 550, 650, 1600, 550, 1650, 600, 1650, 650, 1600, 500, 600, 650, 1600, 500, 1700, 600, 1600, 650, 1600, 550, 550, 650, 500, 600, 1600, 650, 500, 600, 550, 500, 550, 650, 500, 550, 550, 550, 1700, 600, 1600, 650, 500, 550, 1650, 650, 1600, 550, 1650, 600, 1650, 650,};
//unsigned int study_light_warm[68] = {9000, 4400, 600, 550, 550, 550, 650, 500, 550, 550, 550, 550, 650, 500, 550, 550, 550, 550, 650, 1600, 550, 1650, 600, 1650, 650, 1550, 600, 550, 600, 1600, 600, 1650, 600, 1600, 650, 500, 600, 1600, 650, 500, 600, 1600, 650, 500, 600, 500, 600, 500, 650, 500, 600, 1600, 650, 500, 550, 1650, 650, 500, 550, 1650, 650, 1600, 550, 1650, 600, 1650, 650,};
//unsigned int study_light_RED[68] = {9000, 4400, 600, 550, 550, 550, 650, 450, 550, 600, 550, 550, 650, 450, 550, 600, 550, 550, 650, 1600, 550, 1650, 550, 1700, 600, 1600, 550, 550, 650, 1600, 650, 1600, 550, 1650, 650, 500, 500, 600, 550, 1700, 500, 1700, 650, 500, 500, 600, 550, 550, 650, 500, 500, 1700, 650, 1600, 600, 500, 650, 450, 550, 1700, 650, 1600, 500, 1700, 500, 1700, 650,};
//unsigned int study_light_GREEN[68] = {8950, 4500, 500, 600, 550, 550, 650, 500, 550, 550, 550, 550, 650, 500, 550, 550, 550, 550, 650, 1600, 550, 1700, 550, 1650, 650, 1600, 550, 550, 650, 1600, 550, 1650, 550, 1700, 650, 450, 550, 600, 550, 550, 650, 450, 550, 1700, 650, 450, 550, 600, 550, 550, 650, 1600, 550, 1650, 550, 1700, 650, 1600, 600, 500, 600, 1600, 550, 1700, 550, 1650, 650,};
//unsigned int study_light_BLUE[68] = {9050, 4400, 600, 500, 600, 500, 550, 600, 550, 550, 600, 500, 550, 600, 600, 500, 600, 500, 550, 1700, 600, 1600, 650, 1600, 550, 1700, 600, 500, 550, 1700, 550, 1650, 600, 1600, 550, 600, 600, 500, 600, 1650, 600, 500, 600, 1650, 600, 500, 600, 500, 550, 600, 600, 1600, 550, 1700, 600, 500, 550, 1700, 600, 500, 550, 1700, 550, 1650, 650, 1600, 500,};
//unsigned int study_light_flash[68] = {8950, 4450, 550, 600, 550, 550, 600, 500, 550, 600, 550, 550, 600, 500, 550, 600, 550, 550, 600, 1650, 500, 1700, 500, 1750, 600, 1600, 550, 550, 650, 1600, 600, 1650, 550, 1650, 600, 550, 500, 600, 550, 550, 600, 1650, 550, 1700, 500, 600, 550, 550, 600, 550, 500, 1700, 600, 1650, 500, 1700, 550, 600, 550, 550, 600, 1650, 500, 1700, 550, 1700, 600,};
//unsigned int study_light_strobe[68] = {8950, 4500, 500, 600, 500, 600, 650, 500, 500, 650, 450, 600, 650, 500, 500, 600, 500, 600, 650, 1600, 500, 1700, 550, 1700, 650, 1600, 500, 600, 650, 1600, 500, 1700, 550, 1650, 650, 1600, 550, 550, 650, 500, 550, 1650, 650, 1600, 500, 600, 650, 500, 500, 600, 500, 600, 650, 1600, 500, 1700, 550, 600, 500, 600, 650, 1600, 500, 1700, 550, 1700, 650,};
//unsigned int study_light_fade[68] = {8950, 4450, 550, 600, 550, 550, 550, 550, 550, 600, 550, 550, 650, 450, 550, 600, 550, 550, 650, 1600, 500, 1700, 550, 1700, 600, 1650, 600, 500, 600, 1600, 550, 1700, 550, 1650, 650, 500, 550, 1650, 650, 500, 550, 1650, 650, 1600, 550, 550, 650, 500, 500, 600, 550, 1700, 500, 600, 550, 1650, 550, 600, 550, 550, 650, 1600, 550, 1650, 550, 1700, 600,};
//unsigned int study_light_smooth[68] = {8900, 4500, 550, 600, 500, 600, 600, 500, 550, 600, 500, 600, 600, 500, 550, 600, 500, 600, 600, 1650, 500, 1700, 500, 1700, 600, 1650, 550, 550, 600, 1650, 550, 1700, 500, 1700, 600, 1650, 550, 1650, 550, 600, 550, 1650, 500, 1750, 600, 500, 550, 600, 500, 600, 600, 500, 550, 600, 500, 1700, 500, 600, 550, 550, 650, 1600, 550, 1700, 500, 1700, 600,};


//void LED_alert(int color, int alert_delay, int num_loops) {
//  /*
//     COLOR: 1-3 for 'RED' 'GREEN' or 'BLUE' respectively (WIP: ADD all colors available, possibly a color array, or mapping to numbers)
//     ALERT_DELAY: delay between flashing the color
//     NUM_LOOPS: amount of times color is flashed
//
//     given a string color, a pulse perion, and the amount of loops,
//     turn on the LED and flash the color given the delay,
//     for the number of loops defined
//  */
//  irsend.sendRaw(study_light_on, 68, 38);
//  delay(MIN_LED_DELAY);
//
//  if (color == 1) {
//    irsend.sendRaw(study_light_RED, 68, 38);
//  } else if (color == 2) {
//    irsend.sendRaw(study_light_GREEN, 68, 38);
//  } else if (color == 3) {
//    irsend.sendRaw(study_light_BLUE, 68, 38);
//  }
//  delay(MIN_LED_DELAY);
//
//  for (int i = 0; i < num_loops; i++) {
//    irsend.sendRaw(study_light_off, 68, 38);
//    delay(alert_delay);
//    irsend.sendRaw(study_light_on, 68, 38);
//    delay(alert_delay);
//  }
//  delay(alert_delay);
//
//  irsend.sendRaw(study_light_off, 68, 38);
//  delay(MIN_LED_DELAY);
//}

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

  //  Serial.begin(9600);
  //
  //  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  //  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
  //    Serial.println(F("SSD1306 allocation failed"));
  //    for (;;); // Don't proceed, loop forever
  //      if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
  //        Serial.println(F("SSD1306 allocation failed"));
  //      }
  //  }
  //
  //  // Show initial display buffer contents on the screen --
  //  // the library initializes this with an Adafruit splash screen.
  //  display.display();
  //  delay(2000); // Pause for 2 seconds
  //
  //  // Clear the buffer
  //  display.clearDisplay();
  //
  //  // Draw a single pixel in white
  //  display.drawPixel(10, 10, SSD1306_WHITE);
  //
  //  // Show the display buffer on the screen. You MUST call display() after
  //  // drawing commands to make them visible on screen!
  //  display.display();
  //  delay(2000);
}

void loop() {
  my_blink(100, 50);
  irsend.sendRaw(study_light_on, 68, 38);
  delay(5000);
  irsend.sendRaw(study_light_off, 68, 38);
  my_blink(100, 50);
}
