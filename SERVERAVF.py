import socket
import os
import json
import time
import threading
import tkinter as tk
from tkinter import Label, Canvas, Button
from math import sin, cos, radians

class MovableWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Remove window decorations
        self.overrideredirect(1)

        # Create a frame with a grey rectangle
        self.frame = tk.Frame(self, bg="grey", bd=10, relief="solid")
        self.frame.pack(expand=True, fill="both")

        # Make the window movable
        self.bind("<B1-Motion>", self.drag_window)
        self.bind("<Button-3>", self.close_window)

        # Initialize offset values
        self._offsetx = 0
        self._offsety = 0
        self.iteration_count = 0

        # Function to create a label with a border
        def create_bordered_label(parent, text, bold=False):
            label_frame = tk.Frame(parent, bg="grey", bd=2, relief="solid")
            label_frame.grid(sticky="w")

            font_weight = "bold" if bold else "normal"
            label = Label(label_frame, text=text, bg="grey", fg="white", bd=0, font=("Helvetica", 12, font_weight))
            label.pack(padx=5, pady=5)

        # Create a big bold label for "RASPBERRY PI"
        title_label = Label(self.frame, text="RASPBERRY PI", font=("Helvetica", 16, "bold"), bg="grey", fg="white")
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))

        # Create labels to display data
        create_bordered_label(self.frame, "Core Temperature:", bold=True)
        create_bordered_label(self.frame, "Display Power:", bold=True)
        create_bordered_label(self.frame, "Clock Frequency:", bold=True)
        create_bordered_label(self.frame, "DRAM Voltage:", bold=True)

        # Create a canvas for the INFO UPDATE LED
        self.info_update_led_canvas = Canvas(self.frame, width=100, height=100, bg="grey", bd=0, highlightthickness=0)
        self.info_update_led_canvas.grid(row=1, column=2, rowspan=4, padx=(20, 0))

        # Create an Exit button (bolded)
        exit_button = Button(self.frame, text="Exit", command=self.destroy, font=("Helvetica", 12, "bold"))
        exit_button.grid(row=6, column=0, columnspan=4, pady=(10, 0))

        # Sample data for initial update
        sample_data = {
            "Temperature": "30.0",
            "DisplayPower": "1",
            "MeasureClock": "1000000",
            "MeasureVolts": "1.2",
        }

        # Update labels and LEDs with sample data
        self.update_labels(sample_data)
        self.update_info_update_led_color("red")  # Set initial color to red

    def update_labels(self, data_dict):
    # Function to update labels with sample data
        for child in self.frame.winfo_children():
            if isinstance(child, tk.Frame) and child.winfo_children():
                label = child.winfo_children()[0]
                if label.cget("text") == "RASPBERRY PI":
                    label.config(text="RASPBERRY PI (Iteration: {})".format(self.iteration_count))
                    break

    def blink_info_update_led(self):
        # Blink the info update LED
        self.info_update_led_canvas.delete("all")
        self.draw_gradient_circle(self.info_update_led_canvas, 50, 50, 35, "red")
        self.after(500, lambda: self.info_update_led_canvas.delete("all"))
        
          # Increment the iteration count
        self.iteration_count += 1


    def update_info_update_led_color(self, color):
        # Function to update the INFO UPDATE LED color and details
        self.info_update_led_canvas.delete("all")
        self.draw_gradient_circle(self.info_update_led_canvas, 50, 50, 35, color)

    def draw_gradient_circle(self, canvas, x, y, radius, color):
        # Function to draw a filled circle with the specified color
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline="")

    def drag_window(self, event):
        # Function to drag the window
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry(f"+{x}+{y}")

    def close_window(self, event):
        # Function to close the window
        self.destroy()


def server_thread():
    s = socket.socket()
    host = '10.102.13.55'  # Listen on all available interfaces
    port = 5000
    s.bind((host, port))
    s.listen(5)

    def get_pi_data():
        # gets the Core Temperature from Pi
        measure_temp = os.popen('vcgencmd measure_temp').readline().replace("temp=", "").replace("'C\n", "")
        # Returns a boolean value
        display_power = os.popen('vcgencmd display_power').readline().strip()
        # Measure ARM clock frequency
        measure_clock = os.popen('vcgencmd measure_clock arm').readline().strip()
        # Measure sdram voltage
        measure_volts = os.popen('vcgencmd measure_volts sdram_c').readline().strip()

        return {
            "Temperature": measure_temp,
            "DisplayPower": display_power,
            "MeasureClock": measure_clock,
            "MeasureVolts": measure_volts
        }

    # Accept connections
    while True:
        c, addr = s.accept()
        print('Got connection from', addr)

        # Continuously send updated information every 2 seconds
        try:
            while True:
                data_dict = get_pi_data()

                # Convert dictionary to JSON-formatted string
                json_string = json.dumps(data_dict, indent=2)

                # Update labels and LEDs with data
                app.update_labels(data_dict)

                # Send the JSON string as bytes
                c.send(json_string.encode('utf-8'))

                # Flash the INFO UPDATE LED (red)
                app.blink_info_update_led()
                time.sleep(1.5)  # Total delay of 2 seconds

        except (ConnectionResetError, BrokenPipeError):
            print('Connection closed by client')
            c.close()

if __name__ == "__main__":
    # Create GUI window
    app = MovableWindow()

    # Create and start the server thread
    server_thread = threading.Thread(target=server_thread)
    server_thread.start()

    # Start the GUI event loop
    app.mainloop()