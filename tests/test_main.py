import unittest


class TestPyBtool(unittest.TestCase):

    @unittest.skip("skip")
    def test_hci_transport_usb(self):
        from pybtool.host.hci_transport import usb_interface
        from pybtool.host.hci_transport.transport import Device

        hci = usb_interface()
        hci.open(Device(name="test", vid=0x0BDA, pid=0xC123))
        hci.open(Device(name="test", vid=0x0BDA, pid=0xC123))
        hci.open(Device(name="test", vid=0x0BDA, pid=0xC123))
        print(f"hci open {hci.name}")
        cmd = bytes.fromhex("030c00")
        hci.send_command(cmd)
        print("send cmd:" + " ".join([hex(i) for i in cmd]))
        evt = hci.receive_event()
        print("recv evt:" + " ".join([hex(i) for i in evt]))
        hci.close()

    @unittest.skip("skip")
    def test_hci_transport_uart(self):
        import pybtool.host.hci_transport

        hci = pybtool.host.hci_transport.uart_interface()
        hci.open()
        print(f"hci open {hci.name}")
        cmd = bytes.fromhex("01030c00")
        hci.send_command(cmd)

        print("send cmd:" + " ".join([hex(i) for i in cmd]))
        evt = hci.receive_event()
        print("recv evt:" + " ".join([hex(i) for i in evt]))
        hci.close()

    def test_hci_cmd(self):
        from pybtool.host.hci_def import HciCmdReset

        hcicmd = HciCmdReset()
        print(hcicmd.tobytes().hex())
        print(hcicmd)

    def test_hci_event(self):
        from pybtool.host.hci_def import HciEvent

        hcievt = HciEvent()
        hcievt.frombytes(bytes.fromhex("0e0405030c00"))
        print(hcievt)

    def test_hci(self):
        """测试HCI类的初始化。"""
        from pybtool.host import hci

        from pybtool.host.hci_def import HciCmdReset, HciEventCommandComplete, HciEvent

        hci = hci.HCI()
        hci.open()
        print(f"hci open {hci.name}")

        hcicmd = HciCmdReset()
        print(hcicmd)
        hcievt = HciEventCommandComplete()
        hcievt = hci.send_command(hcicmd, hcievt)
        print(hcievt)
        hci.close()


if __name__ == "__main__":
    unittest.main()
