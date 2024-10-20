import struct
import json
from enum import IntEnum
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


class HciCmdLeReadFilterAcceptListSize(HciCmd):
    """
    HCI LE read local supported features page0 command
    """

    def __init__(self):
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_LE_READ_WHITE_LIST_SIZE


class LeEventMaskStruct(Structure):
    _fields_ = [
        ("LeReadLocalP256PublicKeyCompleteevent", c_uint8, 1),
    ]


class LeEventMaskUnion(Union):
    _fields_ = [("B", c_uint8 * 8), ("b", LeEventMaskStruct)]


class HciCmdLeSetEventMask(HciCmdBase):
    """
    HCI LE set event mask command
    """

    _fields_ = HciCmd._fields_ + [
        ("le_event_mask", LeEventMaskUnion),
    ]

    def __init__(self, **kwargs):
        super().__init__()
        # for field in self._fields_:
        #     setattr(self, field[0], 0)  # default set off
        # for key, value in kwargs.items():
        #     if hasattr(self, key):
        #         setattr(self, key, value)
        self.opcode = HCI_OPCODE.HCI_CMD_LE_SET_EVENT_MASK
        self.le_event_mask.B = (c_uint8 * 8)(
            0xFF, 0xFD, 0xFF, 0xFF, 0x07, 0x00, 0x00, 0x00
        )
        self.le_event_mask.b.LeReadLocalP256PublicKeyCompleteevent = 1

    def __str__(self):
        return (
            super().__str__() + f", le_event_mask: {bytes(self.le_event_mask.B).hex()}"
        )


class AdvertisingChannelMapStruct(Structure):
    _fields_ = [
        ("ch37", c_uint8, 1),
        ("ch38", c_uint8, 1),
        ("ch39", c_uint8, 1),
    ]


class HciCmdLeSetAdvertisingParameters(HciCmdBase):
    """
    LE Set Advertising Parameters command
    """

    _fields_ = HciCmd._fields_ + [
        ("Advertising_Interval_Min", c_uint16),
        ("Advertising_Interval_Max", c_uint16),
        ("Advertising_Type", c_uint8),
        ("Own_Address_Type", c_uint8),
        ("Peer_Address_Type", c_uint8),
        ("Peer_Address", c_uint8 * 6),
        ("Advertising_Channel_Map", c_uint8),
        ("Advertising_Filter_Policy", c_uint8),
    ]

    def __init__(
        self,
        Advertising_Interval_Min: int = 0x30,
        Advertising_Interval_Max: int = 0x30,
        Advertising_Type: AdvertisingType = AdvertisingType.ADV_IND,
        Own_Address_Type: AddressType = AddressType.PublicDeviceAddress,
        Peer_Address_Type: AddressType = AddressType.PublicDeviceAddress,
        Peer_Address: bytes = b"\x00\x00\x00\x00\x00\x00",
        Advertising_Channel_Map: int = 0x07,
        Advertising_Filter_Policy: int = 0,
    ):
        """
        Advertising_Interval_Min:
            Minimum advertising interval for undirected and low duty cycle directed advertising.
            Range: 0x0020 to 0x4000
            Default: 0x0800 (1.28 s)
            Time = N × 0.625 ms
            Time Range: 20 ms to 10.24 s

        Advertising_Interval_Max:
            Maximum advertising interval for undirected and low duty cycle directed advertising.
            Range: 0x0020 to 0x4000
            Default: 0x0800 (1.28 s)
            Time = N × 0.625 ms
            Time Range: 20 ms to 10.24 s

        Advertising_Type:
            0x00:Connectable and scannable undirected advertising (ADV_IND) (default)
            0x01:Connectable high duty cycle directed advertising(ADV_DIRECT_IND, high duty cycle)
            0x02:Scannable undirected advertising (ADV_SCAN_IND)
            0x03:Non connectable undirected advertising (ADV_NONCONN_IND)
            0x04:Connectable low duty cycle directed advertising(ADV_DIRECT_IND, low duty cycle)

        Own_Address_Type:
            0x00:Public Device Address (default)
            0x01:Random Device Address
            0x02:Controller generates Resolvable Private Address based on the local IRK from the resolving list. If the resolving list contains no matching entry, use the public address.
            0x03:Controller generates Resolvable Private Address based on the local IRK from the resolving list. If the resolving list contains no matching entry, use the random address from LE_Set_Random_Address.

        Peer_Address:
            0x00:Public Device Address (default) or Public Identity Address
            0x01:Random Device Address or Random (static) Identity Address

        Advertising_Channel_Map:
            bit0:Channel 37 shall be used
            bit1:Channel 38 shall be used
            bit2:Channel 39 shall be used

        Advertising_Filter_Policy:
            0x00:Process scan and connection requests from all devices (i.e., the Filter Accept List is not in use) (default).
            0x01:Process connection requests from all devices and scan requests only from devices that are in the Filter Accept List.
            0x02:Process scan requests from all devices and connection requests only from devices that are in the Filter Accept List.
            0x03:Process scan and connection requests only from devices in the Filter Accept List.
        """
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_LE_SET_ADVERTISING_PARAMETERS
        if Advertising_Interval_Min < 0x0020 or Advertising_Interval_Min > 0x4000:
            raise ValueError("Advertising_Interval_Min 0x0020 to 0x4000")
        if Advertising_Interval_Max < 0x0020 or Advertising_Interval_Max > 0x4000:
            raise ValueError("Advertising_Interval_Max 0x0020 to 0x4000")
        self.Advertising_Interval_Min = Advertising_Interval_Min
        self.Advertising_Interval_Max = Advertising_Interval_Max
        self.Advertising_Type = Advertising_Type
        self.Own_Address_Type = Own_Address_Type
        self.Peer_Address_Type = Peer_Address_Type
        self.Peer_Address = (c_uint8 * 6)(*Peer_Address)
        self.Advertising_Channel_Map = Advertising_Channel_Map
        self.Advertising_Filter_Policy = Advertising_Filter_Policy

    def __str__(self):
        addr = ":".join([f"{a:02X}" for a in self.Peer_Address])
        return (
            super().__str__()
            + f", Advertising_Interval_Min: 0x{self.Advertising_Interval_Min:04X}"
            + f", Advertising_Interval_Max: 0x{self.Advertising_Interval_Min:04X}"
            + f", Advertising_Type: {AdvertisingType(self.Advertising_Type).name}"
            + f", Own_Address_Type: {AddressType(self.Own_Address_Type).name}"
            + f", Peer_Address_Type: {AddressType(self.Peer_Address_Type).name}"
            + f", Peer_Address: {addr}"
            + f", Advertising_Channel_Map: 0x{self.Advertising_Channel_Map:02X}"
            + f", Advertising_Filter_Policy: {self.Advertising_Filter_Policy}"
        )


