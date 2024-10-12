class ATT:
    def __init__(self, hci_interface):
        self.hci = hci_interface

    def read_by_type(self, handle, uuid):
        # 实现 ATT Read By Type 请求逻辑
        pass

    def write_request(self, handle, value):
        # 实现 ATT Write Request 逻辑
        pass