# Pothole-AI 
# 🛣️ Pothole-AI

An AI-powered road damage detection system that uses **YOLO** for pothole detection, **Streamlit** for an interactive web interface, and **Firebase Firestore** for storing detection history. The application helps identify potholes from uploaded images and provides an easy-to-use dashboard for visualization and management.

---

## 🚀 Features

- 🔍 AI-based pothole detection using YOLO
- 🖼️ Image upload and prediction
- 📊 Detection confidence display
- ☁️ Firebase Firestore integration for storing results
- 🌐 Streamlit-based interactive web interface
- 🧪 Training and testing scripts included
- 📁 Modular project structure

---

## 🛠️ Tech Stack

### Frontend
- Streamlit

### Backend
- Python

### AI / Machine Learning
- YOLO
- OpenCV
- NumPy

### Database
- Firebase Firestore

### Other Libraries
- Pillow
- Pandas
- Ultralytics

---

## 📂 Project Structure

```text
Pothole-AI/
│
├── dataset/                  # Dataset used for training
├── models/                   # Trained YOLO model
├── app.py                    # Main Streamlit application
├── firebase_client.py        # Firebase connection
├── cnn_model.py              # CNN model (previous implementation)
├── train_yolo.py             # YOLO training script
├── train_model.py            # CNN training script
├── predict_image.py          # Image prediction
├── test_yolo.py              # YOLO testing
├── test_streamlit_yolo.py    # Streamlit testing
├── test_firestore.py         # Firebase testing
├── images_test.py            # Image testing
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/ayushi03shukla-spec/Pothole-AI.git

cd Pothole-AI
```

### Create a virtual environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔥 Firebase Setup

1. Create a Firebase project.
2. Enable Firestore Database.
3. Download your Service Account Key.
4. Place the credentials file in the project directory.
5. Update `firebase_client.py` with your Firebase configuration.

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 🧠 Model

Current detection model:

- YOLO (Ultralytics)

Previous implementation:

- CNN

---

## 📊 Workflow

```
Image Upload
      │
      ▼
YOLO Detection
      │
      ▼
Confidence Score
      │
      ▼
Display Result
      │
      ▼
Store Detection in Firebase
```

---

## 📸 Output

The application provides:

- Uploaded image preview
- Pothole detection
- Confidence score
- Detection history
- Firebase data storage

---

## 👥 Team

| Name | Role |
|------|------|
| Ayushi Shukla | Project Lead, Streamlit UI, Firebase Integration |
| Prashant | YOLO Development |
| Anika | Dataset Preparation |
| Anamika | Testing & Validation |
| Anushka | Documentation & Deployment |

---

## 🔄 Git Workflow

- Each member works on a separate branch.
- Changes are pushed to individual branches.
- Pull Requests are reviewed before merging into `main`.

Branches:

```
main
Ayushi
Prashant
Anika
Anamika
Anushka
```

---

## 📌 Future Enhancements

- Real-time pothole detection using webcam
- GPS location mapping
- Severity classification
- Road condition analytics dashboard
- Mobile application
- Cloud deployment

---

## 📄 License

This project is developed for educational and research purposes.

---

## ⭐ Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push your branch
5. Open a Pull Request

---

## 📧 Contact

**Ayushi Shukla**

GitHub: https://github.com/ayushi03shukla-spec
