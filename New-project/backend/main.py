import os
import shutil
import uuid
import pickle
import numpy as np
from PIL import Image
from typing import List, Optional
from pydantic import BaseModel

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# PyTorch and Machine Learning Imports
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from sklearn.linear_model import LogisticRegression

app = FastAPI(title="NeuralLab Teachable Machine Backend")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# Ensure dataset directory exists
os.makedirs(DATASET_DIR, exist_ok=True)

# Cache variables for trained model
_trained_model = None
_trained_classes = []
_model_mtime = None

# Initialize PyTorch MobileNetV3 Small (Feature Extractor)
# We load weights lazily or on startup. We use models.MobileNet_V3_Small_Weights.DEFAULT
try:
    weights = models.MobileNet_V3_Small_Weights.DEFAULT
    feature_extractor = models.mobilenet_v3_small(weights=weights)
except Exception as e:
    print(f"Error loading MobileNetV3 weights with DEFAULT: {e}. Falling back without weights.")
    feature_extractor = models.mobilenet_v3_small(pretrained=True)

feature_extractor.eval()

# Image Preprocessing Transform
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Request schemas
class TrainRequest(BaseModel):
    c_value: Optional[float] = 1.0
    max_iter: Optional[int] = 1000

class RenameClassRequest(BaseModel):
    old_name: str
    new_name: str

class DeleteClassRequest(BaseModel):
    class_name: str


