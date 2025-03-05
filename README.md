# CIoT-Bot-Collector

##系統功能
程式利用UDP方式進行傳輸，利用CIoT_udp_data_sender.py傳送資料，CIoT_udp_receiving_server.py接收資料。

## 執行步驟
1. cd CIoI-UDP-Data-Collector

2. python CIoT_udp_receiving_server.py

## Customizing setting.json

1. "packet_length":資料長度
   
2. "timeout":等待封包回傳時間,
  
3. "maximum_image_size": sender端存放檔案最大數量
  
4. "image_save_path" : server端傳輸完成資料存放位置
