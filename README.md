# Gas Leakage Monitoring System with Raspberry Pi Pico W (picoCOmonitor)

**CO (pun intended) author: ChatGPT** 
![Screenshot from a few hours of usage](https://cdn.discordapp.com/attachments/620053809720328193/1133854334778609816/image.png)

The Gas Leakage Monitoring System (picoCOmonitor) is a project that utilizes a Raspberry Pi Pico W and an MQ7 gas sensor to monitor carbon monoxide (CO) levels. The system sends the measured gas concentration data to a server for visualization and analysis. This repository contains code for both the gas leakage monitoring system (on the Pico W) and the server to process and display the data.
## Hardware Setup 
1. Connect the MQ7 Gas Sensor to the Raspberry Pi Pico W as follows:
- MQ7 VCC: Connect to Pico W 3V3 (3.3V).
- MQ7 GND: Connect to Pico W GND (Ground).
- MQ7 AO (Analog Output): Connect to ADC input pin (ADC_PIN = 2 (GPIO pin 28) in the Pico W code).
- MQ7 DO (Digital Output): Connect to DIN input pin (DIN_PIN = 16 in the Pico W code). 
2. Ensure that the Raspberry Pi Pico W is properly connected to your computer or power source via USB.
## Software Setup
### Raspberry Pi Pico W (picoCOmonitor) 
1. Make sure you have the latest version of MicroPython installed on your Raspberry Pi Pico W. 
2. Copy and paste the provided code for the picoCOmonitor into a new Python script on your computer. 
3. Create a new text file named `config.json` in the same directory as the Python script. 
4. Open the `config.json` file and fill in the necessary configuration parameters as explained in the "config.json Guide" section below. 
5. Save the `config.json` file with the appropriate values.
### picoCOmonitor Server 
1. Install Python and then Flask abd waitress on your server machine:
```
pip install Flask waitress
``` 
2. Copy and paste the provided server code into a new Python script on your server. 
3. Save the Python script with an appropriate filename (e.g., `server.py`). 
4. Run the server by executing the Python script:
5. (optional) create a systemd (or other init system) service for it to run 24/7 
```
python server.py
```
By default, the server will run on `http://0.0.0.0:8080`. If you want to specify a different host and port, you can use the optional command-line arguments as shown in the server code.
## Configuration (config.json) Guide

The `config.json` file contains settings for configuring the Gas Leakage Monitoring System on the Raspberry Pi Pico W. Before running the main script, ensure that you correctly configure the `config.json` file with the appropriate values. Below is a detailed explanation of each configuration parameter: 
- `wifi_ssid`: The SSID (Service Set Identifier) of the Wi-Fi network to which the Pico W should connect.

**Description** : The SSID (Service Set Identifier) of the Wi-Fi network to which the device should connect.

**Data Type** : String

**Example** : `"wifi_ssid": "My_WiFi_Network"`

This parameter specifies the Wi-Fi network name (SSID) to which the Gas Leakage Monitoring System should connect. Replace the example `"My_WiFi_Network"` with the actual SSID of your Wi-Fi network. 
- `wifi_pass`: The password for the Wi-Fi network specified by the `wifi_ssid` parameter.

**Description** : The password for the Wi-Fi network specified by the `wifi_ssid` parameter.

**Data Type** : String

**Example** : `"wifi_pass": "MyWiFiPassword123"`

This parameter specifies the password required to connect to the Wi-Fi network with the SSID specified in `wifi_ssid`. Replace the example `"MyWiFiPassword123"` with the actual password of your Wi-Fi network. 
- `server_ip`: The IP address of the server to which the Gas Leakage Monitoring System should send gas concentration data.

**Description** : The IP address of the server to which the Gas Leakage Monitoring System should send gas concentration data.

**Data Type** : String

**Example** : `"server_ip": "192.168.1.100"`

This parameter determines the IP address of the server where you want to receive the gas concentration data. Replace the example `"192.168.1.100"` with the actual IP address of your server. 
- `server_port`: The port number on the server to which the Gas Leakage Monitoring System should send gas concentration data.

**Description** : The port number on the server to which the Gas Leakage Monitoring System should send gas concentration data.

**Data Type** : String

**Example** : `"server_port": "8080"`

This parameter specifies the port number on the server where the system should send gas concentration data. Replace the example `"8080"` with the appropriate port number on your server. 
- `discord_webhook_url`: The Discord Webhook URL that allows the system to send a notification to a Discord channel when gas leakage is detected.

**Description** : The Discord Webhook URL that allows the system to send a notification to a Discord channel when gas leakage is detected.

**Data Type** : String

**Example** : `"discord_webhook_url": "https://discord.com/api/webhooks/1234567890/abcd1234"`

This parameter specifies the Discord Webhook URL to which the system will send notifications when gas leakage is detected. Replace the example `"https://discord.com/api/webhooks/1234567890/abcd1234"` with the actual Discord Webhook URL. 
- `update_pace_seconds`: The time interval (in seconds) between each gas concentration update.

**Description** : The time interval (in seconds) between each gas concentration update.

**Data Type** : Integer or Floating-Point Number

**Example** : `"update_pace_seconds": 1`

This parameter sets the time interval between consecutive updates of gas concentration data. Replace the example `1` with the desired time interval in seconds. For instance, if you set `"update_pace_seconds": 5`, the system will send gas concentration data to the server every 5 seconds.

**Note** : Ensure the validity and correctness of the values in the `config.json` file. Avoid sharing this file with unauthorized individuals, as it may contain sensitive information such as Wi-Fi credentials and Discord Webhook URL.
## Running the Monitoring System 
1. Upload the Python script and `config.json` file to the Raspberry Pi Pico W. 
2. Disconnect the Raspberry Pi Pico W from your computer (if connected via USB). 
3. Power the Raspberry Pi Pico W independently using a USB power source or a battery. 
4. The system will automatically start monitoring gas concentration based on the provided configuration. 
5. If gas leakage is detected, the system will send a notification to the provided Discord Webhook URL. 
6. The gas concentration data will also be sent to the specified server at regular intervals, where you can process and visualize the data as desired.
## API Endpoints (picoCOmonitor Server)

The picoCOmonitor server provides the following API endpoints: 
- `/co` (GET): Allows the Raspberry Pi Pico W to record CO events by sending gas concentration data to the server. 
- `/costats` (GET): Retrieves the recorded CO statistics in JSON format. 
- `/costats.png` (GET): Plots the CO events over time and returns the plot as a PNG image.

For more details on how to use the API endpoints, refer to the "API Endpoints" section in the server code.
## Monitoring and Analysis 
- Monitor the gas concentration data received by the server by visiting the appropriate endpoints (e.g., `/costats`) in your web browser. The data will be displayed in JSON format. 
- For visual analysis, access the `/costats.png` endpoint in your web browser. The plotted graph will show the gas concentration values over time. 
- Download the JSON file containing the CO events from the server for further analysis. The events are stored in the `co_events.json` file.
## Safety Precautions 
- Handle the MQ7 gas sensor with care, and avoid exposure to gases that could be harmful. 
- Place the gas sensor in a suitable location to detect gas leaks effectively. 
- Be cautious when dealing with potential gas leakage scenarios, and follow appropriate safety guidelines.
## Customization 
- You can customize the monitoring intervals, WiFi authentication details, and other paramters in the `config.json` file to suit your specific requirements. 
- For advanced customization and additional functionality, you can extend the Flask application by adding more endpoints or integrating other data analysis libraries.---

Feel free to add any additional information or instructions related to the Gas Leakage Monitoring System in this README file.
