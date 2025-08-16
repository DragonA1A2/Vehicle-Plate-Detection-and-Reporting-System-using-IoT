import serial
import time
import os
import platform
from serial.tools import list_ports


class GateController:
    def __init__(self, port=None, baud_rate=9600):
        if port is None:
            # Get port from environment variable, with platform-specific default
            if platform.system() == "Windows":
                port = os.getenv("ARDUINO_PORT", "COM9")
            else:
                port = os.getenv("ARDUINO_PORT", "/dev/ttyUSB0")

        self.port = port
        self.baud_rate = int(os.getenv("ARDUINO_BAUD_RATE", baud_rate))
        self.serial_connection = None
        self.last_sensor_read = 0

    @staticmethod
    def list_available_ports():
        """List all available serial ports"""
        ports = list_ports.comports()
        return [port.device for port in ports]

    def connect(self):
        try:
            # First, check if port is available
            available_ports = self.list_available_ports()
            print(f"Available ports: {available_ports}")

            if self.port not in available_ports:
                print(f"Warning: {self.port} not found in available ports!")
                if available_ports:
                    print(f"Available ports are: {available_ports}")
                    # Try the first available port
                    self.port = available_ports[0]
                    print(f"Trying first available port: {self.port}")

            # Try to close the port if it's already open
            try:
                temp_connection = serial.Serial(self.port)
                temp_connection.close()
            except:
                pass

            print(f"Attempting to connect to Arduino on port {self.port}...")
            self.serial_connection = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            print("Successfully connected to Arduino!")
            return True

        except Exception as e:
            print(f"Failed to connect to Arduino: {str(e)}")
            print("\nTroubleshooting steps:")
            print("1. Make sure Arduino is properly connected")
            print("2. Close Arduino IDE and any Serial Monitors")
            print("3. Check Device Manager for correct COM port")
            print("4. Try unplugging and replugging the Arduino")
            return False

    def open_gate(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b"O")
                print("Gate opening...")
                return True
            except Exception as e:
                print(f"Error sending open command to Arduino: {str(e)}")
                return False
        return False

    def close_gate(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b"C")
                print("Gate closing...")
                return True
            except Exception as e:
                print(f"Error sending close command to Arduino: {str(e)}")
                return False
        return False

    def read_serial_feedback(self):
        """Read and process any feedback from Arduino"""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting:
                    message = self.serial_connection.readline().decode().strip()
                    print(f"Arduino: {message}")
                    return message
            except Exception as e:
                print(f"Error reading from Arduino: {str(e)}")
        return None

    def operate_gate_with_timer(self, open_time=5):
        """Open gate, wait for specified time, then close it"""
        if self.open_gate():
            print(f"Keeping gate open for {open_time} seconds...")

            # Wait and process any sensor feedback during the wait
            start_time = time.time()
            while time.time() - start_time < open_time:
                self.read_serial_feedback()
                time.sleep(0.1)

            self.close_gate()
            return True
        return False

    def close(self):
        if self.serial_connection:
            try:
                self.serial_connection.close()
                print("Serial connection closed successfully")
            except Exception as e:
                print(f"Error closing serial connection: {str(e)}")
