from machine import Pin, ADC
import utime
import network
import time
from urequests import get
from json import loads

config_file = open('config.json', 'r')
config = loads(config_file.read())
config_file.close()

# Constants
ADC_PIN = 2
V_IN = 5.0
CALIBRATION_SECONDS = 15
COEF_A0 = 100.0
COEF_A1 = -1.513
LOAD_RES = 10000.0
CALIBRATION_CONSTANT = 5.0
DIN_PIN = 16
DIN = Pin(DIN_PIN, Pin.IN)


# Function to connect to WiFi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    timeout = 10  # Timeout in seconds
    start_time = time.time()

    while not wlan.isconnected():
        if time.time() - start_time > timeout:
            # If the connection timed out, reset the board
            machine.reset()

    print("Connected to WiFi:", ssid)
    print("IP address:", wlan.ifconfig()[0])

def read_rs(voltage):
    return (V_IN - voltage) / voltage

def read_ppm(Rs, R0):
    return COEF_A0 * (Rs / R0) ** COEF_A1

def convert_voltage(voltage):
    # ATD conversion
    return float(voltage) * (V_IN / 65535)

def calibrate_gas_sensor():
    # Perform calibration to get the R0 value
    Rs_sum = 0.0
    for i in range(CALIBRATION_SECONDS):
        voltage = ADC_ConvertedValue.read_u16()
        Rs_sum += read_rs(convert_voltage(voltage))
        utime.sleep(1)

    R0 = Rs_sum / CALIBRATION_SECONDS / CALIBRATION_CONSTANT
    return R0

def send_discord_webhook(ppm):
    webhook_url = config['discord_webhook_url']
    message = "Gas leak detected! PPM: {:.2f}".format(ppm)
    payload = {"content": message}
    headers = {"Content-Type": "application/json"}

    try:
        response = urequests.post(webhook_url, json=payload, headers=headers)
        print("Webhook response:", response.text)
    except Exception as e:
        print("Error sending webhook:", e)


# Connect to WiFi
connect_to_wifi(config['wifi_ssid'], config['wifi_pass'])

# Initialize ADC on GPIO2 (ADC_PIN)
ADC_ConvertedValue = ADC(ADC_PIN)

# Call the calibration function to get the R0 value

print('calibrating sensor...')
R0 = calibrate_gas_sensor()
print('Calibrated', str(R0))


def main():
    # Connect to WiFi
    connect_to_wifi(config['wifi_ssid'], config['wifi_pass'])

    # Initialize ADC on GPIO2 (ADC_PIN)
    ADC_ConvertedValue = ADC(ADC_PIN)

    print('Calibrating sensor...')
    R0 = calibrate_gas_sensor()
    print('Calibrated R0:', str(R0))

    while True:
        # Read the voltage from the gas sensor and calculate Rs
        voltage = ADC_ConvertedValue.read_u16()
        Rs = read_rs(convert_voltage(voltage))

        # Calculate PPM using the read_ppm function
        ppm = read_ppm(Rs, R0)
        print("Gas concentration: {:.2f} PPM".format(ppm))

        if DIN.value() == 1:
            print("No Gas leakage!")
        else:
            print("Gas leakage!")
            send_discord_webhook(ppm)
        try:
            r = get('http://{}:{}/co?ppm={}'.format(config['server_ip'], config['server_port'], str(ppm)))
            print('request response:', r.content.decode())
            time.sleep(config['update_pace_seconds'])
        except Exception as e:
            print(str(e))
        # Add a delay for stability and to avoid spamming the output

if __name__ == "__main__":
    main()

