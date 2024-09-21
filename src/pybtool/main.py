import argparse

def main():
    parser = argparse.ArgumentParser(description="bluetooth tool")
    parser.add_argument("-s", "--scan", action="store_true", help="start ble scan")
    args = parser.parse_args()

    if args.scan:
        print("ble scan")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()