from Packets.Packets_Base import Packets_Base
from Packets.Packets_Index import Packets_Index
from File_Helper.Path_Register import Path_Register
from File_Helper.File_Writter import File_Writter

class RemoveFileSlicePacket(Packets_Base):
    def __init__(self, package_data: bytes):
        super().__init__(package_data)
        
        self.timestamp = int.from_bytes(self.data[0:8], byteorder='little')
        
        self.data_length = int.from_bytes(self.data[8:12], byteorder='little')
    
    def handle(self, host):
        # 根據 timestamp 取得對應檔案路徑
        path = Path_Register.get_path(self.timestamp)
        if path is None:
            # 若找不到檔案路徑，回傳一個重置封包 (命令碼 0xff, 空資料)
            return Packets_Base(self.index, 0xff, b"")
        print("Rollback image...:", self.data_length)
        # 呼叫檔案工具進行回滾，並取得最新總長度
        total_length = File_Writter.rollback_file(path, self.data_length)
        # 利用構造用物件建立回應封包並回傳
        return RemoveFileSliceResponse(self.index, self.timestamp, total_length)

class RemoveFileSliceResponse(Packets_Base):
    def __init__(self, index: int, timestamp: int, total_length: int):
        # 將 timestamp (8 bytes) 與 total_length (4 bytes) 轉換成 little-endian 格式
        data = timestamp.to_bytes(8, byteorder='little') + total_length.to_bytes(4, byteorder='little')
        # 利用 encode_data 方法產生最終封包資料
        packet_data = self.encode_data(index, Packets_Index.Remove_File_Slice.value, data)
        super().__init__(packet_data)