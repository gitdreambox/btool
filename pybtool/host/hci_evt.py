import struct
from ctypes import *
from .hci_def import *


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


class HciEventCommandCompleteLocalVersionInfo(HciEventCommandComplete):
    """
    HCI command complete event for buffer size
    """

    def __init__(self):
        super().__init__()
        self.hci_version = 0
        self.hci_subversion = 0
        self.lmp_version = 0
        self.company_identifier = 0
        self.lmp_subversion = 0

    def unpack(self, data: bytes):
        super().unpack(data)
        if (
            self.event_code == 0x0E
            and self.opcode == HCI_OPCODE.HCI_CMD_READ_LOCAL_VERSION_INFO
        ):
            _format = "<BHBHH"
            (
                self.hci_version,
                self.hci_subversion,
                self.lmp_version,
                self.company_identifier,
                self.lmp_subversion,
            ) = struct.unpack(_format, self.param[4 : 4 + 8])

    def __str__(self):
        return (
            super().__str__()
            + f", hci_version: {self.hci_version}, hci_subversion: {self.hci_subversion}, lmp_version: {self.lmp_version}, company_identifier: {self.company_identifier}, lmp_subversion: {self.lmp_subversion}"
        )


class HciEventCommandCompleteLocalSupportedCommands(HciEventCommandComplete):
    """
    HCI command complete event for buffer size
    """

    def __init__(self):
        super().__init__()
        self.supported_commands = bytes()

    def unpack(self, data: bytes):
        super().unpack(data)
        if (
            self.event_code == 0x0E
            and self.opcode == HCI_OPCODE.HCI_CMD_READ_LOCAL_SUPPORTED_COMMANDS
        ):
            _format = "<64B"
            self.supported_commands = self.param[4 : 4 + 64]

    def __str__(self):
        return (
            super().__str__()
            + f", supported_commands: {' '.join([hex(i) for i in self.supported_commands])}"
        )


class HciEventCommandCompleteLocalSupportedFeatures(HciEventCommandComplete):
    """
    HCI command complete event for buffer size
    """

    def __init__(self):
        super().__init__()
        self.lmp_features = bytes()

    def unpack(self, data: bytes):
        super().unpack(data)
        if (
            self.event_code == 0x0E
            and self.opcode == HCI_OPCODE.HCI_CMD_READ_LOCAL_SUPPORTED_FEATURES
        ):
            _format = "<8B"
            self.lmp_features = self.param[4:]

    def __str__(self):
        return (
            super().__str__()
            + f", lmp_features: {' '.join([hex(i) for i in self.lmp_features])}"
        )


class LeLocalSupportedFeaturesStruct(Structure):
    _fields_ = [
        ("LE_Encryption ", c_uint8, 1),
        ("ConnectionParametersRequestprocedure", c_uint8, 1),
        ("ExtendedRejectIndication", c_uint8, 1),
        ("PeripheralInitiatedFeaturesExchange", c_uint8, 1),
        ("LE_Ping", c_uint8, 1),
        ("LE_DataPacketLengthExtension ", c_uint8, 1),
        ("LL_Privacy ", c_uint8, 1),
        ("ExtendedScanningFilterPolicies ", c_uint8, 1),
        ("LE_2M_PHY ", c_uint8, 1),
        ("StableModulationIndexTransmitter ", c_uint8, 1),
        ("StableModulationIndexReceiver ", c_uint8, 1),
        ("LE_Coded_PHY ", c_uint8, 1),
        ("LE_ExtendedAdvertising ", c_uint8, 1),
        ("LE_PeriodicAdvertising ", c_uint8, 1),
        ("ChannelSelectionAlgorithm2", c_uint8, 1),
        ("LE_PowerClass1", c_uint8, 1),
    ]


class LeLocalSupportedFeaturesUnion(Union):
    _fields_ = [("w", c_uint8 * 8), ("b", LeLocalSupportedFeaturesStruct)]


class LeLocalSupportedFeatures(HStructure):
    """
    le local supported features
    """

    _fields_ = [("le_features", LeLocalSupportedFeaturesUnion)]


class HciEventCommandCompleteLeLocalSupportedFeatures(HciEventCommandComplete):
    """
    HCI command complete event for buffer size
    """

    def __init__(self):
        super().__init__()
        self.le_features = LeLocalSupportedFeatures()

    def unpack(self, data: bytes):
        super().unpack(data)
        if (
            self.event_code == 0x0E
            and self.opcode == HCI_OPCODE.HCI_CMD_LE_READ_LOCAL_SUPPORTED_FEATURES
        ):
            self.le_features.unpack(self.param[4 : 4 + 8])

    def __str__(self):
        return super().__str__() + "\n" + self.le_features.__str__()
