import struct
from host.hci_cmd import HCI_OPCODE
from enum import IntEnum


class HciEvent:
    """
    HCI Event
    """

    def __init__(self):
        """
        HCI event
        |event code|Parameter Total Length|Event Parameter|
        """
        self.pkt_type = 0x04  # event packet
        self.event_code = 0x00
        self.len = 0
        self.param = bytes()

    def unpack(self, data: bytes):
        """
        convert from bytes
        """
        if len(data) < 2 or len(data) < (2 + data[1]):
            raise ValueError("data too short")
        self.event_code, self.len = struct.unpack("<BB", data[:2])
        self.param = data[2 : 2 + self.len]

    def __str__(self):
        return f"hci event code: 0x{self.event_code:02X}, len: {self.len}, param: {self.param.hex()}"


class HciEventCommandComplete(HciEvent):
    """
    HCI command complete event
    """

    def __init__(self):
        super().__init__()
        self.event_code = 0x0E
        self.len = 0x04
        self.num_hci_cmd_packets = 0
        self.opcode = 0
        self.status = 0

    def unpack(self, data: bytes):
        """
        convert from bytes
        """
        super().unpack(data)
        if self.event_code == 0x0E:
            self.num_hci_cmd_packets, self.opcode, self.status = struct.unpack(
                "<BHB", self.param[:4]
            )

    def __str__(self):
        return f"hci event code: 0x{self.event_code:02X}, len: {self.len}, num_hci_cmd_packets: {self.num_hci_cmd_packets}, opcode: 0x{self.opcode:04X}, status: 0x{self.status:02X}"


class HciEventCommandCompleteLocalName(HciEventCommandComplete):
    """
    HCI command complete event for local version info
    """

    def __init__(self):
        super().__init__()
        self.local_name = ""

    def unpack(self, data: bytes):
        super().unpack(data)
        if (
            self.event_code == 0x0E
            and self.opcode == HCI_OPCODE.HCI_CMD_READ_LOCAL_NAME
        ):
            self.local_name = self.param[4:].decode("utf-8")

    def __str__(self):
        return super().__str__() + f", local_name: {self.local_name}"


class HciEventCommandCompleteBdAddr(HciEventCommandComplete):
    """
    HCI command complete event for bd addr
    """

    def __init__(self):
        super().__init__()
        self.bd_addr = ""

    def unpack(self, data: bytes):
        super().unpack(data)
        if self.event_code == 0x0E and self.opcode == HCI_OPCODE.HCI_CMD_READ_BD_ADDR:
            self.bd_addr = ":".join([f"{i:02X}" for i in self.param[4:10]])

    def __str__(self):
        return super().__str__() + f", bd_addr: {self.bd_addr}"


class HciEventCommandCompleteBufferSize(HciEventCommandComplete):
    """
    HCI command complete event for buffer size
    """

    def __init__(self):
        super().__init__()
        self.acl_data_packet_size = 0
        self.sco_data_packet_size = 0
        self.total_num_acl_data_packets = 0
        self.total_num_sco_data_packets = 0

    def unpack(self, data: bytes):
        super().unpack(data)
        if (
            self.event_code == 0x0E
            and self.opcode == HCI_OPCODE.HCI_CMD_READ_BUFFER_SIZE
        ):
            (
                self.acl_data_packet_size,
                self.sco_data_packet_size,
                self.total_num_acl_data_packets,
                self.total_num_sco_data_packets,
            ) = struct.unpack("<HBHH", self.param[4 : 4 + 7])

    def __str__(self):
        return (
            super().__str__()
            + f", acl_data_packet_size: {self.acl_data_packet_size}, sco_data_packet_size: {self.sco_data_packet_size}, total_num_acl_data_packets: {self.total_num_acl_data_packets}, total_num_sco_data_packets: {self.total_num_sco_data_packets}"
        )
