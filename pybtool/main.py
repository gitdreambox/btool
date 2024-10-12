import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import argparse
import host

# from pybtool.host import hci, hci_cmd, hci_evt


def main():
    parser = argparse.ArgumentParser(description="bluetooth tool")
    parser.add_argument("-s", "--scan", action="store_true", help="start ble scan")
    parser.add_argument(
        "-t",
        "--transport",
        choices=["usb", "uart"],
        default="usb",
        help="select transport type [usb|uart]",
    )
    # parser.add_argument("-d", "--device", help="select device")
    args = parser.parse_args()

    if args.scan:
        print("ble scan")
    else:
        parser.print_help()

    hci = host.HCI(args.transport)
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
            if i.isdigit():
                i = int(i)
                if i >= 0 and i < len(devices):
                    d = devices[i]
                else:
                    print("invalid device")
                    return
        hci.open(d)
        print(f"hci open {hci.name}")

        hcicmd = host.hci_cmd.HciCmdReset()
        print(hcicmd)
        hcievt = host.hci_evt.HciEventCommandComplete()
        hcievt = hci.send_command(hcicmd, hcievt)
        print(hcievt)

        hcicmd = host.hci_cmd.HciCmdReadLocalName()
        print(hcicmd)
        hcievt = host.hci_evt.HciEventCommandCompleteLocalName()
        hcievt = hci.send_command(hcicmd, hcievt)
        print(hcievt)

        hcicmd = host.hci_cmd.HciCmdReadBdAddr()
        print(hcicmd)
        hcievt = host.hci_evt.HciEventCommandCompleteBdAddr()
        hcievt = hci.send_command(hcicmd, hcievt)
        print(hcievt)

        hcicmd = host.hci_cmd.HciCmdReadBufferSize()
        print(hcicmd)
        hcievt = host.hci_evt.HciEventCommandCompleteBufferSize()
        hcievt = hci.send_command(hcicmd, hcievt)
        print(hcievt)

        hcicmd = host.hci_cmd.HciCmdSetEventMask(inquiry_complete_event=1)
        print(hcicmd)
        hcievt = host.hci_evt.HciEventCommandComplete()
        hcievt = hci.send_command(hcicmd, hcievt)
        print(hcievt)

        hci.close()


if __name__ == "__main__":
    main()
