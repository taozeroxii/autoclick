import pyautogui
import time
import json
import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
from PIL import ImageGrab, ImageFont, ImageTk
import os
import threading
import tkinter.font as tkfont 
import keyboard 

stop_flag = False  # ใช้ควบคุมการหยุดคลิก
def monitor_hotkey():
    global stop_flag
    while True:
        if keyboard.is_pressed('s'):
            stop_flag = True
            print("🛑 หยุดโดยกดปุ่ม S")
            break
        time.sleep(0.1)
        
def find_image_on_screen(target_path, threshold=0.6):
    screen = np.array(ImageGrab.grab())
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

    template = cv2.imread(target_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"❌ ไม่สามารถโหลดภาพ: {target_path}")
        return None

    result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    print(f"🎯 ความคล้าย: {max_val:.2f} (threshold: {threshold})")

    if max_val >= threshold:
        template_h, template_w = template.shape
        center_x = max_loc[0] + template_w // 2
        center_y = max_loc[1] + template_h // 2
        return (center_x, center_y)
    else:
        return None

def load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"loop_count": 1, "click_delay": 2}

def save_settings(loop_count, click_delay):
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump({"loop_count": loop_count, "click_delay": click_delay}, f, ensure_ascii=False, indent=2)

def run_clicks(loop_count, click_delay, status_label):
    global stop_flag
    try:
        with open("click_sequence.json", "r", encoding="utf-8") as f:
            sequence = json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", "ไม่พบไฟล์ click_sequence.json")
        return

    messagebox.showinfo("เริ่มคลิก", "⏳ จะเริ่มคลิกใน 3 วินาที...")
    time.sleep(3)

    for i in range(loop_count):
        if stop_flag:
            status_label.config(text="⛔ หยุดแล้ว", fg="red")
            return
        print(f"\n🔁 รอบที่ {i+1} จาก {loop_count}")
        for step in sequence:
            if stop_flag:
                status_label.config(text="⛔ หยุดแล้ว", fg="red")
                return
            try:
                if step["type"] == "point":
                    x, y = step["pos"]
                    print(f"🖱️ คลิกตำแหน่ง: {x}, {y}")
                    pyautogui.click(x, y)

                elif step["type"] == "image":
                    image_file = step["file"]
                    print(f"🔍 หารูปภาพ: {image_file}")
                    location = find_image_on_screen(image_file, threshold=0.4)

                    if location:
                        print(f"📍 พบภาพที่: {location} คลิก!")
                        pyautogui.click(location)
                    else:
                        print(f"⚠️ ไม่พบภาพ: {image_file}")

                time.sleep(click_delay)

            except Exception as e:
                print(f"🚨 เกิดข้อผิดพลาด: {e}")

    status_label.config(text="✅ เสร็จสิ้นแล้ว", fg="green")
    messagebox.showinfo("เสร็จสิ้น", "✅ คลิกครบทุกครั้งแล้ว!")

def start_gui():
    global stop_flag
    settings = load_settings()

    def on_start():
        nonlocal status_label
        global stop_flag
        stop_flag = False
        try:
            loop = int(entry_loop.get())
            delay = float(entry_delay.get())
            if loop <= 0 or delay < 0:
                raise ValueError
            save_settings(loop, delay)
            status_label.config(text="🟢 กำลังทำงาน...", fg="blue")
            
            # เริ่มฟัง hotkey S (global)
            threading.Thread(target=monitor_hotkey, daemon=True).start()

            # เริ่มคลิก
            threading.Thread(target=run_clicks, args=(loop, delay, status_label), daemon=True).start()
        except ValueError:
            messagebox.showerror("ข้อผิดพลาด", "กรุณาใส่ค่าที่ถูกต้อง เช่น จำนวนรอบ > 0 และดีเลย์ >= 0")


    def on_save_settings():
        try:
            loop = int(entry_loop.get())
            delay = float(entry_delay.get())
            if loop <= 0 or delay < 0:
                raise ValueError
            save_settings(loop, delay)
            messagebox.showinfo("✅ บันทึกแล้ว", "บันทึกค่าการตั้งค่าสำเร็จแล้ว")
        except ValueError:
            messagebox.showerror("ข้อผิดพลาด", "กรุณาใส่ค่าที่ถูกต้อง")

    def on_stop():
        global stop_flag
        stop_flag = True
        status_label.config(text="🛑 กำลังหยุด...", fg="orange")
        
    def on_key_press(event):
        if event.char.lower() == 's':
            on_stop()

    # สร้างหน้าต่างหลัก
    root = tk.Tk()
    root.title("🖱️ Auto Clicker")
    root.geometry("400x450")
    root.configure(bg="#f5f5f5")

    # ฟอนต์ Kanit
    try:
        available_fonts = tkfont.families()
        if "Kanit" in available_fonts:
            kanit_font = ("Kanit", 12, "bold")
        else:
            kanit_font = ("TkDefaultFont", 12, "bold")
    except:
        kanit_font = ("TkDefaultFont", 12, "bold")


    # กล่อง Frame สำหรับจัดกลุ่ม
    frame = tk.Frame(root, bg="#f5f5f5")
    frame.pack(pady=15)

    # จำนวนรอบ
    tk.Label(frame, text="จำนวนรอบการคลิก:", font=kanit_font, bg="#f5f5f5").pack(pady=5)
    entry_loop = tk.Entry(frame, font=kanit_font, justify="center")
    entry_loop.pack(pady=5)
    entry_loop.insert(0, str(settings.get("loop_count", 1)))

    # ดีเลย์
    tk.Label(frame, text="ดีเลย์ระหว่างคลิก (วินาที):", font=kanit_font, bg="#f5f5f5").pack(pady=5)
    entry_delay = tk.Entry(frame, font=kanit_font, justify="center")
    entry_delay.pack(pady=5)
    entry_delay.insert(0, str(settings.get("click_delay", 2)))

    # ปุ่มเริ่ม / หยุด / บันทึก
    button_frame = tk.Frame(root, bg="#f5f5f5")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="▶ เริ่มคลิก", font=kanit_font, command=on_start, bg="#4CAF50", fg="white", width=15).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="💾 บันทึกการตั้งค่า", font=kanit_font, command=on_save_settings, bg="#2196F3", fg="white", width=15).grid(row=1, column=0, padx=5, pady=5)
    tk.Button(button_frame, text="⛔ หยุดการทำงาน", font=kanit_font, command=on_stop, bg="#f44336", fg="white", width=15).grid(row=2, column=0, padx=5)

    # สถานะ
    status_label = tk.Label(root, text="🕒 รอเริ่ม", font=kanit_font, fg="gray", bg="#f5f5f5")
    status_label.pack(pady=15)
    description = tk.Label(root, text="💡 กดปุ่ม 'S' บนคีย์บอร์ดเพื่อหยุดการทำงานได้ทุกเมื่อ", font=("Kanit", 10), fg="black", bg="#f5f5f5")
    description.pack(pady=5)
    # หากมีการกดคีย์บอร์ดและกดเป็น s ให้หยุดการทำงาน
    root.bind_all("<Key>", on_key_press)
    root.mainloop()

if __name__ == "__main__":
    start_gui()
