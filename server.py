from flask import Flask, request, jsonify, Response
import datetime
import json
import os
from waitress import serve
from matplotlib import use as use_mat
use_mat('Agg')  # Change or remove this as necessary 
import matplotlib.pyplot as plt
from io import BytesIO
import argparse


app = Flask(__name__)

# Set the filename for storing CO events
events_filename = "co_events.json"

def load_events():
    if os.path.exists(events_filename):
        with open(events_filename, "r") as file:
            return json.load(file)
    else:
        return []

def save_events(events):
    with open(events_filename, "w") as file:
        json.dump(events, file)

# Initialize CO events from the file (if it exists)
co_events = load_events()

@app.route('/co', methods=['GET'])
def record_co():
    ppm = request.args.get('ppm')
    if ppm is None:
        return "Please provide the 'ppm' parameter in the request.", 400
    
    try:
        ppm = float(ppm)
    except ValueError:
        return "Invalid value for 'ppm'. Please provide a numeric value.", 400

    timestamp = datetime.datetime.now().isoformat()
    co_events.append({"ppm": ppm, "timestamp": timestamp})
    # Save the updated events to the file
    save_events(co_events)
    print("recorded", str(ppm), str(timestamp))
    return "CO event recorded successfully.", 200

@app.route('/costats', methods=['GET'])
def get_co_stats():
    return jsonify(co_events)

@app.route('/costats.png', methods=['GET'])
def plot_co_stats():
    timestamps = [datetime.datetime.fromisoformat(event['timestamp']) for event in co_events]
    ppm_values = [event['ppm'] for event in co_events]

    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, ppm_values, marker='o')
    plt.xlabel('Timestamp')
    plt.ylabel('CO Level (PPM)')
    plt.title('CO Events Over Time')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    # Save the plot to a BytesIO buffer as PNG
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    # Set the buffer position to the beginning and create a Flask response with the PNG image
    buffer.seek(0)
    return Response(buffer.getvalue(), content_type='image/png')

if __name__ == '__main__':
    # Parse command-line arguments for host and port
    parser = argparse.ArgumentParser(description='Run the CO Flask app.')
    parser.add_argument('--host', default='0.0.0.0', help='Host IP to run the server on.')
    parser.add_argument('--port', type=int, default=8080, help='Port number to run the server on.')
    args = parser.parse_args()

    # Use Waitress to serve the app with provided host and port
    serve(app, host=args.host, port=args.port)
