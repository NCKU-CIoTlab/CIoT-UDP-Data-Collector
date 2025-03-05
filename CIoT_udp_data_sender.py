from datetime import datetime
import requests
import base64
import time
import os
import socket
import time as time
import shutil
import traceback

Camera_Image_Dir = "/home/Camera_Images/"

File_Amount_Limitation = 500 #Maximum File Amount for Each Camera

Data_Index = 0
Maximum_Data_Length = 0
Timeout = 5000
image_save_path = "/home/large_space/PTH-pig-images/"

Camera_IDs = {}
def Remove_File(file_path):
    try:
        if(not os.path.exists(file_path)):
            return
        os.remove(file_path)
    except:
        print(f'Remove file failed: {file_path}')

def Initialize_Camera_IDs():
    global Camera_IDs
    setting_file_path = '/home/pi/Desktop/Camera_Setting.txt'
    if(not os.path.exists(setting_file_path)):
        print(f'Setting file doesn\'t exists: {setting_file_path}')
        return False
    Camera_IDs = {}
    with open(setting_file_path, 'r') as f:
        for line in f.readlines():
            split = line.replace('\n', '').split(':')
            Camera_IDs[split[0]] = split[1]
            print(f'Camera {split[0]} ID is {split[1]}')
        return True
Initialize_Camera_IDs()

def Modify_File_Permission():
    try:
        os.system("sudo chmod 777 -R /home/")
        return True
    except:
        print(f'Modify permission failed. Date: {round(time.time() * 1000)}')
        return False

def Get_Images():
    #Camera_Name
    #  - File1
    #  - File2
    #  - ...
    #  - FileN
    Modify_File_Permission()
    image_dict = {}
    for dir_name in os.listdir(Camera_Image_Dir):
        dir_result = []
        dir_path = Camera_Image_Dir + dir_name + "/"
        for date_dir in os.listdir(dir_path):
            date_dir_path = dir_path + date_dir + "/images/"
            dir_result = dir_result + [date_dir_path + f for f in os.listdir(date_dir_path) if os.path.isfile(date_dir_path + f)]
        if(len(dir_result) > 0):
            dir_result.sort()
            image_dict[dir_name] = dir_result
    return image_dict

def Clear_Empty_Dirs():
    for dir_name in os.listdir(Camera_Image_Dir):
        dir_path = Camera_Image_Dir + dir_name + "/"
        for date_dir_name in os.listdir(dir_path):
            date_dir = dir_path + date_dir_name + "/"
            date_dir_image_path = date_dir + "images/"
            dir_result = [date_dir_image_path + f for f in os.listdir(date_dir_image_path) if os.path.isfile(date_dir_image_path + f)]
            if(len(dir_result) == 0):
                shutil.rmtree(date_dir)

def Limit_File_Amount():
    images = Get_Images()
    for camera in images:
        while True:
            camera_image_amount = len(images[camera])
            if(camera_image_amount <= File_Amount_Limitation):
                break
            Remove_File(images[camera][0])
            images[camera] = images[camera][1:]
    Clear_Empty_Dirs()

def Get_Current_Milli():
    return round(time.time()*1000)


def Init_Packet(Cmd, Data):
    global Data_Index
    Data_Index = Data_Index + 1
    Data_Index &= 0xff
    data_list = [Data_Index, Cmd]
    i = 0
    for d in Data:
        data_list.append(d)
    CRC = 0
    for d in data_list:
        CRC += d
    CRC &= 0xff
    data_list.append(CRC)
    return bytearray(data_list)


def Send_Data_And_Get_Response(Packet):
    global Data_Index
    global Timeout
    UDP_IP = "140.116.86.242"
    UDP_PORT = 35525
    BUFFER_SIZE = 4096
    while True:
        try:
            Limit_File_Amount()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 建立 UDP socket
            sock.settimeout(Timeout / 1000)
            print(f"[DEBUG] Sending Packet (hex): {len(Packet.hex())}")
            print(f"[DEBUG] Packet Details - Index: {Packet[0]}, CMD: {Packet[1]}, Length: {len(Packet)}")
            sock.sendto(Packet, (UDP_IP, UDP_PORT))
            result, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"[DEBUG] Received Packet (hex): {result.hex()} from {addr}")
            
            # 檢查 Index
            if result[0] != Data_Index:
                print(f"[ERROR] Index Invalid, Expected: {Data_Index}, Got: {result[0]}")
                time.sleep(1)
                continue
            
            # 檢查 CMD
            if Packet[1] != result[1]:
                if result[1] == 0xFF:
                    print("[ERROR] Server sent reset cmd.")
                    Initialize()
                    Data_Index = Data_Index - 1
                    Send_Data_And_Get_Response(Get_File_Path_Packet(None, None, None, None, True))
                    Data_Index = Data_Index - 1
                else:
                    print(f"[ERROR] CMD Invalid, Expected: {Packet[1]}, Got: {result[1]}")
                time.sleep(1)
                continue
            
            # 計算並檢查 CRC
            CRC = 0
            for j in range(len(result) - 1):
                CRC += result[j]
            CRC &= 0xff
            if CRC != result[len(result) - 1]:
                print(f"[ERROR] CRC Invalid, Calculated: {CRC}, Received: {result[len(result) - 1]}")
                print(f"[DEBUG] Full Received Packet (hex): {result.hex()}")
                time.sleep(1)
                continue
            
            print("[DEBUG] Packet validated successfully.")
            break
        except Exception as e:
            print(f"{round(time.time() * 1000)} Socket Exception occurred:")
            print(traceback.format_exc())
            time.sleep(1)
            continue
    return result



