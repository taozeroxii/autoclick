import cv2
import numpy as np
from PIL import ImageGrab

def find_image_on_screen(target_path, threshold=0.6):
    # จับภาพหน้าจอทั้งหมด
    screen = np.array(ImageGrab.grab())
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

    # โหลดภาพเป้าหมาย
    template = cv2.imread(target_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"❌ ไม่สามารถโหลดภาพ: {target_path}")
        return None

    # ใช้ Template Matching
    result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    print(f"🎯 ความคล้าย: {max_val:.2f} (threshold: {threshold})")

    if max_val >= threshold:
        # คำนวณจุดกึ่งกลาง
        template_h, template_w = template.shape
        center_x = max_loc[0] + template_w // 2
        center_y = max_loc[1] + template_h // 2
        return (center_x, center_y)
    else:
        return None
