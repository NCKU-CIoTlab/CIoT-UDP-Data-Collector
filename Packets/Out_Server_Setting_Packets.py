from Packets.Packets_Base import Packets_Base
from Packets.Packets_Index import Packets_Index

class ServerSettingPacket(Packets_Base):
    def __init__(self, package_data: bytes):
        super().__init__(package_data)
        # 請求封包無額外資料，因此不需解析其他欄位

    def handle(self, host):
        print("Response Server Setting.")
        package_length = host.get_packet_length()
        timeout = host.get_timeout()
        maximum_stacksize = host.get_maximum_stacksize()
        image_save_path = host.get_image_save_path()  # 新增：取得圖片存放路徑
        print('server setting done')
        # 產生回應封包物件，並傳入 image_save_path
        return ServerSettingResponse(self.index, package_length, timeout, maximum_stacksize, image_save_path)


class ServerSettingResponse(Packets_Base):
    def __init__(self, index: int, package_length: int, timeout: int, maximum_stacksize: int, image_save_path: str):
        # 將數值轉換成固定長度的 bytes (little-endian)
        data = package_length.to_bytes(4, byteorder='little')
        data += timeout.to_bytes(2, byteorder='little')
        data += maximum_stacksize.to_bytes(2, byteorder='little')
        
        # 將 image_save_path 字串轉為 UTF-8 bytes，並先傳送其長度（4 bytes）
        path_bytes = image_save_path.encode('utf8')
        path_len = len(path_bytes)
        data += path_len.to_bytes(4, byteorder='little')
        data += path_bytes
        
        # 封裝封包
        packet_data = self.encode_data(index, Packets_Index.Server_Setting.value, data)
        super().__init__(packet_data)
