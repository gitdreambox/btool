import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import signal
import time
from datetime import datetime
import logging
import logging.config
import yaml
import argparse
import host


logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    logger.info('\nCtrl+C pressed. Exiting...')
    sys.exit(0)

def setup_logging():
    # Load logging configuration
    with open(os.path.join(os.path.dirname(__file__), 'log_config.yaml'), 'r') as f:
        config = yaml.safe_load(f.read())
        # 创建logs目录（如果不存在）
        logs_dir = os.path.join(os.path.dirname(__file__), '../logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # 设置日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(logs_dir, f'app_{timestamp}.log')
        config['handlers']['file']['filename'] = log_file

        logging.config.dictConfig(config)

def main():
    setup_logging()

    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="bluetooth tool")
    parser.add_argument("-s", "--scan", action="store_true", help="start ble scan")
    parser.add_argument(
        "-t",
        "--transport",
        choices=["usb", "uart"],
        default="usb",
        help="select transport type [usb|uart]",
    )
    parser.add_argument("-d", "--device", type=int, help="select device index")
    args = parser.parse_args()

    if args.scan:
        logger.info("ble scan")
    else:
        parser.print_help()

    hci = host.HCI(args.transport)
    
    devices = hci.list_devices()
    if len(devices) == 0:
        logger.warning("no device")
    else:
        if len(devices) == 1:
            d = devices[0]
        elif args.device is not None:
            d = devices[args.device]
        else:
            for i, d in enumerate(devices):
                logger.info(f"{i} {d}")
            i = input("select device:")
            if i.isdigit():
                i = int(i)
                if i >= 0 and i < len(devices):
                    d = devices[i]
                else:
                    logger.error("invalid device")
                    return
        hci.open(d)
        logger.info(f"hci open {hci.name}")
        l2cap = host.L2CAP(hci)
        att = host.ATT(l2cap)
        try:
            hci.init()
            
            hcicmd = host.hci_cmd.HciCmdLeSetAdvertisingParameters()
            logger.info(hcicmd)
            hcievt = host.hci_evt.HciEventCommandComplete()
            hcievt = hci.send_command(hcicmd, hcievt)
            logger.info(hcievt)

            hcicmd = host.hci_cmd.HciCmdLeSetAdvertisingData()
            logger.info(hcicmd)
            hcievt = host.hci_evt.HciEventCommandComplete()
            hcievt = hci.send_command(hcicmd, hcievt)
            logger.info(hcievt)

            hcicmd = host.hci_cmd.HciCmdLeSetAdvertisingEnable()
            logger.info(hcicmd)
            hcievt = host.hci_evt.HciEventCommandComplete()
            hcievt = hci.send_command(hcicmd, hcievt)
            logger.info(hcievt)

            logger.info("btool running, Press Ctrl+C to exit...")
            while True:
                time.sleep(1)

        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            logger.info("Closing HCI connection...")
            hci.close()


if __name__ == "__main__":
    main()
