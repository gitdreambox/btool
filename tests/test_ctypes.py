import unittest
import json
from ctypes import *


class PStructure(Structure):
    _pack_ = 1
    _fields_ = []

    def pack(self):
        return string_at(addressof(self), sizeof(self))

    def unpack(self, buf):
        obj = self
        memmove(addressof(obj), buf, sizeof(obj))
        return obj

    def __to_dict(self, obj):
        d = dict((field[0], getattr(obj, field[0])) for field in obj._fields_)
        for field in d:
            att = d[field]
            if isinstance(att, int):
                pass
            elif isinstance(att, bytes):
                d[field] = bytes.decode(d[field], encoding="utf-8", errors="ignore")
            elif isinstance(att, Array):
                if att._type_ is c_ubyte:
                    d[field] = "".join([f"{x:02x}" for x in d[field]])
                else:
                    d[field] = [self.__to_dict(a) for a in att]
            else:
                d[field] = self.__to_dict(att)
        return d

    def __post_process(self, d):
        return d

    def __str__(self):
        return json.dumps(self.__post_process(self.__to_dict(self)), indent=4)


class EventMask(PStructure):
    _fields_ = [
        ("inquiry_complete_event", c_uint32, 1),
        ("connection_complete_event", c_uint32, 1),
        ("connection_request_event", c_uint32, 1),
        ("disconnection_complete_event", c_uint32, 1),
    ]

    def __init__(self):
        super().__init__()
        for (
            field,
            _,
            _,
        ) in self._fields_:
            setattr(self, field, 0)  # default set all off
        self.inquiry_complete_event = 1  # default set on


class TestEventMask(unittest.TestCase):
    def test_event_mask(self):
        mask = EventMask()
        mask.connection_complete_event = 1
        data = mask.pack()
        print(data, type(data))
        print(mask)


if __name__ == "__main__":
    unittest.main()
