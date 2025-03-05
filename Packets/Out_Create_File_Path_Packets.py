from Packets.Packets_Base import Packets_Base
from Packets.Packets_Index import Packets_Index
from File_Helper.Path_Register import Path_Register
import os

class CreateFilePathPacket(Packets_Base):
    def __init__(self, package_data: bytes):
        super().__init__(package_data)
        
        # 解析 Timestamp (8 bytes, little-endian)
        self.timestamp = int.from_bytes(self.data[0:8], byteorder='little')
        
        # 解析 Data_Length (4 bytes, little-endian)
        self.data_length = int.from_bytes(self.data[8:12], byteorder='little')
        
        # 解析 Path_Length (2 bytes, little-endian)
        self.path_length = int.from_bytes(self.data[12:14], byteorder='little')
        
        # 解析 Path 字串 (以 UTF-8 解碼)
        self.path = self.data[14:14+self.path_length].decode('utf-8')
    
    def handle(self, host):
        
        # 註冊檔案路徑與相關資訊
        Path_Register.register_path(self.timestamp, self.data_length, os.path.join(self.path))
        print(f"Create File Path: {self.path}, Data Size: {self.data_length}")
        
        # 回應封包只需回傳 Timestamp，因此建立回應物件
        return CreateFilePathResponse(self.index, self.timestamp)
        

class CreateFilePathResponse(Packets_Base):
    def __init__(self, index: int, timestamp: int):
        # 將 timestamp 轉換成 8 bytes (little-endian)
        data = timestamp.to_bytes(8, byteorder='little')
        # 利用 encode_data 封裝封包：假設 encode_data(index, cmd, data) 為封包組裝輔助函式
        packet_data = self.encode_data(index, Packets_Index.Create_File_Path.value, data)
        super().__init__(packet_data)
