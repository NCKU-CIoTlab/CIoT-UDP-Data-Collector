import socket
import threading

from Packets.Out_Create_File_Path_Packets import *
from Packets.Out_Remove_File_Slice_Packets import *
from Packets.Out_Server_Setting_Packets import *
from Packets.Out_Write_File_Slice_Packets import *
from Packets.Packets_Index import Packets_Index

class Server:
    def __init__(self):
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.debug = False
        self.package_length = 16384  # 1KB
        self.timeout = 5000         # 5秒（未來可依需求套用於封包處理）
        self.maximum_stacksize = 500  # 500 images
        self.image_save_path = ""
        
    def set_image_save_path(self, path: str):
        self.image_save_path = path
    
    def get_image_save_path(self):
        return self.image_save_path

    def get_packet_length(self):
        return self.package_length

    def get_timeout(self):
        return self.timeout

    def get_maximum_stacksize(self):
        return self.maximum_stacksize

    def set_packet_length(self, length: int):
        self.package_length = length

    def set_timeout(self, timeout: int):
        self.timeout = timeout

    def set_maximum_stacksize(self, maximum_stacksize: int):
        self.maximum_stacksize = maximum_stacksize

    def set_debug(self, debug: bool):
        self.debug = debug

    def start_listen(self):
        """
        Server作為Slave
        Request Bytes Array: [Data_Index, Cmd, Data(Nullable), CRC(2Bytes)]
        若通訊Error，則Server不回覆訊息

        Ack: [Data_Index, CMD, CRC(2Bytes)]
        CRC: Sum(0, Index(CRC) - 1)

        CMDs:
        0. 伺服器設定資料請求: [Index, CMD, CRC](無送出資料)
        Response: [Index, CMD, 每個封包最長長度(4Bytes), 逾時時間(ms;2Bytes), CRC]

        1. 建立檔案路徑: [Index, CMD, Timestamp(File_Index;8Bytes), Path(2Bytes), Data, CRC]
        Response: [Index, CMD, Timestamp, CRC]

        2. 上傳檔案片段: [Index, CMD, Timestamp(File_Index;8Bytes), Data_Length(2Bytes), Data, CRC]
        Response: [Index, CMD, Timestamp, 目前總資料長度(4Bytes), CRC]

        3. 刪除檔案片段: [Index, CMD, Timestamp(File_Index;8Bytes), Data_Length(2Bytes), Data, CRC]
        Response: [Index, CMD, Timestamp, 目前總資料長度(4Bytes), CRC]
        """
        # 封包類型對應表：使用 Packets_Index.value 當作 key
        packages = {
            Packets_Index.Server_Setting.value: ServerSettingPacket,
            Packets_Index.Create_File_Path.value: CreateFilePathPacket,
            Packets_Index.Write_File_Slice.value: WriteFileSlicePacket,
            Packets_Index.Remove_File_Slice.value: RemoveFileSlicePacket,
        }
        print("Server is listening...")
        def listen():
            try:
                # 每次建立新 socket，並於 port 35525 綁定
                self.sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sck.bind(("", 35525)) # 35525
                buffer_size = 2048000
                while True:
                    try:
                        # 接收資料與來源位址
                        data, addr = self.sck.recvfrom(buffer_size)
                        if len(data) < 2:
                            continue
                        # 封包的第二個位元組代表 CMD
                        cmd = data[1]

                        # 取得對應的封包類型
                        packet_class = packages.get(cmd)
                        if packet_class is None:
                            if self.debug:
                                print(f"Unknown packet type: {cmd}")
                            continue
                        # 利用收到的 bytes 建立封包實例
                        instance = packet_class(package_data=data)
                        # 呼叫封包處理方法，傳入目前 Server 物件（可供參考各項設定）
                        response_packet = instance.handle(self)
                        # 若封包處理成功回傳 response_packet，則取得封包完整資料
                        response_data = response_packet.get_package_data() if response_packet is not None else b""
                        self.sck.sendto(response_data, addr)
                    except Exception as ex:
                        if self.debug:
                            print("Invalid Packet:", ex)
            except Exception as e:
                if self.debug:
                    print("Socket initialization error:", e)

        # 以背景執行緒啟動監聽
        threading.Thread(target=listen, daemon=True).start()
        

