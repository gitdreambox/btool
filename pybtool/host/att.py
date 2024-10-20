import logging
import struct
from enum import IntEnum
logger = logging.getLogger(__name__)

class ATT_OPCODE(IntEnum):
    ATT_ERROR_RSP = 0x01
    ATT_EXCHANGE_MTU_REQ = 0x02
    ATT_EXCHANGE_MTU_RSP = 0x03
    ATT_FIND_INFORMATION_REQ = 0x04
    ATT_FIND_INFORMATION_RSP = 0x05
    ATT_FIND_BY_TYPE_VALUE_REQ = 0x06
    ATT_FIND_BY_TYPE_VALUE_RSP = 0x07
    ATT_READ_BY_TYPE_REQ = 0x08
    ATT_READ_BY_TYPE_RSP = 0x09
    ATT_READ_REQ = 0x0A
    ATT_READ_RSP = 0x0B
    ATT_READ_BLOB_REQ = 0x0C
    ATT_READ_BLOB_RSP = 0x0D
    ATT_READ_MULTIPLE_REQ = 0x0E
    ATT_READ_MULTIPLE_RSP = 0x0F
    ATT_READ_BY_GROUP_TYPE_REQ = 0x10
    ATT_READ_BY_GROUP_TYPE_RSP = 0x11
    ATT_READ_MULTIPLE_VARIABLE_REQ = 0x20
    ATT_READ_MULTIPLE_VARIABLE_RSP = 0x21

class ATT:
    def __init__(self, l2cap):
        self.l2cap = l2cap
        self.l2cap.register_att(self.att_handler)

    def att_handler(self, connection_handle, cid, att_data: bytes):
        logger.info("att recv:" + " ".join([hex(i) for i in att_data]))
        opcode  = att_data[0]
        logger.info(f"att opcode:0x{opcode:02X} {ATT_OPCODE(opcode).name}")
        parameters = att_data[1:]
        if opcode == ATT_OPCODE.ATT_READ_BY_GROUP_TYPE_REQ:
            self.read_by_group_type_req(connection_handle, cid, parameters)
        else:
            logger.error(f"att opcode:0x{opcode:02X} {ATT_OPCODE(opcode).name} not supported")

    def read_by_group_type_req(self, connection_handle, cid, param):
        start_handle, end_handle, group_type = struct.unpack('<HHH', param)
        logger.info(f"att read by group type req start_handle:0x{start_handle:04X} end_handle:0x{end_handle:04X} group_type:0x{group_type:04X}")
        self.read_by_group_type_rsp(connection_handle, cid, start_handle, end_handle, group_type)

    def read_by_group_type_rsp(self, connection_handle, cid, start_handle, end_handle, group_type):
        att = bytes([0x01, 0x00, 0x03, 0x00, 0x00, 0x18, 0x04, 0x00, 0x07, 0x00, 0x0F, 0x18, 0x08, 0x00, 0x0A, 0x00, 0x01, 0x18])
        header = struct.pack('<BB', ATT_OPCODE.ATT_READ_BY_GROUP_TYPE_RSP, len(att)//3)
        self.l2cap.send(connection_handle, cid, header + att)