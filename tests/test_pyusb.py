print("test pyusb")
import os
import usb
import libusb
import usb.backend.libusb1

backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb-1.0.dll")
# for dev in usb.core.find(find_all=True):
#     print(dev)
# dev = usb.core.find(idVendor=0x8087, idProduct=0x0036)
# dev = usb.core.find(idVendor=0x1209, idProduct=0x7301)
dev = usb.core.find(idVendor=0x0A12, idProduct=0x0001)  # CSR8510 A10
# dev = usb.core.find(idVendor=0x0BDA, idProduct=0xC123)  # RealTek wireless dongle
print(dev)

# set the active configuration. With no arguments, the first
# configuration will be the active one
dev.set_configuration()

dev.ctrl_transfer(0x21, 0x00, 0, 0, bytes.fromhex("030c00"))
ret = dev.read(0x81, 64, 100)
sret = " ".join([hex(x) for x in ret])
print(sret)