def get_feature_vector(image_path_or_file):
    """
    Loads an image, applies standard pre-processing, and runs it through
    MobileNetV3 to extract a 576-dimensional feature vector.
    """
    try:
        img = Image.open(image_path_or_file).convert("RGB")
        tensor = preprocess(img).unsqueeze(0)  # Shape: (1, 3, 224, 224)
        
        with torch.no_grad():
            features = feature_extractor.features(tensor)
            # Global Average Pooling to reduce to (1, 576, 1, 1)
            pooled = torch.nn.functional.adaptive_avg_pool2d(features, (1, 1))
            # Flatten to (1, 576)
            flat = torch.flatten(pooled, 1)
            return flat.numpy()[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")


def load_classifier():
    """
    Checks if a trained classifier is saved, loads it into memory, and caches it.
    Automatically reloads if the model file is modified.
    """
    global _trained_model, _trained_classes, _model_mtime
    
    if not os.path.exists(MODEL_PATH):
        _trained_model = None
        _trained_classes = []
        _model_mtime = None
        return None, []

    current_mtime = os.path.getmtime(MODEL_PATH)
    if _trained_model is None or _model_mtime != current_mtime:
        try:
            with open(MODEL_PATH, "rb") as f:
                data = pickle.load(f)
                _trained_model = data["classifier"]
                _trained_classes = data["class_names"]
                _model_mtime = current_mtime
        except Exception as e:
            print(f"Error loading classifier: {e}")
            return None, []
            
    return _trained_model, _trained_classes


@app.get("/status")
def get_status():
    """
    Returns the status of the workbench: whether a model is trained,
    and a summary of classes and sample counts.
    """
    # Count samples in dataset subfolders
    classes_summary = {}
    if os.path.exists(DATASET_DIR):
        for entry in os.scandir(DATASET_DIR):
            if entry.is_dir():
                count = len([f for f in os.scandir(entry.path) if f.is_file() and f.name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
                classes_summary[entry.name] = count

    model, classes = load_classifier()
    
    return {
        "trained": model is not None,
        "classes": classes_summary
    }


@app.post("/upload-sample")
async def upload_sample(
    class_name: str = Form(...),
    files: List[UploadFile] = File(default=[])
):
    """
    Accepts images for a class. Saves them in dataset/<class_name>/ with UUID names.
    If files is empty, clears the class folder instead.
    """
    # Clean class name to prevent directory traversal
    safe_class_name = "".join(c for c in class_name if c.isalnum() or c in (" ", "-", "_")).strip()
    if not safe_class_name:
        raise HTTPException(status_code=400, detail="Invalid class name")

    class_path = os.path.join(DATASET_DIR, safe_class_name)
    os.makedirs(class_path, exist_ok=True)

    # If no files sent, delete folder contents (Clear Samples action)
    if not files:
        for filename in os.listdir(class_path):
            file_path = os.path.join(class_path, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        return {"status": "success", "message": f"Cleared all samples for class: {safe_class_name}"}

    # Save uploaded files
    saved_count = 0
    for file in files:
        if not file.content_type.startswith("image/"):
            continue
            
        file_ext = os.path.splitext(file.filename)[1]
        if not file_ext:
            file_ext = ".jpg"  # default
            
        random_filename = f"{uuid.uuid4()}{file_ext}"
        destination = os.path.join(class_path, random_filename)
        
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_count += 1

    return {"status": "success", "message": f"Uploaded {saved_count} samples for class {safe_class_name}"}


@app.post("/train")
def train_model(payload: TrainRequest):
    """
    Loads all image samples, extracts features via MobileNetV3,
    trains a Logistic Regression classifier, and saves weights.
    """
    # Scan dataset directory
    if not os.path.exists(DATASET_DIR):
        raise HTTPException(status_code=400, detail="No dataset folder found. Upload images first.")

    classes = sorted([d.name for d in os.scandir(DATASET_DIR) if d.is_dir()])
    
    # Validation: Needs at least 2 classes with >= 1 sample each
    valid_classes = []
    for c in classes:
        c_dir = os.path.join(DATASET_DIR, c)
        files = [f.path for f in os.scandir(c_dir) if f.is_file() and f.name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        if len(files) > 0:
            valid_classes.append((c, files))

    if len(valid_classes) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Training requires at least 2 classes with at least 1 image sample each."
        )

    X = []
    y = []
    class_names = [vc[0] for vc in valid_classes]

    # Extract features
    for class_idx, (class_name, image_paths) in enumerate(valid_classes):
        for img_path in image_paths:
            feature_vector = get_feature_vector(img_path)
            X.append(feature_vector)
            y.append(class_idx)

    X = np.array(X)
    y = np.array(y)

    # Train Logistic Regression
    try:
        classifier = LogisticRegression(C=payload.c_value, max_iter=payload.max_iter, random_state=42)
        classifier.fit(X, y)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fit classifier: {str(e)}")

    # Save classifier and class mapping
    model_data = {
        "classifier": classifier,
        "class_names": class_names
    }
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model_data, f)

    # Force cache reload on next request
    load_classifier()

    return {"status": "success", "message": "Model trained successfully", "classes": class_names}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Accepts a single image, runs inference, and returns prediction details.
    """
    classifier, class_names = load_classifier()
    if classifier is None:
        raise HTTPException(status_code=400, detail="Model has not been trained yet.")

    # Extract features for the uploaded image
    feature_vector = get_feature_vector(file.file)
    feature_vector = feature_vector.reshape(1, -1)

    # Run predictions
    try:
        probs = classifier.predict_proba(feature_vector)[0]
        pred_idx = classifier.predict(feature_vector)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classifier prediction failed: {str(e)}")

    # Map probabilities to classes
    probabilities_map = {}
    for idx, class_name in enumerate(class_names):
        probabilities_map[class_name] = float(probs[idx])

    winning_class = class_names[pred_idx]

    return {
        "class": winning_class,
        "probabilities": probabilities_map
    }


@app.post("/rename-class")
def rename_class(payload: RenameClassRequest):
    """
    Renames the dataset directory of a class, and updates model.pkl
    on the fly to keep class names updated without needing full retraining.
    """
    old_path = os.path.join(DATASET_DIR, payload.old_name)
    new_path = os.path.join(DATASET_DIR, payload.new_name)

    if not os.path.exists(old_path):
        raise HTTPException(status_code=404, detail=f"Class directory '{payload.old_name}' not found.")

    if os.path.exists(new_path) and payload.old_name != payload.new_name:
        raise HTTPException(status_code=400, detail=f"Class directory '{payload.new_name}' already exists.")

    try:
        # Rename dataset folder
        os.rename(old_path, new_path)
        
        # If model is already trained, rename it inside model.pkl too!
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, "rb") as f:
                data = pickle.load(f)
            
            class_names = data["class_names"]
            if payload.old_name in class_names:
                # Replace class name
                idx = class_names.index(payload.old_name)
                class_names[idx] = payload.new_name
                data["class_names"] = class_names
                
                with open(MODEL_PATH, "wb") as f:
                    pickle.dump(data, f)
                    
                # Force cache update
                load_classifier()
        
        return {"status": "success", "message": f"Renamed class from {payload.old_name} to {payload.new_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rename class: {str(e)}")


@app.post("/delete-class")
def delete_class(payload: DeleteClassRequest):
    """
    Deletes the dataset directory for a class.
    Deletes the model.pkl file since the training configurations are no longer valid.
    """
    class_path = os.path.join(DATASET_DIR, payload.class_name)

    if not os.path.exists(class_path):
        raise HTTPException(status_code=404, detail=f"Class '{payload.class_name}' not found.")

    try:
        # Delete class directory
        shutil.rmtree(class_path)
        
        # Delete trained model since classes list has changed
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
            
        # Reset memory cache
        global _trained_model, _trained_classes, _model_mtime
        _trained_model = None
        _trained_classes = []
        _model_mtime = None
        
        return {"status": "success", "message": f"Deleted class '{payload.class_name}' and reset model."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete class: {str(e)}")


@app.post("/clear")
def clear_all():
    """
    Resets the workspace: deletes all uploaded images and the saved model.
    """
    global _trained_model, _trained_classes, _model_mtime
    _trained_model = None
    _trained_classes = []
    _model_mtime = None

    try:
        # Clear model file
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
            
        # Clear dataset directory
        if os.path.exists(DATASET_DIR):
            shutil.rmtree(DATASET_DIR)
        os.makedirs(DATASET_DIR, exist_ok=True)
        
        return {"status": "success", "message": "All workspace data cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
