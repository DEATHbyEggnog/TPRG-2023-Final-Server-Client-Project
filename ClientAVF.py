#Ashley Ferguson 100615979
#Client Portion of Final Project for TPRG 2131
#December 6, 2023
import socket
import json
import time

s = socket.socket()
host = '10.102.13.55'
port = 5000
s.connect((host, port))

# Send data 50 times with a delay of 2 seconds
for _ in range(50):
    data_dict = {
        "Temperature": "some_value",  # Replace with actual data
        "DisplayPower": "some_value",
        "MeasureClock": "some_value",
        "MeasureVolts": "some_value",
        "DiskUsage": "some_value",  # Replace with actual data

    }

    # Convert the dictionary to a JSON-formatted string
    json_string = json.dumps(data_dict)

    # Send the JSON string as bytes
    s.send(json_string.encode('utf-8'))

    # Wait for 2 seconds before sending the next update
    time.sleep(2)

# Close the connection
s.close()
