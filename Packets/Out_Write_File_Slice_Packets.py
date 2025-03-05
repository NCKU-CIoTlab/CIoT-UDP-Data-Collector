from Packets.Packets_Base import Packets_Base
from Packets.Packets_Index import Packets_Index
from File_Helper.Path_Register import Path_Register
from File_Helper.File_Writter import File_Writter
import syslog


class WriteFileSlicePacket(Packets_Base):
    def __init__(self, package_data: bytes):
        super().__init__(package_data)
        
        # 解析 Timestamp (8 bytes, little-endian)
        self.timestamp = int.from_bytes(self.data[0:8], byteorder='little')
        
        # 解析 Data_Length (4 bytes, little-endian)
        self.data_length = int.from_bytes(self.data[8:12], byteorder='little')
        
        # 剩下的 Data_Length bytes 為要寫入的資料
        self.write_data = self.data[12:12 + self.data_length]
    
    def handle(self, host):
        # 根據 Timestamp 從路徑登錄中取得對應檔案路徑
        path = Path_Register.get_path(self.timestamp)
        
        if path is None:
            # 若找不到對應路徑，回傳 Reset 封包 (CMD 設為 0xff, 空資料)
            return Packets_Base(index=self.index, cmd=0xff, data=b"")
        
        # 呼叫檔案寫入工具將寫入資料寫入檔案，並取得最新的總檔案長度
        total_length = File_Writter.write_file(path, self.write_data)
        
        print(f"Write: {self.data_length}, Total: {total_length}")
        
        # 建立並回傳回應封包
        return WriteFileSliceResponse(self.index, self.timestamp, total_length)

class WriteFileSliceResponse(Packets_Base):
    def __init__(self, index: int, timestamp: int, total_length: int):
        # 將 Timestamp (8 bytes) 與 total_length (4 bytes) 轉換為 little-endian 的 bytes
        data = timestamp.to_bytes(8, byteorder='little') + total_length.to_bytes(4, byteorder='little')
        
        # 利用 encode_data 組合完整封包 (此方法定義在 Packets_Base 中)
        packet_data = self.encode_data(index, Packets_Index.Write_File_Slice.value, data)
        
        super().__init__(packet_data)