class HciCmdLeSetAdvertisingData(HciCmdBase):
    """
    LE Set Advertising data command
    """

    _fields_ = HciCmd._fields_ + [
        ("Advertising_Data_Length", c_uint8),
        ("Advertising_Data", c_uint8 * 31),
    ]

    def __init__(
        self,
        flags: int = 0x02,
        completeLocalName: str = "btool adv test",
        manufacturer: bytes = None,
    ):
        """ """
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_LE_SET_ADVERTISING_DATA
        self.Advertising_Data_Length = 0

        # set flags
        self.Advertising_Data[0] = 0x02
        self.Advertising_Data[1] = 0x01
        self.Advertising_Data[2] = flags
        self.Advertising_Data_Length += 1 + 2

        # set complete Local Name
        if completeLocalName is not None:
            name_bytes = completeLocalName.encode("utf-8")[:26]  # limt name length
            name_length = len(name_bytes)
            self.Advertising_Data[self.Advertising_Data_Length] = name_length + 1
            self.Advertising_Data[self.Advertising_Data_Length + 1] = (
                0x09  # Complete Local Name
            )
            memmove(
                addressof(self.Advertising_Data) + self.Advertising_Data_Length + 2,
                name_bytes,
                name_length,
            )
            self.Advertising_Data_Length += name_length + 2

        # set manufacturer
        if manufacturer is not None:
            manu_length = len(manufacturer)
            if self.Advertising_Data_Length + manu_length + 2 <= 31:
                self.Advertising_Data[self.Advertising_Data_Length] = manu_length + 1
                self.Advertising_Data[self.Advertising_Data_Length + 1] = (
                    0xFF  # Manufacturer Specific Data
                )
                memmove(
                    addressof(self.Advertising_Data) + self.Advertising_Data_Length + 2,
                    manufacturer,
                    manu_length,
                )
                self.Advertising_Data_Length += manu_length + 2

    def pack(self):
        self.length = sizeof(self) - 3
        return string_at(addressof(self), sizeof(self))

    def __str__(self):
        return (
            super().__str__()
            + f", Advertising_Data: {bytes(self.Advertising_Data).hex()}"
        )


class HciCmdLeSetScanParameters(HciCmdBase):
    """
    LE Set Advertising data command
    """

    _fields_ = HciCmd._fields_ + [
        ("LE_Scan_Type", c_uint8),
        ("LE_Scan_Interval", c_uint16),
        ("LE_Scan_Window", c_uint16),
        ("Own_Address_Type", c_uint8),
        ("Scanning_Filter_Policy", c_uint8),
    ]

    def __init__(self):
        """ """
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_LE_SET_SCAN_PARAMETERS
        self.LE_Scan_Type = 0x01
        self.LE_Scan_Interval = 0x01E0
        self.LE_Scan_Window = 0x0030
        self.Own_Address_Type = 0x01
        self.Scanning_Filter_Policy = 0x00

    def __str__(self):
        return super().__str__() + f", LE_Scan_Type: {self.LE_Scan_Type}"


class HciCmdLeSetAdvertisingEnable(HciCmdBase):
    """
    LE Set Advertising data command
    """

    _fields_ = HciCmd._fields_ + [
        ("enable", c_uint8),
    ]

    def __init__(
        self,
        enable: bool = True,
    ):
        """ """
        super().__init__()
        self.opcode = HCI_OPCODE.HCI_CMD_LE_SET_ADVERTISING_ENABLE
        self.enable = 1 if enable else 0

    def __str__(self):
        return super().__str__() + f", enable: {self.enable}"


class HciCmdLeSetHostFeatrue(HciCmdBase):
    """
    LE Set Advertising data command
    """

    _fields_ = HciCmd._fields_ + [
        ("enable", c_uint16),
    ]

    def __init__(
        self,
    ):
        """ """
        super().__init__()
        self.opcode = 0x2074
        self.enable = 0x0120

    def __str__(self):
        return super().__str__() + f", enable: {self.enable}"
