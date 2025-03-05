import threading

class Path_Register:
    # 使用 class-level 變數儲存路徑與檔案大小資料
    _path_table = {}         # type: dict[int, str]
    _file_size_table = {}    # type: dict[int, int]
    _timestamp_list = []     # type: list[int]
    _lock = threading.Lock() # 共用鎖

    @staticmethod
    def register_path(timestamp: int, file_size: int, path: str):
        with Path_Register._lock:
            if timestamp in Path_Register._path_table:
                del Path_Register._path_table[timestamp]
                del Path_Register._file_size_table[timestamp]
                Path_Register._timestamp_list.remove(timestamp)
            Path_Register._path_table[timestamp] = path
            Path_Register._file_size_table[timestamp] = file_size
            Path_Register._timestamp_list.append(timestamp)
            if len(Path_Register._timestamp_list) > 100:
                oldest_timestamp = Path_Register._timestamp_list.pop(0)
                del Path_Register._path_table[oldest_timestamp]
                del Path_Register._file_size_table[oldest_timestamp]

    @staticmethod
    def get_path(timestamp: int) -> str:
        with Path_Register._lock:
            return Path_Register._path_table.get(timestamp, None)

    @staticmethod
    def get_file_size(timestamp: int) -> int:
        with Path_Register._lock:
            return Path_Register._file_size_table.get(timestamp, None)