def Decode_Data(Row_Data, Offset, Length):
    data = 0
    for i in range(Length):
        data <<= 8
        data |= Row_Data[Offset + Length - i + 1]
    return data


def Encode_Data(data, len):
    final_data = []
    for j in range(len):
        final_data.append(data & 0xff)
        data >>= 8
    return bytearray(final_data)


def Get_File_Path_Packet(milli, file_size, path_len, path, cache):
    global milli_bytes
    global file_size_bytes
    global path_len_bytes
    global path_bytes
    if(not cache):
        milli_bytes = milli
        file_size_bytes = file_size
        path_len_bytes = path_len
        path_bytes = path
    return Init_Packet(1, milli_bytes + file_size_bytes + path_len_bytes + path_bytes)


def Upload_Image(Timestamp, Path, Data):
    path = Path.encode('utf8')
    path_len = len(path)
    total_len = len(Data)
    milli = Encode_Data(Timestamp, 8)
    # 1 = Register Image Path
    Send_Data_And_Get_Response(Get_File_Path_Packet(
        milli, Encode_Data(total_len, 4), Encode_Data(path_len, 2), path, False))
    # 2 = Upload Image
    # [CMD, Timestamp(File_Index;8Bytes), Data_Length(2Bytes), Data]
    global Maximum_Data_Length
    current_index = 0
    while(True):
        upload_len = total_len - current_index
        if(upload_len > Maximum_Data_Length):
            upload_len = Maximum_Data_Length
        #print(f'Sending... {current_index} ~ {current_index + upload_len}')
        result = Send_Data_And_Get_Response(Init_Packet(
            2, milli + Encode_Data(upload_len, 4) + Data[current_index: current_index + upload_len]))
        server_current_img_len = Decode_Data(result, 8, 4)
        if(server_current_img_len != current_index + upload_len):
            if(server_current_img_len < current_index):
                current_index = 0
            rollbck_len = server_current_img_len - current_index
            # Rollback
            print(
                f'Length Check Error, Except: {current_index + upload_len}, Got: {server_current_img_len}, Rolling back...')
            Send_Data_And_Get_Response(Init_Packet(3, milli + Encode_Data(rollbck_len, 4)))
            continue
        current_index += upload_len
        if(current_index == total_len):
            break


def Initialize():
    global Maximum_Data_Length
    global Timeout
    global Data_Index
    global File_Amount_Limitation
    global image_save_path  # 新增一個全局變數來保存圖片儲存路徑

    data = Send_Data_And_Get_Response(Init_Packet(0, []))
    # 從封包中解析前 8 個位元組的設定參數
    Maximum_Data_Length = Decode_Data(data, 0, 4)
    Timeout = Decode_Data(data, 4, 2)
    File_Amount_Limitation = Decode_Data(data, 6, 2)
    
    # 接著從 offset 8 開始解析 image_save_path
    # 假設 image_save_path 前先有一個 2 位元組的長度欄位 (little-endian)
    path_len = Decode_Data(data, 8, 4)
    image_save_path = data[14:14 + path_len].decode('utf-8')
    
    print(Timeout/1000)
    print(f'File Maximum Slice: {Maximum_Data_Length}, Timeout: {Timeout}, Maximum Image Stack Size: {File_Amount_Limitation}')
    print(f'Image Save Path: {image_save_path}')

def Get_File_Bytes(File_Path):
    file_size = -1
    with open(File_Path, 'rb') as f:
        data = f.read()
        while True:
            if(len(data) == file_size):
                break
            file_size = len(data)
            time.sleep(1)
    return data

print('Requeting server data setting...')
# 0=Request setting from server
Initialize()

while True:
    try:
        for Camera_Name in Camera_IDs:
            Camera_ID = Camera_IDs[Camera_Name]
            images = Get_Images()
            if(not (Camera_Name in images)):
                print("not77")
                continue
            images = images[Camera_Name]
            if(len(images) == 0):
                print("not78")
                continue
            image = images[0]
            image_data = Get_File_Bytes(image)
            print(f'Uploading {Camera_Name}(ID: {Camera_ID}) image... {image}')
            print(f'Total Length: {len(image_data)}, Path: {image}')
            Timestamp = round(os.path.getmtime(image) * 1000)
            Upload_Image(int(Timestamp), os.path.join(image_save_path,f'Camera_{Camera_ID}/{Timestamp}.jpg'), image_data)
            Remove_File(image)
            Limit_File_Amount()        
    except:
        print(f'{round(time.time() * 1000)} File Manager Exception occur:')
        print(traceback.format_exc())
    time.sleep(10)
