import serial
import serial.tools.list_ports
from .transport import HCIInterface, Device


class uart_interface(HCIInterface):
    def __init__(self):
        self.port = "COM3"
        self.baudrate = 115200
        self.serial = None

    def list_devices(self):
        return serial.tools.list_ports.comports()

    @property
    def name(self):
        return 'uart ' + self.port + " " + str(self.baudrate)

    def open(self, device: Device = None):
        self.serial = serial.Serial(device.name, self.baudrate)

    def close(self):
        if self.serial:
            self.serial.close()

    def send_command(self, cmd:bytes):
        if self.serial:
            self.serial.write(cmd)

    def receive_event(self):
        if self.serial:
            return self.serial.read()
        return None


if __name__ == "__main__":
    hci = uart_interface()
    hci.open(Device(name="COM3", vid=0x0BDA, pid=0xC123))
    print(f"hci open {hci.name}")
    cmd = bytes.fromhex("010c0300")
    hci.send_command(cmd)
    print("send cmd:" + " ".join([hex(i) for i in cmd]))
    evt = hci.receive_event()
    print("recv evt:" + " ".join([hex(i) for i in evt]))
    hci.close()
