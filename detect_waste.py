import os
from pathlib import Path
import numpy as np
import tensorflow as tf
from PIL import Image

try:
    from pillow_heif import register_heif
    register_heif()
except Exception:
    pass

MODEL_PATH = os.path.join("models", "waste_classifier.h5")
CLASS_NAMES = ["e-waste", "glass", "metal", "organic", "paper", "plastic"]

print("[INFO] Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("[INFO] Model loaded successfully!")

def preprocess_image(image_path, target_size=(224, 224)):
    p = Path(image_path)
    if not p.exists():
        raise FileNotFoundError(f"Path does not exist: {p}")
    try:
        img = Image.open(p).convert("RGB")
    except Exception as e:
        raise ValueError(f"Could not open image (unsupported/corrupt): {p}\n{e}")
    img = img.resize(target_size)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)

def detect_waste(image_path):
    x = preprocess_image(image_path)
    preds = model.predict(x)
    idx = int(np.argmax(preds))
    conf = float(np.max(preds))
    print(f"\n[RESULT] Predicted class: {CLASS_NAMES[idx]}")
    print(f"[CONFIDENCE] {conf*100:.2f}%")
    return CLASS_NAMES[idx], conf

if __name__ == "__main__":
    raw = input("Enter the path to an image: ").strip()
    raw = raw.strip('"').strip("'")
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = Path(os.getcwd()) / p
    p = p.resolve()
    print(f"[INFO] Using image: {p}")
    detect_waste(str(p))
python - <<'PY'
from PIL import Image, ImageDraw
im = Image.new('RGB', (224,224), 'white')
d = ImageDraw.Draw(im)
d.rectangle((40,40,180,180), outline='black', width=8)
d.text((60,95), "TEST", fill='black')
im.save('sample.jpg')
print("Wrote sample.jpg")
