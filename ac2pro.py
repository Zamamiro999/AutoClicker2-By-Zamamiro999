import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import win32gui
import win32con
import win32api
from pynput import keyboard, mouse

clicking = False
target_hwnd = None
click_pos = (0, 0)

# ==========================
# Ambil daftar window aktif
# ==========================
def enum_windows():
    windows = []
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            windows.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(callback, None)
    return windows

# ==========================
# Kirim klik ke window target
# ==========================
def click_in_window(hwnd, x, y, delay, repeat):
    global clicking
    lParam = win32api.MAKELONG(x, y)
    count = 0
    while clicking and (repeat == -1 or count < repeat):
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, lParam)
        count += 1
        time.sleep(delay / 1000.0)

# ==========================
# Start/Stop
# ==========================
def start_clicking():
    global clicking, target_hwnd, click_pos
    if clicking:
        return
    
    if not target_hwnd:
        messagebox.showerror("Error", "Pilih window target terlebih dahulu!")
        return

    try:
        delay = int(delay_var.get())
        repeat = int(repeat_var.get())
    except ValueError:
        messagebox.showerror("Error", "Delay dan Repeat harus angka!")
        return

    if click_pos == (0, 0):
        messagebox.showerror("Error", "Posisi klik belum ditentukan!")
        return

    clicking = True
    threading.Thread(target=click_in_window, args=(target_hwnd, click_pos[0], click_pos[1], delay, repeat), daemon=True).start()
    log(f"Mulai auto click di {click_pos}")

def stop_clicking():
    global clicking
    clicking = False
    log("Auto Clicker dihentikan")

def toggle_clicking():
    if clicking:
        stop_clicking()
    else:
        start_clicking()

# ==========================
# Ambil posisi klik dari window target
# ==========================
def capture_click_position():
    log("Klik di dalam window target...")
    def on_click(x, y, button, pressed):
        global click_pos
        if pressed:
            # Konversi koordinat layar ke koordinat window
            rect = win32gui.GetWindowRect(target_hwnd)
            click_pos = (x - rect[0], y - rect[1])
            log(f"Posisi klik diatur ke {click_pos}")
            return False  # Stop listener
    mouse.Listener(on_click=on_click).start()

# ==========================
# Pilih window dari dropdown
# ==========================
def update_window_list():
    windows = enum_windows()
    window_dropdown["values"] = [title for hwnd, title in windows]
    log("Daftar window diperbarui")

def set_target_window(event=None):
    global target_hwnd
    title = window_var.get()
    for hwnd, t in enum_windows():
        if t == title:
            target_hwnd = hwnd
            log(f"Target window: {title}")
            break

# ==========================
# Listener tombol F8
# ==========================
def on_key_press(key):
    if key == keyboard.Key.f8:
        toggle_clicking()

def start_listener():
    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()

# ==========================
# GUI
# ==========================
root = tk.Tk()
root.title("Auto Clicker PRO Edition")
root.geometry("480x430")
root.resizable(False, False)

# ========== DARK MODE THEME ==========
root.configure(bg="#1e1e1e")
style = ttk.Style()
style.theme_use("clam")

# Style untuk widget
style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10, "bold"), background="#2d2d30", foreground="#ffffff", borderwidth=0, padding=8)
style.map("TButton",
          background=[("active", "#3a3a3d"), ("!disabled", "#2d2d30")],
          foreground=[("active", "#00ffcc")])
style.configure("TCombobox", fieldbackground="#2d2d30", background="#2d2d30", foreground="#ffffff", arrowcolor="#00ffcc")
style.configure("TEntry", fieldbackground="#2d2d30", foreground="#ffffff", insertcolor="#ffffff")

# Fungsi log status
def log(msg):
    status_label.config(text=f"Status: {msg}")

# Pilih window target
ttk.Label(root, text="🎯 Pilih Window Target:").pack(pady=5)
window_var = tk.StringVar()
window_dropdown = ttk.Combobox(root, textvariable=window_var, state="readonly", width=50)
window_dropdown.pack(pady=2)
window_dropdown.bind("<<ComboboxSelected>>", set_target_window)
ttk.Button(root, text="🔄 Perbarui Daftar Window", command=update_window_list).pack(pady=5)

# Delay & Repeat
ttk.Label(root, text="⏳ Delay antar klik (ms):").pack(pady=5)
delay_var = tk.StringVar(value="50")
ttk.Entry(root, textvariable=delay_var).pack(pady=2)

ttk.Label(root, text="🔁 Jumlah klik (-1 = infinite):").pack(pady=5)
repeat_var = tk.StringVar(value="-1")
ttk.Entry(root, textvariable=repeat_var).pack(pady=2)

# Posisi klik
ttk.Label(root, text="📍 Posisi klik:").pack(pady=5)
ttk.Button(root, text="🎯 Tentukan Posisi Klik", command=capture_click_position).pack(pady=5)

# Tombol Start/Stop
ttk.Button(root, text="▶ START", command=start_clicking).pack(pady=5)
ttk.Button(root, text="⏹ STOP", command=stop_clicking).pack(pady=5)

# Status
status_label = ttk.Label(root, text="Status: Menunggu")
status_label.pack(pady=10)

# Mulai
update_window_list()
start_listener()
root.mainloop()
