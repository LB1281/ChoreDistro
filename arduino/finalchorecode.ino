#include <DHT.h>
#include <Servo.h>

#define DHTPIN 2         
#define DHTTYPE DHT11    
#define SERVO_PIN 9
#define PIR_PIN 3        // Pin for the PIR sensor
#define LED_PIN 13       // Pin for the LED

DHT dht(DHTPIN, DHTTYPE);
Servo fanServo;

void setup() {
  Serial.begin(9600);
  
  // Initialize DHT and Servo
  dht.begin();
  fanServo.attach(SERVO_PIN);
  fanServo.write(90); 

  // Initialize PIR and LED pins
  pinMode(PIR_PIN, INPUT);   // PIR is an input
  pinMode(LED_PIN, OUTPUT);  // LED is an output
}

void loop() {
  // --- Motion Detection Logic ---
  int motionDetected = digitalRead(PIR_PIN);

  if (motionDetected == HIGH) {
    digitalWrite(LED_PIN, HIGH); // Turn LED ON
    Serial.println("Motion Detected! LED ON");
  } else {
    digitalWrite(LED_PIN, LOW);  // Turn LED OFF
    Serial.println("No motion.");
  }

  // --- Temperature Logic ---
  float temperature = dht.readTemperature();

  if (isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    Serial.print("Current Temp: ");
    Serial.print(temperature);
    Serial.println("C");

    if (temperature > 27) {
      fanServo.write(180); 
      Serial.println("Fan ON");
    } else {
      fanServo.write(90);  
      Serial.println("Fan OFF");
    }
  }

  // Note: PIR sensors are very fast, but DHT sensors need time.
  // This delay affects both. For better responsiveness, 
  // you might consider using millis() in the future!
  delay(1000); 
}