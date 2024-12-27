from flask import Flask, request, jsonify
import pickle
import numpy as np
import cv2
import os
from PIL import Image
import io
import logging
from skimage.feature import hog

logging.basicConfig(level=logging.INFO)

# Starting the app
app = Flask(__name__)

# Loading the model
with open('modell.pkl', 'rb') as file:
    model = pickle.load(file)


def preprocess_image(image):
    """
    Preprocess the input image for the model:
    - Convert to grayscale
    - Resize to 300x300 pixels
    - Extract HOG features
    Parameters:
    - image: PIL.Image.Image, the input image.
    Returns:
    - A NumPy array of the preprocessed image (HOG features).
    """
    # Convert image to OpenCV format
    image_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # Convert to grayscale
    grayscale = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
    # Resize to 300x300
    resized = cv2.resize(grayscale, (300, 300))
    # Extract HOG features
    hog_features, _ = hog(resized, orientations=8, pixels_per_cell=(16, 16),
                          cells_per_block=(1, 1), visualize=True)
    return np.expand_dims(hog_features, axis=0)


def preprocess_images_batch(image_list):
    """
    Preprocess a batch of images for the model:
    - Convert to grayscale
    - Resize to 300x300
    - Extract HOG features
    Parameters:
    - image_list: List of PIL.Image.Image
    Returns:
    - A NumPy array of HOG features for the batch.
    """
    logging.info(f"Received {len(image_list)} files for batch prediction.")
    preprocessed_images = []
    for image in image_list:
        try:
            # Converting PIL image to OpenCV format
            image_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            grayscale = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(grayscale, (300, 300))
            # Extracting HOG features
            hog_features, _ = hog(resized, orientations=8, pixels_per_cell=(16, 16),
                                  cells_per_block=(1, 1), visualize=True)
            preprocessed_images.append(hog_features)
        except Exception as e:
            logging.error(f"Error processing image: {str(e)}")
            raise ValueError(f"Error in preprocessing batch: {str(e)}")
    # Returning as a NumPy array
    return np.array(preprocessed_images)


# Adding functionality to enable getting predictions
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        # Checking if file is in raw binary (e.g., from Postman binary upload)
        file = request.get_data()
        if not file:
            return jsonify({"error": "No file provided"}), 400
        try:
            image = Image.open(io.BytesIO(file))
            preprocessed_image = preprocess_image(image)
            print(f"Input shape for model: {preprocessed_image.shape}")
            prediction = model.predict(preprocessed_image)
            # Convert prediction to a Python list
            predicted_label = prediction.tolist()
            return jsonify({"Predicted label": predicted_label})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    try:
        # Opening the uploaded image file
        image = Image.open(io.BytesIO(file.read()))
        # Preprocessing the image
        preprocessed_image = preprocess_image(image)
        print(f"Input shape for model: {preprocessed_image.shape}")
        # Making prediction
        prediction = model.predict(preprocessed_image)
        # Convert prediction to a Python list
        predicted_label = prediction.tolist()
        if predicted_label[0] == 0:
            label_to_output = "approved"
        elif predicted_label[0] == 1:
            label_to_output = "rejected"
        else:
            label_to_output = "unknown"
        return jsonify({"The refund request should be": label_to_output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/predict_batch', methods=['POST'])
def predict_batch():
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files provided"}), 400
    try:
        images = []
        for file in files:
            if file.filename == '':
                return jsonify({"error": "One or more files are missing filenames"}), 400
            try:
                images.append(Image.open(io.BytesIO(file.read())))
            except Exception as e:
                return jsonify({"error": f"Error processing one of the files: {str(e)}"}), 400
        preprocessed_images = preprocess_images_batch(images)
        print(f"Batch input shape for model: {preprocessed_images.shape}")
        predictions = model.predict(preprocessed_images)
        # Converting predictions to human-readable labels
        predicted_labels = predictions.tolist()
        label_mapping = {0: "approved", 1: "rejected"}
        # Handle predictions based on their shape
        friendly_labels = [
            label_mapping.get(int(pred[0]) if isinstance(pred, (list, np.ndarray)) else int(pred), "unknown")
            for pred in predicted_labels
        ]
        # Returning results with both raw predictions and user-friendly labels
        return jsonify({
            "Batch results": [
                {"File": files[idx].filename, "Raw prediction": predicted_labels[idx], "Decision": friendly_labels[idx]}
                for idx in range(len(files))
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
