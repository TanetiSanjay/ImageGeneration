import pickle
import socket
import time
import os
from PIL import Image, ImageTk
import tkinter as tk

SIZE = 1024
FORMAT = "utf-8"
IMAGE_FORMAT = "latin-1"


class ClientGUI:
    def __init__(self, master):

        self.master = master
        self.master.title("Image Generator Client")
        self.master.geometry("800x800")

        self.ip_label = tk.Label(self.master, text="Enter IP of server: ")
        self.ip_label.grid(row=0, column=0, padx=10, pady=10)

        self.ip_entry = tk.Entry(self.master, width=50)
        self.ip_entry.grid(row=0, column=1, padx=10, pady=10)

        self.port_label = tk.Label(self.master, text="Enter PORT: ")
        self.port_label.grid(row=1, column=0, padx=10, pady=10)

        self.port_entry = tk.Entry(self.master, width=50)
        self.port_entry.grid(row=1, column=1, padx=10, pady=10)

        self.prompt_label = tk.Label(self.master, text="Enter your Prompt: ")
        self.prompt_label.grid(row=2, column=0, padx=10, pady=10)

        self.prompt_entry = tk.Entry(self.master, width=50)
        self.prompt_entry.grid(row=2, column=1, padx=10, pady=10)

        self.generate_button = tk.Button(self.master, text="Generate Image", command=self.generate_image)
        self.generate_button.grid(row=3, column=1, padx=10, pady=10)

        self.image_label = tk.Label(self.master)
        self.image_label.grid(row=4, column=1, padx=0, pady=0)

    def generate_image(self):
        prompt = self.prompt_entry.get()
        ip = self.ip_entry.get()
        port = self.port_entry.get()

        if prompt:
            client_obj = Client(ip, int(port), prompt, 1)
            file_path = client_obj.client_connection()

            if os.path.exists(file_path):
                img = Image.open(file_path)
                img_tk = ImageTk.PhotoImage(img)
                self.image_label.config(image=img_tk)
                self.image_label.image = img_tk


class Client:
    def __init__(self, ip, port, prompt, count):
        self.ip = ip
        self.port = port
        self.prompt = prompt
        self.count = count
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def client_connection(self):
        time.sleep(1)
        self.client.connect((self.ip, self.port))
        print(f"[-] {socket.gethostbyname(socket.gethostname())} has connected to the server.")

        try:
            position = self.client.recv(SIZE).decode(FORMAT)
            print(f'[*] Message from server: {position}')

            prompt_count = f"{self.prompt}:{self.count}"
            self.client.send(prompt_count.encode(FORMAT))

            file_names = self.client.recv(SIZE)
            file_dir = pickle.loads(file_names)
            print(file_dir)
            file_extension = '.png'
            new_file = []

            for file in file_dir:
                if os.path.exists(file):
                    i = 0
                    while os.path.exists(file):
                        i += 1
                        file = f'{file.strip(file_extension)}_{i}.png'

                print(f'[-] Receiving files...')
                file_size = int(self.client.recv(SIZE).decode(FORMAT))
                print(file_size)

                with open(f'{os.path.basename(file)}', 'wb') as f:
                    recv_data = 0
                    while recv_data < file_size:
                        data = self.client.recv(SIZE)
                        if not data:
                            break
                        f.write(data)
                        recv_data += len(data)
                    f.close()

                print(f'[-] {file} was received successfully')
                time.sleep(0.5)
                new_file.append(file)

            self.client.close()
            print(f"[-] Disconnected from the server")

            return new_file[0]

        except ConnectionResetError:
            print("[-] Server has shut downed or Server is not started yet")


if __name__ == '__main__':
    root = tk.Tk()
    client_gui_obj = ClientGUI(root)
    root.mainloop()
