import BlynkLib
from BlynkTimer import BlynkTimer
import serial
import RPi.GPIO as GPIO
import time
import joblib  # For model persistence
import threading  # For asynchronous SMS sending

BLYNK_AUTH_TOKEN = 't3saat0dD0heraKSj4YAARFkwdDwr-Tu'  # Blynk authentication token

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN)
timer = BlynkTimer()

ser = serial.Serial("/dev/ttyACM0", 9600)

# Load your decision tree model
model = joblib.load('trained_decision_tree_model.pkl')  # Replace 'trained_decision_tree_model.pkl' with your actual model file

# Replace 'serial_port', 'phone_number', 'message', and 'pin' with your specific values
#serial_port = '/dev/serial0'  # Adjust the serial port based on your Raspberry Pi configuration
phone_number = '+254701871697'  # Replace with the recipient's phone number
pin = '6594'  # Replace with the actual PIN of your SIM card

# Function to send SMS asynchronously
def send_sms_async(phone_number, message, pin=None):
    try:
        # Initialize the serial connection
        ser_sms = serial.Serial('/dev/serial0', 9600, timeout=1)
        time.sleep(2)  # Allow time for the serial connection to initialize

        # Unlock SIM card if a PIN is provided
        if pin:
            ser_sms.write('AT+CPIN="{}"\r\n'.format(pin).encode('utf-8'))
            time.sleep(1)

        # Set the recipient phone number
        ser_sms.write('AT+CMGS="{}"\r\n'.format(phone_number).encode('utf-8'))
        time.sleep(1)

        # Enter the message content
        ser_sms.write('{}\r\n'.format(message).encode('utf-8'))
        time.sleep(1)

        # Send the SMS
        ser_sms.write(bytes([26]))  # ASCII code for Ctrl+Z
        time.sleep(2)

        # Print GSM module response
        response = ser_sms.read_all().decode('utf-8')
        print("GSM Module Response:", response)

        # Close the serial connection
        ser_sms.close()

        print("SMS sent successfully!")

    except Exception as e:
        print("Error:", str(e))

def read_and_send_serial_data():
    read_ser = ser.readline().decode().strip()  # Decode byte string to string and remove newline characters
    print(read_ser)

    # Send the raw data to Blynk virtual pin
    blynk.virtual_write(0, read_ser)

    # Check if the data starts with 'Temperature:'
    if read_ser.startswith('Temperature:'):
        # Extract the temperature value
        temperature_str = read_ser.split(':')[1].split(' ')[1]
        temperature = float(temperature_str)

        # Send temperature data to Blynk virtual pin
        blynk.virtual_write(1, temperature)

    # Check if the data starts with 'Heart Rate:'
    elif read_ser.startswith('Heart Rate:'):
        # Extract the heart rate value
        heart_rate_str = read_ser.split(':')[1].strip()
        heart_rate = float(heart_rate_str)

        # Perform prediction using the decision tree model only for heart rate data
        if 'Heart Rate' in read_ser:
            prediction = model.predict([[heart_rate]])
            # Send heart rate data to Blynk virtual pin
            blynk.virtual_write(0, heart_rate)

            # Check if the prediction is "2" and send SMS alert
            if prediction[0] == 2:
                message = f"Alert: Model predicts 'Distress'. Heart rate is high"
                print("Sending SMS...")
                threading.Thread(target=send_sms_async, args=(phone_number, message, pin)).start()

        else:
            prediction = None

        # Send the prediction to Blynk virtual pin
        blynk.virtual_write(4, prediction[0] if prediction is not None else None)  # Assuming virtual pin 4 for displaying the prediction

# Set up a timer to read and send data every 5 seconds
timer_id = timer.set_interval(5, read_and_send_serial_data)

@blynk.on("connected")
def blynk_connected():
    print("Raspberry Pi Connected to Blynk")

# Enable the timer
timer.enable(timer_id)

try:
    while True:
        blynk.run()
        timer.run()
        time.sleep(0.1)  # Small delay to avoid excessive CPU usage

except KeyboardInterrupt:
    print("Data collection stopped.")