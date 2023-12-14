import socket
import os
import json
import time
import threading
import tkinter as tk
from tkinter import Label, Canvas, Button

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

        # Initialize iteration count as a class variable
        MovableWindow.iteration_count = 0

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
        create_bordered_label(self.frame, "Disk Usage:", bold=True)  # Added Extra Data label
        
        # Create a canvas for the INFO UPDATE LED
        self.info_update_led_canvas = Canvas(self.frame, width=100, height=100, bg="grey", bd=0, highlightthickness=0)
        self.info_update_led_canvas.grid(row=1, column=2, rowspan=6, padx=(20, 0))

        # Create an Exit button (bolded)
        exit_button = Button(self.frame, text="Exit", command=self.destroy, font=("Helvetica", 12, "bold"))
        exit_button.grid(row=8, column=0, columnspan=4, pady=(10, 0))

        # Create a label to display iteration count
        self.iteration_label = self.create_data_label("Iteration: 0", row=9, column=0, columnspan=4, pady=(10, 0))

        # Sample data for initial update
        sample_data = {
            "Temperature": "30.0",
            "DisplayPower": "1",
            "MeasureClock": "1000000",
            "MeasureVolts": "1.2",
            "DiskUsage": "42.0",  # Added the fifth Pi data
           
        }

        # Update labels and LEDs with sample data
        self.update_labels(sample_data)
        self.update_info_update_led_color("red")  # Set initial color to red

        # Initialize iteration count
        MovableWindow.iteration_count = 0

    def create_data_label(self, text, row, column, columnspan, pady):
        # Function to create a label for data display
        label_frame = tk.Frame(self.frame, bg="grey", bd=2, relief="solid")
        label_frame.grid(row=row, column=column, columnspan=columnspan, pady=pady, sticky="w")

        label = Label(label_frame, text=text, bg="grey", fg="white", bd=0, font=("Helvetica", 12))
        label.pack(padx=5, pady=5)

        return label

    def update_labels(self, data_dict):
        
        # Function to update labels with sample data
        temperature_label = self.frame.winfo_children()[1].winfo_children()[0]
        temperature_label.config(text="Core Temperature: {} C".format(data_dict["Temperature"]))

        display_power_label = self.frame.winfo_children()[2].winfo_children()[0]
        display_power_label.config(text="Display Power: {}".format(data_dict["DisplayPower"]))

        clock_frequency_label = self.frame.winfo_children()[3].winfo_children()[0]
        clock_frequency_label.config(text="Clock Frequency: {} Hz".format(data_dict["MeasureClock"]))

        dram_voltage_label = self.frame.winfo_children()[4].winfo_children()[0]
        dram_voltage_label.config(text="DRAM Voltage: {} V".format(data_dict["MeasureVolts"]))

        # Update the iteration count label
        self.iteration_label.config(text="Iteration: {}".format(MovableWindow.iteration_count))

        # Display the new Pi data
        disk_usage = self.frame.winfo_children()[5].winfo_children()[0]
        disk_usage.config(text="Disk Usage: {}".format(data_dict["DiskUsage"]))

      
    def blink_info_update_led(self):
        # Blink the info update LED
        self.info_update_led_canvas.delete("all")
        self.draw_gradient_circle(self.info_update_led_canvas, 50, 50, 35, "red")
        self.after(500, lambda: self.info_update_led_canvas.delete("all"))

    def update_info_update_led_color(self, color):
        # Function to update the INFO UPDATE LED color and details
        self.info_update_led_canvas.delete("all")
        self.draw_gradient_circle(self.info_update_led_canvas, 50, 50, 35, color)

    def draw_gradient_circle(self, canvas, x, y, radius, color):
        # Function to draw a gradient-filled circle
        for i in range(radius, 0, -1):
            intensity = int(255 * (1 - i / radius))
            canvas.create_oval(x - i, y - i, x + i, y + i, fill="#%02x%02x%02x" % (intensity, 0, 0), outline="")

    def drag_window(self, event):
        # Function to drag the window
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry(f"+{x}+{y}")

    def close_window(self, event):
        # Function to close the window
        self.destroy()

def server_thread(app):
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
        # Extra Pi data (replace with actual commands)
        disk_usage_data = os.popen('df -h / | awk \'NR==2{printf "%s", $5}\'').readline().strip()
       
        return {
            "Temperature": measure_temp,
            "DisplayPower": display_power,
            "MeasureClock": measure_clock,
            "MeasureVolts": measure_volts,
            "DiskUsage": disk_usage_data,
           
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

                # Increment iteration count
                MovableWindow.iteration_count += 1

                # Check if 50 iterations reached and exit
                if MovableWindow.iteration_count >= 50:
                    app.destroy()

                time.sleep(1.5)  # Total delay of 2 seconds

        except (ConnectionResetError, BrokenPipeError):
            print('Connection closed by client')
            c.close()

if __name__ == "__main__":
    app = MovableWindow()
    server_thread = threading.Thread(target=server_thread, args=(app,))
    server_thread.start()
    app.mainloop()


