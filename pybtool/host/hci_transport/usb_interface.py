import usb.core
import usb.util
import usb.backend.libusb1
import libusb
from .transport import HCIInterface, Device

backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb-1.0.dll")


class usb_interface(HCIInterface):
    def __init__(self):
        self.vendor_id = 0
        self.product_id = 0
        self.device = None

    @property
    def name(self):
        return "usb" + " vid:" + str(self.vendor_id) + " pid:" + str(self.product_id)

    def list_devices(self):
        devices = usb.core.find(find_all=True, bDeviceClass=0xE0)
        d = [
            Device(
                f"{usb.util.get_string(device, device.iManufacturer)} {usb.util.get_string(device, device.iProduct)} {hex(device.idVendor)} {hex(device.idProduct)} ",
                device.idVendor,
                device.idProduct,
            )
            for device in devices
        ]
        return d

    def open(self, device: Device = None):
        if device is None:
            self.device = usb.core.find(idVendor=0x0BDA, idProduct=0xC123)
        else:
            self.device = usb.core.find(idVendor=device.vid, idProduct=device.pid)
        if self.device is None:
            raise ValueError("Device not found")
        self.device.set_configuration()

    def close(self):
        if self.device:
            usb.util.dispose_resources(self.device)

    def send_command(self, cmd: bytes):
        if self.device:
            self.device.ctrl_transfer(0x21, 0x00, 0, 0, cmd)

    def register_event(self, cb: callable):
        """
        register event callback
        """
        pass

    def receive_event(self) -> bytes:
        try:
            if self.device:
                d = self.device.read(0x81, 256, 100)
                return d.tobytes()
        except usb.core.USBError as e:
            if e.errno == 10060:
                pass
            else:
                print(e)
        return bytes()


if __name__ == "__main__":
    hci = usb_interface()
    hci.open(Device(name="test", vid=0x0BDA, pid=0xC123))
    print(f"hci open {hci.name}")
    cmd = bytes.fromhex("010c0300")
    hci.send_command(cmd)
    print("send cmd:" + " ".join([hex(i) for i in cmd]))
    evt = hci.receive_event()
    print("recv evt:" + " ".join([hex(i) for i in evt]))
    hci.close()
