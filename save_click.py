import pyautogui
import keyboard
import time
import json
import os

click_sequence = []

print("คำสั่ง:")
print("- กด 's' เพื่อบันทึกตำแหน่งเมาส์")
print("- กด 'i' เพื่อเพิ่มตำแหน่งจากภาพ (พิมพ์ชื่อภาพ)")
print("- กด 'q' เพื่อบันทึกและออก")

while True:
    if keyboard.is_pressed('s'):
        pos = pyautogui.position()
        click_sequence.append({"type": "point", "pos": [pos[0], pos[1]]})
        print(f"✔ บันทึกตำแหน่ง: {pos}")
        time.sleep(0.5)

    elif keyboard.is_pressed('i'):
        image_file = input("📷 ป้อนชื่อไฟล์ภาพ (เช่น image.png): ")
        if os.path.exists(image_file):
            click_sequence.append({"type": "image", "file": image_file})
            print(f"✔ เพิ่มคำสั่งคลิกจากภาพ: {image_file}")
        else:
            print("❌ ไม่พบไฟล์ภาพ")
        time.sleep(0.5)

    elif keyboard.is_pressed('q'):
        print("📁 กำลังบันทึก click_sequence.json...")
        with open("click_sequence.json", "w") as f:
            json.dump(click_sequence, f, indent=2)
        print("✅ บันทึกเรียบร้อย!")
        break
