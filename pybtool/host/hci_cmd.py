import struct
import json
from ctypes import *
from .hci_def import *

# class HciCmd:
#     """
#     HCI command
#     """

#     def __init__(self):
#         """
#         HCI command
#         |OpFode(OCF|OGF)|Parameter Total Length|Parameter|
#         """
#         self.pkt_type = 0x01
#         self.opcode = 0
#         self.len = 0
#         self.param = bytes()

#     def pack(self):
#         """
#         convert to bytes
#         """
#         self.len = len(self.param)
#         return struct.pack("<HB", self.opcode, self.len) + self.param

#     def __str__(self):
#         return f"hci cmd opcode: 0x{self.opcode:04X}, len: {self.len}, param: {self.param.hex()}"


class HciCmdBase(HStructure):
    """
    HCI command
    |OpFode(OCF|OGF)|Parameter Total Length|Parameter|
    """

    def __init__(self):
        super().__init__()
        self.opcode = 0
        self.length = 0

    def pack(self):
        self.length = sizeof(self) - 3
        return string_at(addressof(self), sizeof(self))

    def __str__(self):
        try:
            opcode_name = HCI_OPCODE(self.opcode).name
        except ValueError:
            opcode_name = "UNKNOWN"
        return (
            f"hci cmd opcode: {opcode_name} (0x{self.opcode:04X}), len: {self.length}"
        )


class HciCmd(HciCmdBase):
    """
    HCI command
    |OpFode(OCF|OGF)|Parameter Total Length|Parameter|
    """

    _fields_ = [
        ("opcode", c_uint16),
        ("length", c_uint8),
    ]


class HciCmdReset(HciCmd):
    """
    HCI reset command
    """

    def __init__(self):
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_RESET


class HciCmdReadLocalName(HciCmd):
    """
    HCI read local name command
    """

    def __init__(self):
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_READ_LOCAL_NAME


class HciCmdReadBdAddr(HciCmd):
    """
    HCI read bd addr command
    """

    def __init__(self):
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_READ_BD_ADDR


class EventMaskStruct(Structure):
    _fields_ = [
        ("inquiry_complete_event", c_uint64, 1),
        ("inquiry_result_event", c_uint64, 1),
        ("connection_complete_event", c_uint64, 1),
        ("connection_request_event", c_uint64, 1),
        ("disconnection_complete_event", c_uint64, 1),
        ("authentication_complete_event", c_uint64, 1),
        ("remote_name_request_event", c_uint64, 1),
        ("remote_name_request_complete_event", c_uint64, 1),
        ("link_key_request_event", c_uint64, 1),
        ("link_key_notification_event", c_uint64, 1),
    ]


class EventMaskUnion(Union):
    _fields_ = [("w", c_uint64), ("b", EventMaskStruct)]


class HciCmdSetEventMask(HciCmdBase):
    """
    HCI set event mask command
    """

    _fields_ = HciCmd._fields_ + [
        ("event_mask", EventMaskUnion),
    ]

    def __init__(self, **kwargs):
        super().__init__()
        # for field in self._fields_:
        #     setattr(self, field[0], 0)  # default set off
        # for key, value in kwargs.items():
        #     if hasattr(self, key):
        #         setattr(self, key, value)
        self.opcode = HCI_OPCODE.HCI_CMD_SET_EVENT_MASK
        self.event_mask.w = 0x3FFFFFFFFFFFFFFF
        self.event_mask.b.inquiry_complete_event = 0

    def __str__(self):
        return super().__str__() + f", event_mask: 0x{self.event_mask.w:016X}"


class HciCmdReadBufferSize(HciCmd):
    """
    HCI read buffer size command
    """

    def __init__(self):
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_READ_BUFFER_SIZE


class HciCmdReadLocalVersionInfo(HciCmd):
    """
    HCI read local version info command
    """

    def __init__(self):
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_READ_LOCAL_VERSION_INFO


class HciCmdReadLocalSupportedCommands(HciCmd):
    """
    HCI read local supported commands command
    """

    def __init__(self):
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_READ_LOCAL_SUPPORTED_COMMANDS


class HciCmdReadLocalSupportedFeatures(HciCmd):
    """
    HCI read local supported features command
    """

    def __init__(self):
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_READ_LOCAL_SUPPORTED_FEATURES


class HciCmdReadLocalSupportedCodecs(HciCmd):
    """
    HCI read local supported codecs command
    """

    def __init__(self):
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_READ_LOCAL_SUPPORTED_CODECS


class HciCmdLeReadlocalSupportedFeaturesPage0(HciCmd):
    """
    HCI LE read local supported features page0 command
    """

    def __init__(self):
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_LE_READ_LOCAL_SUPPORTED_FEATURES
