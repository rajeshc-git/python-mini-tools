import sys
import os

# Redirect stdout and stderr to /dev/null (on Windows use 'nul')
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')


import customtkinter as ctk
import speedtest
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time
from plyer import notification
from threading import Thread  # Import Thread from threading module

class SpeedometerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Internet Speed Test")
        self.geometry("800x600")
        self.configure(bg='white')
        
        # Menu
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        about_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="About", menu=about_menu)
        about_menu.add_command(label="About Us", command=self.show_about)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        
        # Version Label
        version_label = ctk.CTkLabel(self, text="Speed Test | Powered by ABI Health", font=("Helvetica", 12))
        version_label.pack(pady=10)

        self.figure, self.ax = plt.subplots()
        self.ax.set_facecolor('#ffffff')
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(pady=20)
        
        self.start_button = ctk.CTkButton(self, text="Start Speed Test", command=self.start_speed_test)
        self.start_button.pack(pady=20)
        
        self.download_label = ctk.CTkLabel(self, text="Download Speed: 0 Mbps", font=("Helvetica", 16))
        self.download_label.pack(pady=10)
        
        self.upload_label = ctk.CTkLabel(self, text="Upload Speed: 0 Mbps", font=("Helvetica", 16))
        self.upload_label.pack(pady=10)
        
        self.draw_speedometer(0, 0)
    
    def draw_speedometer(self, download_speed, upload_speed):
        self.ax.clear()
        self.ax.set_facecolor('#ffffff')
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # Draw the speedometer
        theta = np.linspace(0, np.pi, 100)
        r = np.ones(100)
        
        self.ax.plot(np.cos(theta), np.sin(theta), 'k-', linewidth=2)
        
        for i in range(0, 101, 10):
            angle = np.pi * i / 100
            x = np.cos(angle)
            y = np.sin(angle)
            self.ax.text(x * 1.1, y * 1.1, f'{i}', ha='center', va='center', fontsize=10)
        
        # Draw the download needle
        download_angle = np.pi * download_speed / 100
        download_x = np.cos(download_angle)
        download_y = np.sin(download_angle)
        self.ax.plot([0, download_x], [0, download_y], 'r-', linewidth=4, label='Download')

        # Draw the upload needle
        upload_angle = np.pi * upload_speed / 100
        upload_x = np.cos(upload_angle)
        upload_y = np.sin(upload_angle)
        self.ax.plot([0, upload_x], [0, upload_y], 'b-', linewidth=4, label='Upload')

        self.ax.legend(loc='lower right')
        
        self.canvas.draw()
    
    def start_speed_test(self):
        self.download_label.configure(text="Testing Download Speed...")
        self.upload_label.configure(text="Testing Upload Speed...")
        self.start_button.configure(state=tk.DISABLED)
        
        # Run the speed test in a separate thread
        thread = Thread(target=self.run_speed_test)
        thread.start()
    
    def run_speed_test(self):
     try:
        st = speedtest.Speedtest()
        st.get_best_server()

        start_time = time.time()
        download_speed = 0
        upload_speed = 0
        test_duration = 10  # seconds
        measurements = 0

        while time.time() - start_time < test_duration:
            download_speed += st.download() / 1_000_000  # Convert to Mbps
            upload_speed += st.upload() / 1_000_000  # Convert to Mbps
            measurements += 1

            # Update GUI
            self.after(0, self.update_ui, download_speed / measurements, upload_speed / measurements)
            
            time.sleep(1)  # Adjust update frequency as needed

        # Calculate average speed
        download_speed /= measurements
        upload_speed /= measurements

     except Exception as e:
        print(f"Error running speed test: {e}")
        self.after(0, self.update_ui, 0, 0)
    
     finally:
        self.after(0, self.finish_test, download_speed, upload_speed)


    
    def update_ui(self, download_speed, upload_speed):
        self.download_label.configure(text=f"Download Speed: {download_speed:.2f} Mbps")
        self.upload_label.configure(text=f"Upload Speed: {upload_speed:.2f} Mbps")
        self.draw_speedometer(download_speed, upload_speed)
    
    def finish_test(self, download_speed, upload_speed):
        self.start_button.configure(state=tk.NORMAL)
        self.download_label.configure(text=f"Download Speed: {download_speed:.2f} Mbps")
        self.upload_label.configure(text=f"Upload Speed: {upload_speed:.2f} Mbps")

        # Display notification using tkinter messagebox
        messagebox.showinfo("Internet Speed Test Result",
                            f"Download Speed: {download_speed:.2f} Mbps\nUpload Speed: {upload_speed:.2f} Mbps")

    def show_about(self):
        about_window = tk.Toplevel(self)
        about_window.title("About Us")
        about_window.geometry("300x100")
        
        about_label = tk.Label(about_window, text="Created By Rajesh Choudhury", font=("Helvetica", 14))
        about_label.pack(pady=20)

    def toggle_dark_mode(self):
        if ctk.get_appearance_mode() == "Light":
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

if __name__ == "__main__":
    app = SpeedometerApp()
    app.mainloop()
