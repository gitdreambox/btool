class GATT:
    def __init__(self, att):
        self.att = att

    def discover_services(self):
        # 实现 GATT 服务发现逻辑
        pass

    def read_characteristic(self, char_handle):
        # 实现 GATT 特征值读取逻辑
        pass

    def write_characteristic(self, char_handle, value):
        # 实现 GATT 特征值写入逻辑
        pass