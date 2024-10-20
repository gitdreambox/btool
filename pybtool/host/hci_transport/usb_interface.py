import usb.core
import usb.util
import usb.backend.libusb1
import libusb
import threading
from .transport import HCIInterface, Device

backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb-1.0.dll")

class usb_interface(HCIInterface):
    # Endpoints for HCI CMD, EVT, ACL
    USB_HCI_SCO_R_ENDP = 0x83  # isochornous
    USB_HCI_SCO_W_ENDP = 0x03  # isochornous
    USB_HCI_ACL_R_ENDP = 0x82  # bulk
    USB_HCI_ACL_W_ENDP = 0x02  # bulk
    USB_HCI_CMD_W_ENDP = 0x00  # control - use controlMsg method
    USB_HCI_INT_R_ENDP = 0x81  # interrupt

    def __init__(self):
        self.vendor_id = 0
        self.product_id = 0
        self.device = None
        self.running = False
        self.receive_thread = None
        self.event_callbacks = []
        self.acl_callbacks = []

    @property
    def name(self):
        return "usb" + " vid:" + str(self.vendor_id) + " pid:" + str(self.product_id)

    def list_devices(self):
        devices = usb.core.find(find_all=True, bDeviceClass=0xE0)
        d = [
            Device(
                # f"{usb.util.get_string(device, device.iManufacturer)} {usb.util.get_string(device, device.iProduct)} {hex(device.idVendor)} {hex(device.idProduct)} ",
                f"{hex(device.idVendor)} {hex(device.idProduct)} ",
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

        # 启动接收线程
        self.running = True
        self.receive_thread = threading.Thread(target=self._receive_loop,daemon=True)
        self.receive_thread.start()
        

    def close(self):
        self.running = False
        if self.receive_thread:
            self.receive_thread.join()
        if self.device:
            usb.util.dispose_resources(self.device)

    def send_command(self, cmd: bytes):
        if self.device:
            self.device.ctrl_transfer(0x21, 0x00, 0, 0, cmd)

    def send_acl(self, data: bytes):
        if self.device:
            self.device.write(self.USB_HCI_ACL_W_ENDP, data, 0)   

    def register_event(self, cb: callable):
        """
        注册事件回调函数
        """
        if cb not in self.event_callbacks:
            self.event_callbacks.append(cb)

    def unregister_event(self, cb: callable):
        """
        取消注册事件回调函数
        """
        if cb in self.event_callbacks:
            self.event_callbacks.remove(cb)

    def register_acl(self, cb: callable):
        """
        注册 ACL 数据回调函数
        """
        if cb not in self.acl_callbacks:
            self.acl_callbacks.append(cb)

    def unregister_acl(self, cb: callable):
        """
        取消注册 ACL 数据回调函数
        """
        if cb in self.acl_callbacks:
            self.acl_callbacks.remove(cb)

    def _receive_loop(self):
        while self.running:
            try:
                # 读取 HCI 事件
                evt = self.device.read(0x81, 256, 100)
                if evt:
                    evt_data = evt.tobytes()
                    for cb in self.event_callbacks:
                        cb(evt_data)

                # 读取 ACL 数据
                acl = self.device.read(0x82, 256, 100)
                if acl:
                    acl_data = acl.tobytes()
                    for cb in self.acl_callbacks:
                        cb(acl_data)

            except usb.core.USBError as e:
                if e.errno == 10060:  # 超时错误，可以忽略
                    pass
                else:
                    print(f"USB Error: {e}")


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
