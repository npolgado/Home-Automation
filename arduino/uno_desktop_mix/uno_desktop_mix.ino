#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "DHT.h"

#define DHTPIN 2
#define DHTTYPE DHT11
#define TIMEOUT 5000                        // in milliseconds
#define MAX_PAYLOAD_SIZE 100
#define SENSOR_TIMEOUT 2000                 // 2 second timeout for sensor readings
#define SENSOR_AVERAGING_PERIOD 300000      // average sensor data every minute

DHT dht(DHTPIN, DHTTYPE);

long last_reading_time;
long last_averaging_time;
long poll_time;
long humidity_sum = 0;
long humidity_count = 0;
long temperature_sum = 0;
long temperature_count = 0;
long heat_index_sum = 0;
long heat_index_count = 0;

void setup()
{
    while (!Serial);
    Serial.begin(9600);
    Serial.println("Initializing Uno IoT");

    dht.begin();
    pinMode(LED_BUILTIN, OUTPUT);
    last_reading_time = millis();
    last_averaging_time = millis();
    
    Serial.println("Init Done!");
}

void loop()
{
//    Serial.print("poll_time: ");
//    Serial.print(poll_time);
//
//    Serial.print(" _ last_reading_time: ");
//    Serial.print(last_reading_time);
//
//    Serial.print(" _ last_averaging_time: ");
//    Serial.println(last_averaging_time);

    // SENDOUT SENSOR DATA COLLECTION
    poll_time = millis();
    if((poll_time - last_reading_time) > SENSOR_TIMEOUT){
        // READING DHT
        float h, t, f, hif, hic;
        h = dht.readHumidity();
        t = dht.readTemperature();
        f = dht.readTemperature(true);
        
        last_reading_time = millis();
        
        if (isnan(h) || isnan(t) || isnan(f))
        {
            Serial.println(F("Failed to read from DHT sensor!"));
        }
        else
        {
            hif = dht.computeHeatIndex(f, h);
            hic = dht.computeHeatIndex(t, h, false);
        }
        
        humidity_sum = humidity_sum + h;
        humidity_count++;
        
        temperature_sum = temperature_sum + f;
        temperature_count++;

        heat_index_sum = heat_index_sum + hif;
        heat_index_count++;
    }

    // SENDOUT SENSOR DATA TO FLASK
    if((poll_time - last_averaging_time) > SENSOR_AVERAGING_PERIOD){
        float humidity = (float) (humidity_sum / humidity_count);
        float temperature = (float) (temperature_sum / temperature_count);
        float heat_index = (float) (heat_index_sum / heat_index_count);
        
        last_averaging_time = millis();
        
        Serial.print(humidity);
        Serial.print("-");
        Serial.print(temperature);
        Serial.print("-");
        Serial.println(heat_index);
        
        humidity_sum, temperature_sum, heat_index_sum = 0;
        humidity_count, temperature_count, heat_index_count = 0;
    }
}
