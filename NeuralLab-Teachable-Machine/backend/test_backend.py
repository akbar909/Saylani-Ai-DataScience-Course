import os
import shutil
import numpy as np
from PIL import Image

# Import backend modules
import main
from main import (
    DATASET_DIR, 
    MODEL_PATH, 
    TrainRequest, 
    train_model, 
    get_feature_vector, 
    load_classifier
)

def create_solid_image(color, filename):
    """
    Creates a solid color 224x224 image and saves it.
    """
    img = Image.new("RGB", (224, 224), color=color)
    img.save(filename)
    return filename

def run_tests():
    print("=== NeuralLab Backend Verification ===")
    
    # 1. Clean workspace
    print("\n1. Cleaning up existing test folders...")
    if os.path.exists(DATASET_DIR):
        shutil.rmtree(DATASET_DIR)
    os.makedirs(DATASET_DIR, exist_ok=True)
    if os.path.exists(MODEL_PATH):
        os.remove(MODEL_PATH)

    # 2. Generate mock image samples
    # We will create two classes: 'RedClass' and 'BlueClass'
    print("\n2. Creating mock image samples (solid Red and solid Blue)...")
    red_dir = os.path.join(DATASET_DIR, "RedClass")
    blue_dir = os.path.join(DATASET_DIR, "BlueClass")
    os.makedirs(red_dir, exist_ok=True)
    os.makedirs(blue_dir, exist_ok=True)
    
    # Create 5 red images and 5 blue images
    for i in range(5):
        create_solid_image((255, 0, 0), os.path.join(red_dir, f"red_{i}.jpg"))
        create_solid_image((0, 0, 255), os.path.join(blue_dir, f"blue_{i}.jpg"))
        
    print(f"Created Class RedClass inside {red_dir}")
    print(f"Created Class BlueClass inside {blue_dir}")

    # 3. Test Feature Extraction
    print("\n3. Testing MobileNetV3 feature extraction...")
    test_img = os.path.join(red_dir, "red_0.jpg")
    features = get_feature_vector(test_img)
    print(f"Successfully extracted features from {test_img}")
    print(f"Feature Vector shape: {features.shape} (Expected: (576,))")
    assert features.shape == (576,), "Feature vector shape mismatch"

    # 4. Run Training Engine
    print("\n4. Triggering local training engine...")
    req = TrainRequest(c_value=1.0, max_iter=100)
    res = train_model(req)
    print("Training result:", res)
    assert res["status"] == "success", "Training failed"
    assert os.path.exists(MODEL_PATH), "model.pkl was not saved!"
    print("Successfully saved model.pkl")

    # 5. Load and Verify Model
    print("\n5. Verifying trained model loading...")
    classifier, class_names = load_classifier()
    print("Loaded classes:", class_names)
    assert "RedClass" in class_names and "BlueClass" in class_names, "Classes not loaded correctly"
    print("Model loaded successfully.")

    # 6. Run Predictions
    print("\n6. Running prediction tests...")
    # Test Red Image
    red_test = create_solid_image((230, 20, 20), "temp_red_test.jpg") # slight variations in red
    features_red = get_feature_vector(red_test).reshape(1, -1)
    probs_red = classifier.predict_proba(features_red)[0]
    pred_idx_red = classifier.predict(features_red)[0]
    winning_class_red = class_names[pred_idx_red]
    
    print(f"Red image prediction probabilities:")
    for name, p in zip(class_names, probs_red):
        print(f"  - {name}: {p * 100:.2f}%")
    print(f"Winning Class: {winning_class_red} (Expected: RedClass)")
    
    # Test Blue Image
    blue_test = create_solid_image((20, 20, 230), "temp_blue_test.jpg") # slight variations in blue
    features_blue = get_feature_vector(blue_test).reshape(1, -1)
    probs_blue = classifier.predict_proba(features_blue)[0]
    pred_idx_blue = classifier.predict(features_blue)[0]
    winning_class_blue = class_names[pred_idx_blue]
    
    print(f"Blue image prediction probabilities:")
    for name, p in zip(class_names, probs_blue):
        print(f"  - {name}: {p * 100:.2f}%")
    print(f"Winning Class: {winning_class_blue} (Expected: BlueClass)")

    # Clean up temp test files
    os.remove(red_test)
    os.remove(blue_test)
    print("\nCleaned up temp test files.")

    # Assert correctness
    assert winning_class_red == "RedClass", "Failed to predict RedClass for red image"
    assert winning_class_blue == "BlueClass", "Failed to predict BlueClass for blue image"
    
    print("\n=== ALL BACKEND UNIT TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
