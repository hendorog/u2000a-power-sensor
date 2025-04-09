import pyvisa
import time
import tkinter as tk
from tkinter import ttk, messagebox

class USBPowerSensor:
    def __init__(self, resource_name):
        self.rm = pyvisa.ResourceManager()
        self.rm.timeout = 1000
        self.instrument = self.rm.open_resource(resource_name)
        self.instrument.timeout = 5000  # timeout in milliseconds

    def identify(self):
        return self.instrument.query("*IDN?").strip()

    def measure_power(self):
        response = self.instrument.query("MEASure?").strip()
        return float(response)

    def calibrate_zero_internal(self):
        self.instrument.write("CALibration:ZERO:TYPE INTernal")
        self.instrument.write("CALibration:ZERO:AUTO ONCE")
        time.sleep(5)  # give some time to complete calibration

    def calibrate_zero_external(self):
        self.instrument.write("CALibration:ZERO:TYPE EXTernal")
        self.instrument.write("CALibration:ZERO:AUTO ONCE")
        time.sleep(5)  # give some time to complete calibration

    def set_display_unit(self, unit):
        if unit.lower() == "dbm":
            self.instrument.write("UNIT:POWer DBM")
        elif unit.lower() == "mw":
            self.instrument.write("UNIT:POWer W")
        else:
            raise ValueError("Invalid unit. Use 'mW' or 'dBm'.")

    def close(self):
        self.instrument.close()
        self.rm.close()

class PowerSensorGUI:
    def __init__(self, root):
        self.sensor = None

        self.root = root
        self.root.title("USB Power Sensor")

        ttk.Label(root, text="Resource Address:").grid(row=0, column=0, padx=5, pady=5)
        self.resource_entry = ttk.Entry(root, width=40)
        self.resource_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(root, text="Connect", command=self.connect_sensor).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(root, text="List Sensors", command=self.list_sensors).grid(row=0, column=3, padx=5, pady=5)

        self.measurement_var = tk.StringVar(value="Measurement: ---")
        ttk.Label(root, textvariable=self.measurement_var, font=("Arial", 16)).grid(row=1, column=0, columnspan=4, pady=10)

        ttk.Button(root, text="Measure (dBm)", command=lambda: self.measure("dBm")).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(root, text="Measure (mW)", command=lambda: self.measure("mW")).grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(root, text="Internal Calibration", command=self.internal_calibration).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(root, text="External Calibration", command=self.external_calibration).grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(root, text="Disconnect", command=self.disconnect_sensor).grid(row=2, column=2, padx=5, pady=5)

    def connect_sensor(self):
        resource = self.resource_entry.get()
        try:
            self.sensor = USBPowerSensor(resource)
            messagebox.showinfo("Connected", f"Connected to sensor:\n{self.sensor.identify()}")
        except Exception as e:
            self.sensor = None
            messagebox.showerror("Connection Error", str(e))

    def list_sensors(self):
        try:
            rm = pyvisa.ResourceManager()
            rm.timeout = 5000  # 5000ms timeout
            resources = rm.list_resources()
            sensor_list = "\n".join(resources)
            messagebox.showinfo("Connected Sensors", sensor_list)
        except Exception as e:
            messagebox.showerror("List Error", str(e))

    def measure(self, unit):
        if not self.sensor:
            messagebox.showerror("Error", "Sensor not connected!")
            return

        try:
            self.sensor.set_display_unit(unit)
            power = self.sensor.measure_power()
            if unit == "mW":
                power *= 1000  # convert W to mW
            self.measurement_var.set(f"Measurement: {power:.3f} {unit}")
        except Exception as e:
            messagebox.showerror("Measurement Error", str(e))

    def internal_calibration(self):
        if self.sensor:
            self.sensor.calibrate_zero_internal()
            messagebox.showinfo("Calibration", "Internal calibration completed.")
        else:
            messagebox.showerror("Error", "Sensor not connected!")

    def external_calibration(self):
        if self.sensor:
            self.sensor.calibrate_zero_external()
            messagebox.showinfo("Calibration", "External calibration completed.")
        else:
            messagebox.showerror("Error", "Sensor not connected!")

    def disconnect_sensor(self):
        if self.sensor:
            self.sensor.close()
            self.sensor = None
            messagebox.showinfo("Disconnected", "Sensor disconnected successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PowerSensorGUI(root)
    root.mainloop()
