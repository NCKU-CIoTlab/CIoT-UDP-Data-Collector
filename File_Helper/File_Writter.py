import os

class File_Writter:
    @staticmethod
    def write_file(file_path: str, data: bytes) -> int:
        mode = 'ab'
        
        # 檢查檔案是否存在，若不存在則建立目錄並以覆蓋模式寫入
        if not os.path.exists(file_path):
            dir_path = os.path.dirname(file_path)
            os.makedirs(dir_path, exist_ok=True)
            mode = 'wb'
        
        try:
            with open(file_path, mode) as f:
                f.write(data)
                data_length = f.tell()
        except Exception as e:
            raise  # 若有需要，也可以選擇 return -1 或其他錯誤處理方式

        return data_length

    @staticmethod
    def rollback_file(file_path: str, length: int) -> int:
        try:
            if not os.path.exists(file_path):
                return 0
            file_size = os.path.getsize(file_path)
            new_length = file_size - length
            if new_length < 0:
                new_length = 0

            original_data = b''
            if new_length > 0:
                with open(file_path, 'rb') as f:
                    original_data = f.read(new_length)
            os.remove(file_path)
            if new_length > 0:
                with open(file_path, 'wb') as f:
                    f.write(original_data)
            return new_length
        except Exception as ex:
            return 0
