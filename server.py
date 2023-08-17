import os
import json
import argparse
import datetime
import sqlite3
from io import BytesIO
from time import strftime
from flask import Flask, request, jsonify, Response, render_template
from waitress import serve
import matplotlib.pyplot as plt
from matplotlib import use as use_mat
use_mat("Agg")


app = Flask(__name__)

# Set the filename for storing CO events
db_filename = "co_events.db"
OFFSET = 3
# sets the offset in hours from UTC

def load_events():
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM co_events')
    events = [{"ppm": ppm, "timestamp": timestamp} for _, ppm, timestamp in cursor.fetchall()]
    conn.close()
    return events

def save_events(events):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM co_events')  # Clear existing data
    for event in events:
        cursor.execute('INSERT INTO co_events (ppm, timestamp) VALUES (?, ?)', (event["ppm"], event["timestamp"]))
    conn.commit()
    conn.close()

def load_events_interval(interval_minutes=1):
    min_time_difference = datetime.timedelta(minutes=int(interval_minutes))

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM co_events')
    events = [{"ppm": ppm, "timestamp": timestamp} for _, ppm, timestamp in cursor.fetchall()]
    conn.close()

    filtered_events = [events[0]]  # Start with the first event
    for i in range(1, len(events)):
        current_event = events[i]
        previous_event = events[i - 1]

        current_time = datetime.datetime.fromisoformat(current_event["timestamp"])
        previous_time = datetime.datetime.fromisoformat(previous_event["timestamp"])

        time_difference = current_time - previous_time
        if time_difference >= min_time_difference:
            filtered_events.append(current_event)

    for event in filtered_events:
        event["formatted_timestamp"] = datetime.datetime.fromisoformat(event["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')

    return filtered_events


@app.route('/co', methods=['GET'])
def record_co():
    ppm = request.args.get('ppm')
    if ppm is None:
        return "Please provide the 'ppm' parameter in the request.", 400

    try:
        ppm = float(ppm)
    except ValueError:
        return "Invalid value for 'ppm'. Please provide a numeric value.", 400

    current_time = datetime.datetime.now()
    adjusted_time = current_time + datetime.timedelta(hours=OFFSET)
    timestamp = adjusted_time.isoformat()
    co_events = load_events()
    co_events.append({"ppm": ppm, "timestamp": timestamp})
    # Save the updated events to the file
    save_events(co_events)
    print("recorded", str(ppm), str(timestamp))
    return "CO event recorded successfully.", 200


@app.route('/costats.png', methods=['GET'])
def plot_co_stats():
    co_events = load_events()
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

@app.route('/', methods=['GET'])
def home():
    interval = request.args.get('i')
    if not interval:
        interval = 1
    return render_template('home.html', events=load_events_interval(interval))

def initialize_database():
    conn = sqlite3.connect(db_filename)
    with conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS co_events (
                id INTEGER PRIMARY KEY,
                ppm REAL,
                timestamp TEXT
            )
        ''')


@app.route('/generate_graph', methods=['GET'])
def generate_graph():
    start_timestamp = request.args.get('start_timestamp')
    end_timestamp = request.args.get('end_timestamp')
    if not start_timestamp or not end_timestamp:
        return "Please select both start and end timestamps.", 400
    start_time = datetime.datetime.fromisoformat(start_timestamp.replace('T', ' '))
    end_time = datetime.datetime.fromisoformat(end_timestamp.replace('T', ' '))

    filtered_events = [event for event in load_events() if start_time <= datetime.datetime.fromisoformat(event['timestamp']) <= end_time]

    timestamps = [datetime.datetime.fromisoformat(event['timestamp']) for event in filtered_events]
    ppm_values = [event['ppm'] for event in filtered_events]

    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, ppm_values, marker='o')
    plt.xlabel('Timestamp')
    plt.ylabel('CO Level (PPM)')
    plt.title('CO Events Over Time')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    return Response(buffer.getvalue(), content_type='image/png')

if __name__ == '__main__':
    # Parse command-line arguments for host and port
    parser = argparse.ArgumentParser(description='Run the CO Flask app.')
    parser.add_argument('--host', default='0.0.0.0', help='Host IP to run the server on.')
    parser.add_argument('--port', type=int, default=8888, help='Port number to run the server on.')
    initialize_database()
    args = parser.parse_args()
    # Use Waitress to serve the app with provided host and port
    serve(app, host=args.host, port=args.port)
