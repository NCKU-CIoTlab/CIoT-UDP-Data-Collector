from enum import Enum

class Packets_Index(Enum):
    """
    CMDs:
    
    Server_Setting:
      設定資料請求
      樹梅派傳來: [Index, CMD, CRC]
      Response: [Index, CMD, 每個封包最長長度(4Bytes), 逾時時間(ms;2Bytes), CRC]
    
    Create_File_Path:
      建立檔案路徑
      樹梅派傳來: [Index, CMD, Timestamp(File_Index;8Bytes), Path(2Bytes), Data, CRC]
      Response: [Index, CMD, Timestamp, CRC]
    
    Write_File_Slice:
      上傳檔案片段
      樹梅派傳來: [Index, CMD, Timestamp(File_Index;8Bytes), Data_Length(2Bytes), Data, CRC]
      Response: [Index, CMD, Timestamp, 目前總資料長度(4Bytes), CRC]
    
    Remove_File_Slice:
      刪除檔案片段
      樹梅派傳來: [Index, CMD, Timestamp(File_Index;8Bytes), Data_Length(2Bytes), Data, CRC]
      Response: [Index, CMD, Timestamp, 目前總資料長度(4Bytes), CRC]
    """
    Server_Setting = 0
    Create_File_Path = 1
    Write_File_Slice = 2
    Remove_File_Slice = 3
