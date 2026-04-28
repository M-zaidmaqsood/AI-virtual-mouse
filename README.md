# 🖱️ AI Virtual Mouse — Hand Gesture Control

> Control your entire computer mouse using just your hand gestures via webcam — no extra hardware needed!

Built with **Python**, **MediaPipe**, **OpenCV**, and **PyAutoGUI**.

---

## 📸 Demo

> Point your index finger at the camera and move your hand to control the cursor in real time!

---

## ✋ Gesture Controls

| Gesture | Action |
|---|---|
| ☝️ Index finger move (thumb closed) | 🖱️ Move cursor |
| 👆 Index finger bent | 🖱️ Left click |
| 🖕 Middle finger bent | 🖱️ Right click |
| ✌️ V-sign (index + middle open) | 🖱️ Double click |
| ✊ Fist | 🖱️ Drag |
| 🤏 Pinch + move UP | 🔍 Zoom in |
| 🤏 Pinch + move DOWN | 🔍 Zoom out |
| 🖐️ All fingers stacked vertically | 📊 Slide mode |
| ↔️ Slide mode + swipe RIGHT | ▶️ Next slide |
| ↔️ Slide mode + swipe LEFT | ◀️ Previous slide |
| Thumb open | ⛔ Stop cursor |

---

## 🛠️ Tech Stack

| Library | Purpose |
|---|---|
| `opencv-python` | Webcam feed & frame processing |
| `mediapipe` | Hand landmark detection |
| `pyautogui` | Mouse & keyboard control |
| `numpy` | Coordinate math & smoothing |

---

## ⚙️ Installation & Setup

### ✅ Requirements
- Python **3.10** (recommended)
- A working **webcam**
- Windows OS (tested on Windows 10/11)

---

### 📥 Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-virtual-mouse.git
cd ai-virtual-mouse
```

---

### 🐍 Step 2 — Create a Virtual Environment

```bash
python -m venv venv
```

**Activate it:**

- Windows:
```bash
venv\Scripts\activate
```
- Mac/Linux:
```bash
source venv/bin/activate
```

---

### 📦 Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ Use the exact versions in `requirements.txt` to avoid compatibility issues.

---

### ▶️ Step 4 — Run the Project

```bash
python Script.py
```

Press **`Q`** to quit.

---

## 📋 Requirements (Tested & Working Versions)

```
numpy==1.26.4
opencv-python==4.9.0.80
mediapipe==0.10.9
pyautogui==0.9.54
```

> Full list is in `requirements.txt`

---

## 📁 Project Structure

```
ai-virtual-mouse/
│
├── Script.py           # Main application file
├── requirements.txt    # All dependencies with versions
├── README.md           # Project documentation
└── .gitignore          # Excludes venv and cache files
```

---

## ⚠️ Common Issues & Fixes

| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'cv2'` | Run `pip install opencv-python==4.9.0.80` |
| `module 'mediapipe' has no attribute 'solutions'` | Run `pip install mediapipe==0.10.9` |
| `numpy.core.multiarray failed to import` | Run `pip install numpy==1.26.4` |
| Camera not detected | Change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` |
| Cursor moving too fast | Increase `smoothing` value in `Script.py` (default: 4) |

---

## 🔧 Configuration

You can tweak these variables at the top of `Script.py`:

```python
smoothing = 4          # Higher = smoother but slower cursor
min_detection_confidence = 0.7   # Hand detection sensitivity
min_tracking_confidence = 0.7    # Hand tracking sensitivity
```

---

## 👨‍💻 Author


- GitHub: [@M-zaidmaqsood](https://github.com/M-zaidmaqsood)

---

## 📄License

 This project is open source and available under the [MIT License](LICENSE).