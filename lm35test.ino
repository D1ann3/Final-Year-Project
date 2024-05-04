const int lm35Pin = A0; // Define the analog input pin for the LM35 sensor

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
}

void loop() {
  // Read the analog voltage from the LM35 sensor
  int sensorValue = analogRead(lm35Pin);

  // Convert the sensor value to temperature in degrees Celsius
  float temperature = (sensorValue * 5.0 / 1024.0) * 100.0;

  // Print the temperature to the serial monitor
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");

  delay(1000); // Wait for a second before reading again
}
