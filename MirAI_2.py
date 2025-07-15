import os
import sys
import json
import time
import threading
import subprocess
import requests
from datetime import datetime, timedelta
from collections import deque
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QTextEdit, QPlainTextEdit,
    QListWidget, QListWidgetItem, QDateTimeEdit, QSlider
)
import keyboard
from openai import OpenAI
from PySide6.QtCore import Qt, QTimer, QEvent


# === CONFIG ===
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
SERPER_NUM_RESULTS = 3
WEATHER_CITY = "Bhopal"
MAX_CHAT_MEMORY = 8
SETTINGS_FILE = Path.home() / ".mirai_settings.json"
TASKS_FILE = Path.home() / ".mirai_tasks.json"

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"  # Adjust if needed

def open_in_brave(url: str):
    try:
        subprocess.Popen([BRAVE_PATH, url])
    except Exception:
        import webbrowser
        webbrowser.open_new_tab(url)

def fetch_free_models():
    try:
        resp = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
        data = resp.json().get("data", [])
        models = [
            {"id": m["id"], "name": m.get("name", m["id"])}
            for m in data
            if m["id"].endswith(":free") or all(float(v or 0) == 0 for v in m.get("pricing", {}).values())
        ]
        return sorted(models, key=lambda m: m["name"].lower())
    except Exception:
        # fallback if API fails
        return [
            {"id": "mistralai/mistral-7b-instruct:free", "name": "Mistral‑7B"},
            {"id": "huggingfaceh4/zephyr-7b-beta:free", "name": "Zephyr‑7B"},
        ]

