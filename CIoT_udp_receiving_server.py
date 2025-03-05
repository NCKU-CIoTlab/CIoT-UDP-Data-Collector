import os
from Server import Server
import time
import syslog
import json

def save_config(server):
    config = {
        "packet_length": server.get_packet_length(),
        "timeout": server.get_timeout(),
        "maximum_image_size": server.get_maximum_stacksize(),
        "image_save_path" : server.get_image_save_path()
    }
    with open("setting.json", "w") as f:
        json.dump(config, f, indent=4)

def reload_config(server):
    path = "setting.json"
    if not os.path.exists(path):
        save_config(server)
    with open(path, "r") as f:
        config = json.load(f)
    if "packet_length" in config:
        server.set_packet_length(int(config["packet_length"]))
    if "timeout" in config:
        server.set_timeout(int(config["timeout"]))
    if "maximum_image_size" in config:
        server.set_maximum_stacksize(int(config["maximum_image_size"]))
    if "image_save_path" in config:
        server.set_image_save_path(config["image_save_path"])

class Tutorial:
    @staticmethod
    def send_help():
        print("Commands:")
        print("  /timeout <milliseconds>")
        print("  /length <packet_length>")
        print("  /debug <true/false>")

def main(debug):
    version = "1.0"
    date = "2024/04/06"
    
    server = Server()

    print("Data Collector Server")
    print("Version: " + version)
    print("Date: " + date)
    print("------------------------------------------")
    
    reload_config(server)
    print("Maximum Packet Length: " + str(server.get_packet_length()) + " Bytes")
    print("Timeout: " + str(server.get_timeout()) + " milliseconds")
    print(f'Image Save Path: {server.get_image_save_path()}')
    # print("Maximum client stack size: " + str(server.get_maximum_stacksize()) + " ")  # Deprecated

    server.start_listen()
    
    if debug:
        while True:
            user_input = input()
            if not user_input:
                Tutorial.send_help()
                continue
            if user_input[0] != '/':
                Tutorial.send_help()
                continue
            data = user_input[1:]  # 移除開頭的 '/'
            parts = data.split(" ")
            command = parts[0].lower()

            if command == "timeout":
                try:
                    new_timeout = int(parts[1])
                    server.set_timeout(new_timeout)
                    print("Timeout: " + str(server.get_timeout()) + " milliseconds")
                    save_config(server)
                except Exception:
                    print("Invalid timeout value.")
            elif command == "length":
                try:
                    new_length = int(parts[1])
                    server.set_packet_length(new_length)
                    print("Maximum Packet Length: " + str(server.get_packet_length()) + " Bytes")
                    save_config(server)
                except Exception:
                    print("Invalid packet length value.")
            elif command == "debug":
                try:
                    # 將字串轉成布林值：只有 "true" (忽略大小寫) 為 True，其它為 False
                    new_debug = parts[1].lower() == "true"
                    server.set_debug(new_debug)
                    print("Debug mode: " + str(new_debug))
                except Exception:
                    print("Invalid debug value.")
            else:
                Tutorial.send_help()
    else:
        while True:
            time.sleep(1)

if __name__ == '__main__':
    debug = False
    main(debug)
