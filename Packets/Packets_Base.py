# -*- coding: utf-8 -*-
class Packets_Base:
    def __init__(self, package_data=None, index=None, cmd=None, data=None):
        if package_data is not None:
            # 確保傳入資料為 bytearray
            if not isinstance(package_data, bytearray):
                package_data = bytearray(package_data)
            self.package_data = package_data
            # 計算 CRC (不含最後一個位元組)
            crc_index = len(package_data) - 1
            computed_crc = 0
            for i in range(crc_index):
                computed_crc = (computed_crc + package_data[i]) % 256
            # 檢查 CRC (使用 XOR 判斷是否相等)
            if (package_data[crc_index] ^ computed_crc) != 0:
                raise Exception("CRC ERROR")

            # 解析 Index 與 CMD
            # print(f'package_data[0]: {package_data[0]}, package_data[1]: {package_data[1]}')
            self.index = package_data[0]
            self.cmd = package_data[1]

            # 解析 Data (若有的話)
            data_length = len(package_data) - 3  # 扣除 Index、CMD 與 CRC
            if data_length > 0:
                self.data = package_data[2:2+data_length]
            else:
                self.data = bytearray()
        elif index is not None and cmd is not None and data is not None:
            self.encode_data(index, cmd, data)
        else:
            # 預設建構子，不做任何初始化
            self.index = None
            self.cmd = None
            self.data = None
            self.package_data = None

    def encode_data(self, index, cmd, data):
        self.index = index
        self.cmd = cmd
        self.data = data

        # 初始化封包資料空間，長度 = 3 + 資料長度 (Index, CMD, Data, CRC)
        package_length = 3 + len(data)
        package_data = bytearray(package_length)

        package_data[0] = index
        package_data[1] = cmd

        # CRC 初始值為 Index + CMD
        crc = (index + cmd) % 256
        for i, b in enumerate(data):
            crc = (crc + b) % 256
            package_data[i + 2] = b

        # 將 CRC 放在最後一個位元組
        package_data[len(data) + 2] = crc

        self.package_data = package_data
        return self.package_data

    def get_index(self):
        return self.index

    def get_cmd(self):
        return self.cmd

    def get_data(self):
        return self.data

    def get_package_data(self):
        return self.package_data

    def handle(self, host):
        return None
