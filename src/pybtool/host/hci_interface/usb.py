import usb.core
import usb.util
from .hci_interface import HCIInterface

class USBInterface(HCIInterface):
    def __init__(self, vendor_id, product_id):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = None

    def open(self):
        self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
        if self.device is None:
            raise ValueError('Device not found')

    def close(self):
        if self.device:
            usb.util.dispose_resources(self.device)

    def send_command(self, command):
        if self.device:
            self.device.write(1, command)

    def receive_event(self):
        if self.device:
            return self.device.read(0x81, 64)
        return None