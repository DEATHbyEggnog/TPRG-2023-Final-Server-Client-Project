#Ashley Ferguson 100615979
#Server Portion of Final Project for TPRG 2131
#December 6, 2023
#GUI added to server
import socket
import json
import tkinter as tk
from tkinter import Label
import os
import time
from math import sin, cos, radians

class ServerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Server GUI")
        self.geometry("600x500")
        
        # Create labels to display data
        self.temperature_label = Label(self, text="Core Temperature:")
        self.display_power_label = Label(self, text="Display Power:")
        self.clock_frequency_label = Label(self, text="Clock Frequency:")
        self.dram_voltage_label = Label(self, text="DRAM Voltage:")
        self.firmware_version_label = Label(self, text="Firmware Version:")

        # Pack labels into the window
        self.temperature_label.pack()
        self.display_power_label.pack()
        self.clock_frequency_label.pack()
        self.dram_voltage_label.pack()
        self.firmware_version_label.pack()

        # Create a canvas for the INFO UPDATE LED
        self.info_update_led_canvas = tk.Canvas(self, width=100, height=100, bg="grey", bd=0, highlightthickness=0)
        self.info_update_led_canvas.pack(side="right", padx=20)

        # Create a canvas for the CONNECTION LED
        self.connection_led_canvas = tk.Canvas(self, width=100, height=100, bg="grey", bd=0, highlightthickness=0)
        self.connection_led_canvas.pack(side="right", padx=20)

        # Create labels for CONNECTION and INFO UPDATE
        connection_label = tk.Label(self, text="CONNECTION:")
        connection_label.pack(side="right", pady=(0, 10))

        info_update_label = tk.Label(self, text="INFO UPDATE")
        info_update_label.pack(side="right", pady=(0, 10))

        # Sample data for initial update
        sample_data = {
            "Temperature": "30.0",
            "DisplayPower": "1",
            "MeasureClock": "1000000",
            "MeasureVolts": "1.2",
            "FirmwareVersion": "1.0"
        }

        # Update labels and LEDs with sample data
        self.update_labels(sample_data)
        self.update_info_update_led_color("red")  # Set initial color to red
        self.update_connection_led_color("green")  # Set initial color to green

    def update_labels(self, data_dict):
        # Function to update labels with sample data
        self.temperature_label.config(text="Core Temperature: {} C".format(data_dict["Temperature"]))
        self.display_power_label.config(text="Display Power: {}".format(data_dict["DisplayPower"]))
        self.clock_frequency_label.config(text="Clock Frequency: {} Hz".format(data_dict["MeasureClock"]))
        self.dram_voltage_label.config(text="DRAM Voltage: {} V".format(data_dict["MeasureVolts"]))
        self.firmware_version_label.config(text="Firmware Version: {}".format(data_dict["FirmwareVersion"]))

    def update_info_update_led_color(self, color):
        # Function to update the INFO UPDATE LED color and details
        self.info_update_led_canvas.delete("all")

        # Draw the INFO UPDATE LED circle
        led_radius = 35
        self.draw_gradient_circle(self.info_update_led_canvas, 50, 50, led_radius, color)

        # Draw some details on the INFO UPDATE LED
        for angle in range(0, 360, 30):
            x1 = 50 + 0.9 * led_radius * cos(radians(angle))
            y1 = 50 + 0.9 * led_radius * sin(radians(angle))
            x2 = 50 + led_radius * cos(radians(angle))
            y2 = 50 + led_radius * sin(radians(angle))
            self.info_update_led_canvas.create_line(x1, y1, x2, y2, width=2, fill="black")

    def update_connection_led_color(self, color):
        # Function to update the CONNECTION LED color and details
        self.connection_led_canvas.delete("all")

        # Draw the CONNECTION LED circle
        led_radius = 35
        self.draw_gradient_circle(self.connection_led_canvas, 50, 50, led_radius, color)

        # Draw some details on the CONNECTION LED
        for angle in range(0, 360, 30):
            x1 = 50 + 0.9 * led_radius * cos(radians(angle))
            y1 = 50 + 0.9 * led_radius * sin(radians(angle))
            x2 = 50 + led_radius * cos(radians(angle))
            y2 = 50 + led_radius * sin(radians(angle))
            self.connection_led_canvas.create_line(x1, y1, x2, y2, width=2, fill="black")

    def draw_gradient_circle(self, canvas, x, y, radius, color):
        # Function to draw a gradient-filled circle
        for i in range(radius, 0, -1):
            intensity = int(255 * (1 - i / radius))
            canvas.create_oval(x - i, y - i, x + i, y + i, fill="#%02x%02x%02x" % (intensity, intensity, intensity))

# Create an instance of the ServerGUI class
server_gui = ServerGUI()

s = socket.socket()
host = '10.102.13.65'
port = 5000
s.bind((host, port))
s.listen(5)

def update_labels(data_dict):
    server_gui.update_labels(data_dict)
    server_gui.update()

def get_pi_data():
    # Gets the Core Temperature from Pi
    measure_temp = os.popen('vcgencmd measure_temp').readline().replace("temp=", "").replace("'C\n", "")
    # Returns a boolean value
    display_power = os.popen('vcgencmd display_power').readline().strip()
    # Measure ARM clock frequency
    measure_clock = os.popen('vcgencmd measure_clock arm').readline().strip()
    # Measure sdram voltage
    measure_volts = os.popen('vcgencmd measure_volts sdram_c').readline().strip()
    # Get firmware version
    firmware_version = os.popen('vcgencmd version').readline().strip() 

    return {
        "Temperature": measure_temp,
        "DisplayPower": display_power,
        "MeasureClock": measure_clock,
        "MeasureVolts": measure_volts,
        "FirmwareVersion": firmware_version
    }

while True:
    c, addr = s.accept()
    print('Got connection from', addr)

    # Continuously send updated information every 2 seconds
    try:
        while True:
            data_dict = get_pi_data()
            update_labels(data_dict)
            time.sleep(2)

    except (ConnectionResetError, BrokenPipeError):
        print('Connection closed by client')
        c.close()

# Start the Tkinter event loop
server_gui.mainloop()