class MirAi(QWidget):
    def __init__(self):
        super().__init__()

        self.client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

        self.serper_available = bool(SERPER_API_KEY)
        self.models = fetch_free_models()
        self.current_model_index = 0
        self.chat_memory = deque(maxlen=MAX_CHAT_MEMORY)
        self.temperature = 0.7

        self.settings = self._load_json(SETTINGS_FILE) or {}
        self.tasks = self._load_json(TASKS_FILE) or []
        self.tasks = [t for t in self.tasks if isinstance(t, dict) and "text" in t and "when" in t]

        self._build_ui()
        self._apply_styles()

        self._setup_timers()

        self.hide()
        self._last_hotkey = 0.0

    def _load_json(self, path):
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
            return None
        except Exception:
            return None

    def _save_json(self, path, obj):
        try:
            path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print("Error saving json:", e)

    def _build_ui(self):
        self.setWindowTitle("MirAi 2.0")
        self.resize(900, 600)
        layout = QHBoxLayout(self)

        # Left panel: YouTube Music Search (Brave)
        left = QVBoxLayout()
        left.addWidget(QLabel("🎵 Search YouTube (Brave)"))
        self.song_input = QLineEdit(placeholderText="Search song or artist ...")
        left.addWidget(self.song_input)
        btn_search = QPushButton("Search & Play")
        btn_search.clicked.connect(self._open_music)
        left.addWidget(btn_search)
        left.addStretch()

        # Center panel: Chat AI + controls
        center = QVBoxLayout()

        title = QLabel("MirAi 2.0")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 24px;")
        center.addWidget(title)

        info_row = QHBoxLayout()
        self.datetime_label = QLabel()
        self.weather_label = QLabel()
        info_row.addWidget(self.datetime_label)
        info_row.addStretch()
        info_row.addWidget(self.weather_label)
        center.addLayout(info_row)

        # Model selector
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Model:"))
        self.model_box = QComboBox()
        for m in self.models:
            self.model_box.addItem(m["name"], userData=m["id"])
        self.model_box.setCurrentIndex(self.current_model_index)
        self.model_box.currentIndexChanged.connect(self._model_changed)
        model_row.addWidget(self.model_box)
        model_row.addStretch()
        center.addLayout(model_row)

        # Creativity slider
        temp_row = QHBoxLayout()
        self.temp_label = QLabel(f"Creativity: {self.temperature:.1f}")
        temp_row.addWidget(self.temp_label)
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(1, 10)
        self.temp_slider.setValue(int(self.temperature * 10))
        self.temp_slider.valueChanged.connect(self._set_temp)
        temp_row.addWidget(self.temp_slider)
        center.addLayout(temp_row)

        # Search enable checkbox
        self.search_chk = QCheckBox("Enable Web Search")
        self.search_chk.setChecked(self.serper_available)
        center.addWidget(self.search_chk)

        # Output chat box
        self.out_box = QTextEdit(readOnly=True)
        center.addWidget(self.out_box, stretch=1)

        # Input box
        self.in_edit = QPlainTextEdit()
        self.in_edit.setPlaceholderText("Ask something... (Ctrl+Enter to send)")
        self.in_edit.installEventFilter(self)
        center.addWidget(self.in_edit, stretch=0)

        btn_send = QPushButton("Send")
        btn_send.clicked.connect(self._send)
        center.addWidget(btn_send)

        # Right panel: Tasks
        right = QVBoxLayout()
        right.addWidget(QLabel("📝 Tasks"))

        self.task_list = QListWidget()
        right.addWidget(self.task_list, stretch=1)

        self.task_in = QPlainTextEdit()
        self.task_in.setMaximumHeight(50)
        self.task_in.setPlaceholderText("Add task ...")
        right.addWidget(self.task_in)

        self.dt_pick = QDateTimeEdit(datetime.now() + timedelta(minutes=30))
        self.dt_pick.setCalendarPopup(True)
        right.addWidget(self.dt_pick)

        btn_add_task = QPushButton("Add Task")
        btn_add_task.clicked.connect(self._add_task)
        right.addWidget(btn_add_task)

        btn_del_task = QPushButton("Delete Selected")
        btn_del_task.clicked.connect(self._delete_task)
        right.addWidget(btn_del_task)

        right.addStretch()

        layout.addLayout(left, 1)
        layout.addLayout(center, 3)
        layout.addLayout(right, 1)

        self._refresh_tasks()

    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {background:#121212; color:#EEE; font-family:'Segoe UI',sans-serif;}
            QLineEdit,QTextEdit,QPlainTextEdit {background:#1E1E1E; border:1px solid #444; border-radius:6px; padding:8px; font-size:14px;}
            QPushButton {background:#007ACC; border-radius:6px; padding:8px; font-weight:bold; font-size:16px; color:white;}
            QPushButton:hover {background:#005999;}
            QSlider::groove:horizontal {height:6px; background:#444; border-radius:3px;}
            QSlider::handle:horizontal {background:#007ACC; width:14px; height:14px; border-radius:7px; margin:-4px 0;}
            QCheckBox, QLabel {font-size:14px;}
            QListWidget {background:#222; border:1px solid #444; border-radius:6px;}
        """)

    def _set_temp(self, val):
        self.temperature = val / 10.0
        self.temp_label.setText(f"Creativity: {self.temperature:.1f}")

    def _model_changed(self, index):
        self.current_model_index = index
        self.settings["model_index"] = index
        self._save_json(SETTINGS_FILE, self.settings)

    def _open_music(self):
        query = self.song_input.text().strip()
        if not query:
            return
        # Encode query and form YouTube search URL (brave browser)
        search_url = f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}"
        open_in_brave(search_url)

    def _send(self):
        text = self.in_edit.toPlainText().strip()
        if not text:
            return
        self.in_edit.clear()
        self._append("You", text)

        threading.Thread(target=self._ask_ai, args=(text,), daemon=True).start()

    def _append(self, who, text):
        safe_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        self.out_box.append(f"<b>{who}:</b> {safe_text}")

    def _ask_ai(self, text):
        context = None
        if self.search_chk.isChecked() and self.serper_available:
            context = self._live_search_serper(text)
        prompt = f"{text}\n\n{context}\n\nUsing ONLY the information above, answer clearly." if context else text

        model_id = self.model_box.currentData()
        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"<i>Error:</i> {e}"
        self._append("AI", answer)

    def _live_search_serper(self, query):
        try:
            r = requests.post(
                "https://google.serper.dev/search",
                json={"q": query, "num": SERPER_NUM_RESULTS},
                headers={"X-API-KEY": SERPER_API_KEY},
                timeout=10,
            )
            if r.status_code == 429:
                self.serper_available = False
                return None
            r.raise_for_status()
            data = r.json()
            snippets = []
            if (ab := data.get("answerBox", {})).get("answer"):
                snippets.append(f'AnswerBox: {ab["answer"]}')
            if (kg := data.get("knowledgeGraph")) and kg.get("title"):
                snippets.append(f'KnowledgeGraph: {kg["title"]} – {kg.get("description","")}')
            for res in data.get("organic", [])[:SERPER_NUM_RESULTS]:
                snippets.append(f'"{res.get("title","")}" – {res.get("snippet","")}')
            return "Recent Web Results:\n" + "\n".join(snippets) if snippets else None
        except Exception as e:
            print("[Serper error]", e)
            self.serper_available = False
            return None

    def eventFilter(self, obj, event):
        # Ctrl+Enter triggers send
        if obj == self.in_edit and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and (event.modifiers() & Qt.ControlModifier):
                self._send()
                return True
        return super().eventFilter(obj, event)

    def _refresh_tasks(self):
        self.task_list.clear()
        now = datetime.now()
        for t in self.tasks:
            # Format display with time
            when = t.get("when")
            if isinstance(when, str):
                try:
                    dt = datetime.fromisoformat(when)
                    when_str = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    when_str = when
            else:
                when_str = str(when)
            item_text = f"{t.get('text', '')} – {when_str}"
            item = QListWidgetItem(item_text)
            self.task_list.addItem(item)

    def _add_task(self):
        text = self.task_in.toPlainText().strip()
        if not text:
            return
        dt = self.dt_pick.dateTime().toPython()
        new_task = {"text": text, "when": dt.isoformat()}
        self.tasks.append(new_task)
        self._save_json(TASKS_FILE, self.tasks)
        self._refresh_tasks()
        self.task_in.clear()

    def _delete_task(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            idx = self.task_list.row(item)
            del self.tasks[idx]
        self._save_json(TASKS_FILE, self.tasks)
        self._refresh_tasks()

    def _setup_timers(self):
        # Update date/time and weather every second
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_datetime_weather)
        self.timer.start(1000)
        self._last_weather_update = 0
        self._update_datetime_weather()

        # Check tasks every minute for reminders
        self.task_timer = QTimer()
        self.task_timer.timeout.connect(self._check_reminders)
        self.task_timer.start(60 * 1000)

        # Hotkey poller every 100ms
        self.hotkey_timer = QTimer()
        self.hotkey_timer.timeout.connect(self._check_hotkey)
        self.hotkey_timer.start(100)

    def _update_datetime_weather(self):
        now = datetime.now().strftime("%A, %d %b %Y  %I:%M:%S %p")
        self.datetime_label.setText(f"📅 {now}")

        # Update weather max every 10 mins
        if time.time() - self._last_weather_update > 600:
            threading.Thread(target=self._fetch_weather, daemon=True).start()

    def _fetch_weather(self):
        try:
            url = f"https://wttr.in/{WEATHER_CITY}?format=%t+%C"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                weather = res.text.strip()
                self.weather_label.setText(f"🌤 {WEATHER_CITY}: {weather}")
            else:
                self.weather_label.setText("⚠️ Weather Unavailable")
            self._last_weather_update = time.time()
        except Exception:
            self.weather_label.setText("⚠️ Weather Unavailable")

    def _check_hotkey(self):
        now = time.time()
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('k'):
            if now - self._last_hotkey > 0.7:
                self._last_hotkey = now
                if self.isVisible():
                    self.hide()
                else:
                    self.show()
                    self.raise_()
                    self.activateWindow()
                    self.in_edit.setFocus()

    def _check_reminders(self):
        now = datetime.now()
        due = []
        for task in self.tasks:
            try:
                dt = datetime.fromisoformat(task["when"])
                if dt <= now:
                    due.append(task)
            except Exception:
                continue

        for task in due:
            self._append("Reminder", f"⏰ Task due: {task['text']}")
            self.tasks.remove(task)

        if due:
            self._save_json(TASKS_FILE, self.tasks)
            self._refresh_tasks()

# === RUN APP ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MirAi()
    sys.exit(app.exec())
