import logging
import struct
logger = logging.getLogger(__name__)

class L2CAP:
    def __init__(self, hci_interface):
        self.hci = hci_interface
        self.hci.register_acl(self.acl_handler)
        self.att_cb = None

    def acl_handler(self, acl_data: bytes):
        logger.info("l2cap recv acl:" + " ".join([hex(i) for i in acl_data]))
        _connection_handle, total_len, pdu_len, cid  = struct.unpack('<HHHH', acl_data[0:8])
        connection_handle = _connection_handle & 0x0FFF
        broadcast_flag = (_connection_handle & 0xC000) >> 14
        packet_boundary_flag = (_connection_handle & 0x3000) >> 12
        logger.info(f"l2cap connection_handle:0x{connection_handle:04X} total_len:{total_len} pdu_len:{pdu_len} cid:0x{cid:04X} broadcast_flag:{broadcast_flag} packet_boundary_flag:{packet_boundary_flag}")
        payload = acl_data[8:]
        if self.att_cb is not None:
            self.att_cb(connection_handle,cid, payload)

    def register_att(self, cb:callable):
        self.att_cb = cb

    def send(self, connection_handle, cid, data):
        pdu_len = len(data)
        total_len = pdu_len + 4
        data = struct.pack('<HHHH', connection_handle, total_len, pdu_len, cid) + data
        self.hci.send_acl(data)