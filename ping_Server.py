import os
import threading
import time
from ping3 import ping
import customtkinter as ctk
from tkinter import Menu, messagebox

# Hide the console window on Windows
if os.name == 'nt':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

class ServerMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Monitor")

        self.server_ip = ctk.StringVar(value="192.168.16.13")

        # Create menu
        self.create_menu()

        # Server IP Entry
        self.label_ip = ctk.CTkLabel(root, text="Enter Server IP:")
        self.label_ip.pack(pady=5)

        self.entry_ip = ctk.CTkEntry(root, textvariable=self.server_ip, width=200)
        self.entry_ip.pack(pady=5)

        # Start Button
        self.btn_start = ctk.CTkButton(root, text="Start Monitoring", command=self.start_monitoring)
        self.btn_start.pack(pady=10)

        # Status Label
        self.label_status = ctk.CTkLabel(root, text="Click 'Start Monitoring' to begin.")
        self.label_status.pack(pady=10)

        # Countdown Label
        self.label_countdown = ctk.CTkLabel(root, text="")
        self.label_countdown.pack(pady=10)

        # Thread for monitoring
        self.monitor_thread = None
        self.is_monitoring = False

    def create_menu(self):
        menu_bar = Menu(self.root)
        
        # Appearance Mode Menu
        appearance_menu = Menu(menu_bar, tearoff=0)
        appearance_menu.add_command(label="Light Mode", command=lambda: self.change_mode("light"))
        appearance_menu.add_command(label="Dark Mode", command=lambda: self.change_mode("dark"))
        
        # Adding menus to the menu bar
        menu_bar.add_cascade(label="⚙️", menu=appearance_menu)
        self.root.config(menu=menu_bar)

    def change_mode(self, mode):
        ctk.set_appearance_mode(mode)

    def start_monitoring(self):
        if self.is_monitoring:
            return

        self.server_ip = self.entry_ip.get()
        self.label_status.configure(text=f"Monitoring server {self.server_ip}...")
        self.btn_start.configure(state=ctk.DISABLED)

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_server, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)

    def monitor_server(self):
        while self.is_monitoring:
            try:
                response = ping(self.server_ip)

                if response is not None:
                    # Server is reachable
                    self.label_status.configure(text=f"Server {self.server_ip} is reachable.")
                    self.show_notification("Server Status", f"Server {self.server_ip} is now reachable!")
                else:
                    # Server is not reachable
                    self.label_status.configure(text=f"Server {self.server_ip} is down!")

                countdown_seconds = 300  # 5 minutes
                for i in range(countdown_seconds, 0, -1):
                    if not self.is_monitoring:
                        break
                    self.label_countdown.configure(text=f"Next check in {i} seconds...")
                    time.sleep(1)

                self.label_countdown.configure(text="")
            except Exception as e:
                print(f"Error: {e}")
                self.is_monitoring = False
                break

        self.btn_start.configure(state=ctk.NORMAL)
        self.label_status.configure(text="Click 'Start Monitoring' to begin.")

    def show_notification(self, title, message):
        messagebox.showinfo(title, message)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.stop_monitoring()
        self.root.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = ServerMonitorApp(root)
    app.run()
