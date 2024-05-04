// Heart Rate Sensor Connection:
// Connect the sensor's Signal pin to A0 on Arduino
// Connect the sensor's VCC pin to 5V on Arduino
// Connect the sensor's GND pin to GND on Arduino

int sensorPin = A0; // Analog input pin for the heart rate sensor
int previousValue = 0; // Store the previous sensor value
unsigned long previousMillis = 0; // Store the previous time

void setup() {
  Serial.begin(9600); // Start serial communication at 9600 baud
}

void loop() {
  // Read the analog value from the heart rate sensor
  int sensorValue = analogRead(sensorPin);

  // Check if the sensor value has changed significantly
  if (abs(sensorValue - previousValue) > 10) { // Adjust this threshold as needed
    // Calculate heart rate (beats per minute)
    float heartRate = map(sensorValue, 200, 800, 50, 120); // Adjusted range for heart rate

    // Print heart rate to the serial monitor
    Serial.print("Heart Rate: ");
    Serial.println(heartRate);

    // Update the previous sensor value
    previousValue = sensorValue;
  }

  // Delay for a short time before taking the next reading (adjust as needed)
  delay(100); // Adjust this delay based on your application
}
