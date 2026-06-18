# 🌟 NeuralLab: Interactive Teachable Machine Clone

NeuralLab is a full-stack replica of Google's famous **Teachable Machine**, allowing users to build custom, real-time image classifiers directly from their web browsers. 

By leveraging **Transfer Learning**, the system avoids the need for massive computing resources and hours of training. It combines a pre-trained deep learning feature extractor with a lightning-fast machine learning classifier to train models in milliseconds.

---

## 🚀 Key Features

*   **Custom Class Creation:** Define image classes dynamically (e.g., "Red Object", "Blue Object", "Dog", "Cat").
*   **Dynamic Sample Upload:** Ingest image datasets per class on the fly.
*   **Transfer Learning Engine:** Uses a PyTorch MobileNetV3 backbone to extract robust image features, which are then classified using a Scikit-Learn Logistic Regression model.
*   **Instant Local Training:** Fits the classification boundary in milliseconds.
*   **Real-time Predictions:** Upload or supply test images and receive immediate classification outcomes along with percentage-based class probabilities.
*   **Workspace Management:** Rename classes (which dynamically re-labels the saved model on the fly without requiring a full retrain), delete classes, or clear the workspace completely.
*   **Unit Tests Suite:** Automated end-to-end tests to verify feature extraction, training, saving, and prediction logic.

---

## 🛠️ Tech Stack

### Backend
*   **FastAPI:** High-performance, production-ready Python API framework.
*   **PyTorch & Torchvision:** MobileNetV3 Small (pre-trained on ImageNet) utilized for feature extraction.
*   **Scikit-Learn:** Logistic Regression used for fast classifier training.
*   **Pillow:** Image manipulation and preprocessing.
*   **Uvicorn:** ASGI web server.

### Frontend
*   **React (Vite):** Modern, fast single-page app container.
*   **Tailwind CSS:** Premium, responsive user interface styling.

---

## 📂 Project Structure

```text
New-project/
├── backend/
│   ├── dataset/            # Uploaded training samples grouped by class
│   ├── main.py             # FastAPI Server (training, predicting, management)
│   ├── model.pkl           # Pickled trained model & class list
│   ├── requirements.txt    # Backend dependencies
│   └── test_backend.py     # Local verification test script
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React application layout & logic
│   │   ├── index.css       # Tailwind configuration & global styles
│   │   └── main.jsx        # App entry point
│   ├── index.html          # HTML Shell
│   ├── package.json        # Frontend dependencies
│   └── vite.config.js      # Vite configuration
└── README.md               # Project documentation (This file)
```

---

## 🧠 How It Works (The Science)

Instead of training a convolutional neural network (CNN) from scratch, NeuralLab utilizes **Transfer Learning**:

1.  **Preprocessing:** When an image is received, it is resized to $224 \times 224$ pixels and normalized according to ImageNet standards.
2.  **Feature Extraction ("The Eye"):** The image is fed into a pre-trained **MobileNetV3** model. We strip the final classification layer and extract the output of its feature extractor, resulting in a **576-dimensional vector** (representing texture, edges, and shapes).
3.  **Classification ("The Brain"):** A **Logistic Regression** model is trained using these 576-dimensional vectors. It fits decision boundaries between your classes.
4.  **Inference:** When a new image is tested, its 576-dimensional vector is fed to the trained Logistic Regression model, which outputs confidence percentages for each class using standard probability functions (`predict_proba`).

---

## 💻 Local Setup & Installation

### Prerequisite
*   Python 3.9+
*   Node.js & npm

### 1. Set Up the Backend
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   python main.py
   ```
   *The backend will start running locally at `http://localhost:8000`.*
   *API documentation can be accessed at `http://localhost:8000/docs`.*

### 2. Run the Verification Tests
To make sure the PyTorch feature extractor and training logic are functioning correctly on your local machine:
```bash
cd backend
python test_backend.py
```
This script will programmatically generate mock datasets, run feature extraction, train the classifier, and verify prediction accuracy.

### 3. Set Up the Frontend
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   *The frontend will run locally (typically at `http://localhost:5173`).*

---
