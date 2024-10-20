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


class HciEventDisconnectionComplete(HciEvent):
    """
    HCI LE disconnection complete event
    """
    EVENT_CODE = 0x05
    def __init__(self):
        super().__init__()
        self.event_code = 0
        self.len = 0
        self.status = 0
        self.connection_handle = 0
        self.reason = 0

    def unpack(self, data: bytes):
        """
        convert from bytes
        """
        super().unpack(data)
        if self.event_code == self.EVENT_CODE:
            _format = "<BHB"
            _offset = 0
            _len = struct.calcsize(_format)
            self.status, self.connection_handle, self.reason = struct.unpack(_format, self.param[_offset:_offset+_len])

    def __str__(self):
        return f"hci event code: 0x{self.event_code:02X} HCI_Disconnection_Complete, len: {self.len}, status: {StatusType(self.status).name}, connection_handle: 0x{self.connection_handle:04X}, reason: {DisconnectionReasonType(self.reason).name}"


class HciEventCommandComplete(HciEvent):
    """
    HCI command complete event
    """
    EVENT_CODE = 0x0E
    def __init__(self):
        super().__init__()
        self.event_code = 0
        self.len = 0x04
        self.num_hci_cmd_packets = 0
        self.opcode = 0
        self.status = 0

    def unpack(self, data: bytes):
        """
        convert from bytes
        """
        super().unpack(data)
        if self.event_code == self.EVENT_CODE:
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
            self.event_code == self.EVENT_CODE
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
        if self.event_code == self.EVENT_CODE and self.opcode == HCI_OPCODE.HCI_CMD_READ_BD_ADDR:
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
            self.event_code == self.EVENT_CODE
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
            self.event_code == self.EVENT_CODE
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
            self.event_code == self.EVENT_CODE
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
            self.event_code == self.EVENT_CODE
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
            self.event_code == self.EVENT_CODE
            and self.opcode == HCI_OPCODE.HCI_CMD_LE_READ_LOCAL_SUPPORTED_FEATURES
        ):
            self.le_features.unpack(self.param[4 : 4 + 8])

    def __str__(self):
        return super().__str__() + "\n" + self.le_features.__str__()


class HciEventCommandStatus(HciEvent):
    """
    HCI command Status event
    """
    EVENT_CODE = 0x0F
    def __init__(self):
        super().__init__()
        self.event_code = 0
        self.len = 0x04
        self.status = 0
        self.num_hci_cmd_packets = 0
        self.opcode = 0

    def unpack(self, data: bytes):
        """
        convert from bytes
        """
        super().unpack(data)
        if self.event_code == self.EVENT_CODE:
            self.status, self.num_hci_cmd_packets, self.opcode = struct.unpack(
                "<BHB", self.param[:4]
            )

    def __str__(self):
        return f"hci event code: 0x{self.event_code:02X}, len: {self.len}, status: 0x{self.status:02X}, num_hci_cmd_packets: {self.num_hci_cmd_packets}, opcode: 0x{self.opcode:04X}"


class HciEventLeMeta(HciEvent):
    """
    HCI LE meta event
    """
    EVENT_CODE = 0x3E
    def __init__(self):
        super().__init__()
        self.event_code = self.EVENT_CODE
        self.len = 0x04
        self.subevent_code = 0

    def unpack(self, data: bytes):
        """
        convert from bytes
        """
        super().unpack(data)
        if self.event_code == self.EVENT_CODE:
            self.subevent_code = self.param[0]

    def __str__(self):
        return f"hci event code: 0x{self.event_code:02X} HCI_LE_Meta_Event, len: {self.len}, subevent_code: 0x{self.subevent_code:02X}"


class HciEventLeConnectionComplete(HciEventLeMeta):
    """
    HCI LE connection complete event
    """
    SUBEVENT_CODE = 0x01
    def __init__(self):
        super().__init__()
        self.subevent_code = 0
        self.status = 0
        self.connection_handle = 0
        self.role = 0
        self.adv_address_type = 0
        self.peer_bd_addr = bytes()
        self.connection_interval = 0
        self.max_latency = 0
        self.supervision_timeout = 0
        self.central_clock_accuracy = 0

    def unpack(self, data: bytes):
        """
        convert from bytes
        """
        super().unpack(data)
        if self.event_code == self.EVENT_CODE and self.subevent_code == self.SUBEVENT_CODE:
            _format = "<BHBB6sHHHB"
            _offset = 1
            _len = struct.calcsize(_format)
            self.status, self.connection_handle, self.role, self.adv_address_type, self.peer_bd_addr, self.connection_interval, self.max_latency, self.supervision_timeout, self.central_clock_accuracy = struct.unpack(_format, self.param[_offset:_offset+_len])

    def __str__(self):
        return super().__str__() + f" HCI_LE_Connection_Complete, status: {StatusType(self.status).name}, connection_handle: 0x{self.connection_handle:04X}, role: {RoleType(self.role).name}, adv_address_type: {AddressType(self.adv_address_type).name}, peer_bd_addr: {address_to_str(self.peer_bd_addr)}, connection_interval: {self.connection_interval*1.25} ms, max_latency: {self.max_latency} events, supervision_timeout: {self.supervision_timeout} ms, central_clock_accuracy: {self.central_clock_accuracy} ppm"

class HciEventLeConnectionUpdateComplete(HciEventLeMeta):
    """
    HCI LE connection update complete event
    """
    SUBEVENT_CODE = 0x03
    def __init__(self):
        super().__init__()
        self.subevent_code = 0
        self.status = 0
        self.connection_handle = 0
        self.connection_interval = 0
        self.max_latency = 0
        self.supervision_timeout = 0

    def unpack(self, data: bytes):
        """
        convert from bytes
        """
        super().unpack(data)
        if self.event_code == self.EVENT_CODE and self.subevent_code == self.SUBEVENT_CODE:
            _format = "<BHHHH"
            _offset = 1
            _len = struct.calcsize(_format)
            self.status, self.connection_handle, self.connection_interval, self.max_latency, self.supervision_timeout = struct.unpack(_format, self.param[_offset:_offset+_len])

    def __str__(self):
        return super().__str__() + f" HCI_LE_Connection_Update_Complete, status: {StatusType(self.status).name}, connection_handle: 0x{self.connection_handle:04X}, connection_interval: {self.connection_interval*1.25} ms, max_latency: {self.max_latency} events, supervision_timeout: {self.supervision_timeout} ms"

