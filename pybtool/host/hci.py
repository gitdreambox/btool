import time
from enum import IntEnum
from . import hci_transport
from .hci_cmd import HciCmd
from .hci_evt import HciEvent
from .hci_btsnoop import BTSnoop


class HCI:
    """
    HCI class
    """

    def __init__(self, transport: str = "usb"):
        self.btsnoop = BTSnoop()
        self.btsnoop.createHeader("hci_btsnoop.cfa")
        if transport == "usb":
            self.hci = hci_transport.usb_interface()
        else:
            self.hci = hci_transport.uart_interface()

    def list_devices(self):
        return self.hci.list_devices()

    @property
    def name(self):
        return self.hci.name

    def open(self, device: str = None):
        self.hci.open(device)

    def close(self):
        self.hci.close()
        self.btsnoop.close()

    def send_command(self, cmd: HciCmd, expect_evt: HciEvent = None, timeout: int = 2):
        evt = HciEvent()
        print("send cmd:" + " ".join([hex(i) for i in cmd.pack()]))
        self.btsnoop.addRecord(bytes([0x00, 0x01]) + cmd.pack())
        self.hci.send_command(cmd.pack())
        # wait for expect event timeout times
        time_start = time.time()
        while time.time() - time_start < timeout:
            recv = self.hci.receive_event()
            if len(recv) > 0:
                print("recv evt:" + " ".join([hex(i) for i in recv]))
                self.btsnoop.addRecord(bytes([0x00, 0x04]) + recv)
                evt.unpack(recv)
                if evt.event_code == expect_evt.event_code:
                    expect_evt.unpack(recv)
                    return expect_evt
        return None

    def receive_event(self):
        return self.hci.receive_event()


if __name__ == "__main__":
    from .hci_cmd import HciCmdReset

    hcicmd = HciCmdReset()
    print(hcicmd.pack().hex())
    hcicmd.unpack(bytes.fromhex("010c0300"))
    print(hcicmd.pack().hex())

    hci = HCI()
    devices = hci.list_devices()
    if len(devices) == 0:
        print("no device")
    else:
        if len(devices) == 1:
            d = devices[0]
        else:
            for i, d in enumerate(devices):
                print(i, d)
            i = input("select device:")
            d = devices[i]
        hci.open(d)
        print(f"hci open {hci.name}")
        cmd = bytes.fromhex("010c0300")
        hci.send_command(cmd)
        print("send cmd:" + " ".join([hex(i) for i in cmd]))
        evt = hci.receive_event()
        print("recv evt:" + " ".join([hex(i) for i in evt]))
        hci.close()
