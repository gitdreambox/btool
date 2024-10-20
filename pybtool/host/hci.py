import time
import queue
import logging
from enum import IntEnum
from . import hci_transport
from .hci_cmd import *
from .hci_evt import *
from .hci_btsnoop import BTSnoop

logger = logging.getLogger(__name__)

hci_init_cmds = [
    (HciCmdReset, HciEventCommandComplete),
    (HciCmdReadLocalName, HciEventCommandCompleteLocalName),
    (HciCmdReadBdAddr, HciEventCommandCompleteBdAddr),
    (HciCmdReadBufferSize, HciEventCommandCompleteBufferSize),
    (HciCmdReadLocalVersionInfo, HciEventCommandCompleteLocalVersionInfo),
    (HciCmdReadLocalSupportedCommands, HciEventCommandCompleteLocalSupportedCommands),
    (HciCmdReadLocalSupportedFeatures, HciEventCommandCompleteLocalSupportedFeatures),
    (HciCmdSetEventMask, HciEventCommandComplete),
    (
        HciCmdLeReadlocalSupportedFeaturesPage0,
        HciEventCommandCompleteLeLocalSupportedFeatures,
    ),
]

hci_evt_handlers = {
    HciEventDisconnectionComplete.EVENT_CODE: HciEventDisconnectionComplete,
    HciEventCommandComplete.EVENT_CODE: HciEventCommandComplete,
    HciEventCommandStatus.EVENT_CODE: HciEventCommandStatus,
    HciEventLeMeta.EVENT_CODE: HciEventLeMeta,
}

hci_evt_le_handlers = {
    HciEventLeConnectionComplete.SUBEVENT_CODE: HciEventLeConnectionComplete,
    HciEventLeConnectionUpdateComplete.SUBEVENT_CODE: HciEventLeConnectionUpdateComplete,
}


class HCI:
    """
    HCI class
    """

    def __init__(self, transport: str = "usb"):
        print(__name__)
        self.acl_callback = None
        self.event_callback = None
        self.event_queue = queue.Queue()
        self.acl_queue = queue.Queue()
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
        self.hci.register_event(self.event_handler)
        self.hci.register_acl(self.acl_handler)

    def close(self):
        self.hci.close()
        self.btsnoop.close()

    def send_command(self, cmd: HciCmd, expect_evt: HciEvent = None, timeout: int = 2):
        evt = HciEvent()
        logger.info("send cmd:" + " ".join([hex(i) for i in cmd.pack()]))
        self.btsnoop.addRecord(bytes([0x00, 0x01]) + cmd.pack())
        self.hci.send_command(cmd.pack())
        # wait for expect event timeout times
        time_start = time.time()
        while time.time() - time_start < timeout:
            recv = self.receive_event()
            if len(recv) > 0:
                evt.unpack(recv)
                if evt.event_code == expect_evt.EVENT_CODE:
                    expect_evt.unpack(recv)
                    return expect_evt
        return None
    
    def send_acl(self, data: bytes):
        logger.info("send acl:" + " ".join([hex(i) for i in data]))
        self.btsnoop.addRecord(bytes([0x00, 0x02]) + data)
        self.hci.send_acl(data)

    def event_handler(self, evt_data: bytes):
        logger.info("recv evt:" + " ".join([hex(i) for i in evt_data]))
        self.event_queue.put(evt_data)
        self.btsnoop.addRecord(bytes([0x00, 0x04]) + evt_data)
        if evt_data[0] in hci_evt_handlers:
            evt = hci_evt_handlers[evt_data[0]]()
            evt.unpack(evt_data)
            if evt.event_code == HciEventLeMeta.EVENT_CODE:
                if evt.subevent_code in hci_evt_le_handlers:
                    evt = hci_evt_le_handlers[evt.subevent_code]()
                    evt.unpack(evt_data)
            print(evt)
            

    def acl_handler(self, acl_data: bytes):
        logger.info("recv acl:" + " ".join([hex(i) for i in acl_data]))
        self.acl_queue.put(acl_data)
        self.btsnoop.addRecord(bytes([0x00, 0x02]) + acl_data)

    def receive_event(self) -> bytes:
        try:
            return self.event_queue.get(block=False)
        except queue.Empty:
            return bytes()

    def receive_acl(self) -> bytes:
        try:
            return self.acl_queue.get(block=False)
        except queue.Empty:
            return bytes()

    def register_acl(self, cb: callable):
        """
        注册 ACL 数据回调函数
        """
        self.hci.register_acl(cb)


    def init(self):
        """
        hci module init
        """
        for h in hci_init_cmds:
            hcicmd = h[0]()
            logger.info(hcicmd)
            hcievt = h[1]()
            hcievt = self.send_command(hcicmd, hcievt)
            logger.info(hcievt)


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
