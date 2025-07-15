<h1 align="center">🧠 MirAi 2.0 – Smart Desktop AI Assistant</h1>

<p align="center">
  Your intelligent sidekick with AI chat, reminders, music launcher, real-time weather, and live search — all in one beautiful dark-mode desktop app.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Made%20With-PySide6-purple" />
  <img src="https://img.shields.io/badge/OpenRouter-LLMs-blue" />
  <img src="https://img.shields.io/badge/Status-Stable-brightgreen" />
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

---

## 🌟 Features

- 💬 **Chat with AI** using OpenRouter (Mistral, GPT, Claude & more)
- 🌍 **Live web search** via Serper.dev (optional)
- ⏰ **Smart Task Reminders** — set a task with date & time, get reminded!
- 🎵 **YouTube Music Launcher** — search in Brave instantly
- 🌦️ **Real-time Weather & Clock** (via wttr.in)
- 💡 **Creativity Slider** — tweak temperature in real time
- 🧠 **Persistent Chat Memory** (short context)
- 🖥️ **Modern UI** with full dark theme
- 🪄 **Summon anywhere** with `Ctrl+K` global hotkey
- ⚙️ **Build your own `.exe`** (no VSCode needed)

---

## 📸 Interface Preview

> Here's what it looks like in action:
<img width="684" height="684" alt="image" src="https://github.com/user-attachments/assets/0d0504d9-0fdc-4d7a-8d2e-c2f3772cf7e2" />

---

## 🚀 Quickstart

### 1. Clone this repo

```bash
git clone https://github.com/Manan-S85/MirAi2.git
cd MirAi2
```
<h3>2. Set up Python</h3>

Ensure Python 3.9+ is installed.
```bash
https://www.python.org/downloads/
```

<h3>3. Create and activate a virtual environment</h3>

```bash
python -m venv mirai
mirai\Scripts\activate
```

<h3>4. Install dependencies</h3>

```bash
pip install -r requirements.txt
```

<h3>5. Add your API keys</h3>

Create a file named .env in the root folder:
```bash
OPENROUTER_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
```
Don’t want web search? Leave SERPER_API_KEY blank.

<h3>🖥️ Run the Assistant</h3>

```bash
python mirai2.py
```
It will start minimized to system tray.
Hit Ctrl + K anytime to bring it up!

<h3>🧠 How to Use</h3>

✏️ Type your query and hit Send

🔍 Toggle “Enable Web Search” (optional)

📈 Slide “Creativity” to change randomness

🌦 Weather + Clock are always updated

📅 Add reminders from the right panel

🎵 Search any song and launch Brave

<h3>🛠️ Build a Windows Executable</h3>

Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

Step 2: Convert to .exe
```bash
pyinstaller --onefile --windowed --icon=logo.ico mirai2.py
```

Your final .exe will be in the dist/ folder. Share it freely!

<h3>⚙️ Configuration Options</h3>

<table>
  <thead>
    <tr>
      <th>Setting</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>DEFAULT_MODEL</code></td>
      <td>Initial model from OpenRouter</td>
    </tr>
    <tr>
      <td><code>SERPER_NUM_RESULTS</code></td>
      <td>Number of web results to fetch</td>
    </tr>
    <tr>
      <td><code>WEATHER_CITY</code></td>
      <td>Change default weather location</td>
    </tr>
    <tr>
      <td><code>BRAVE_PATH</code></td>
      <td>Set custom Brave browser path</td>
    </tr>
  </tbody>
</table>

<p>💡 <b>Bonus:</b> Easily <b>toggle between multiple free models</b> from OpenRouter using the dropdown – including Mistral, Zephyr, and more!</p>

<h3>📁 Project Structure</h3>

<pre>
MirAi2/
├── <code>mirai2.py</code>              # Main app file
├── <code>logo.png</code> / <code>icon.ico</code>    # Icons
├── <code>requirements.txt</code>       # All dependencies
├── <code>.env</code>                   # Your private API keys
├── <code>dist/</code>                  # Contains final .exe
└── <code>README.md</code>              # This file
</pre>

<h3>🔐 API Sources</h3>

OpenRouter.ai — Chat with powerful LLMs

Serper.dev — Google Search results

wttr.in — Terminal-based weather reports

<h3>📄 License</h3>

This project is under the MIT License. Free to use, fork, remix.

<h2>👨‍💻 Author</h2>

Manan Sandhaliya

Computer Science Engineering(Specilaization in AI-ML) student 🎓 @ VIT Bhopal 

🔗 LinkedIn("www.linkedin.com/in/manansinh-sandhaliya-0b6569251")

💌 Feedback welcome via Issues or DMs!
