import serial
from .hci_interface import HCIInterface

class UARTInterface(HCIInterface):
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = None

    def open(self):
        self.serial = serial.Serial(self.port, self.baudrate)

    def close(self):
        if self.serial:
            self.serial.close()

    def send_command(self, command):
        if self.serial:
            self.serial.write(command)

    def receive_event(self):
        if self.serial:
            return self.serial.read()
        return None