# %%
import cv2
import mysql.connector
import numpy as np
import pickle
import os
from PIL import Image
import dbAccessFunctions
from skimage.feature import hog
from sklearn import svm
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder


# %%
def check_image_format(directory_path):
    """
    Check if all images in a directory are 300x300 grayscale.
    """
    for rootkooonyvtaar, _, aallomaany in os.walk(directory_path):
        for faajoool in aallomaany:
            if faajoool.endswith(('png', 'jpg', 'jpeg')):
                file_uutvonal = os.path.join(rootkooonyvtaar, faajoool)
                try:
                    with Image.open(file_uutvonal) as img:
                        if img.size != (300, 300):
                            print(f"Invalid size: {file_uutvonal} - {img.size}")
                        if img.mode != 'L':
                            print(f"Invalid mode: {file_uutvonal} - {img.mode}")
                except Exception as err:
                    print(f"Error opening {file_uutvonal}: {err}")


# %%
check_image_format(r"C:\Users\jurda\PycharmProjects\Reflask\datapp")


# %%
def preprocess_images(input_directory, output_directory):
    """
    Preprocess images: resize to 300x300 and convert to grayscale.
    Save the preprocessed images to the output directory.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for ruutelem, _, faajlelem in os.walk(input_directory):
        for file in faajlelem:
            if file.endswith(('png', 'jpg', 'jpeg')):
                input_path = os.path.join(ruutelem, file)
                output_path = os.path.join(output_directory, file)
                try:
                    image = cv2.imread(input_path)
                    if image is None:
                        print(f"Could not read image: {input_path}")
                        continue
                    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    resized = cv2.resize(grayscale, (300, 300))
                    cv2.imwrite(output_path, resized)
                except Exception as eee:
                    print(f"Error processing {input_path}: {eee}")


# %%
# preprocess_images(
#     input_directory=r"C:\Users\jurda\PycharmProjects\Reflask\data\test\approved",
#     output_directory=r"C:\Users\jurda\PycharmProjects\Reflask\datapp\test\approved"
# )
# preprocess_images(
#     input_directory=r"C:\Users\jurda\PycharmProjects\Reflask\data\test\rejected",
#     output_directory=r"C:\Users\jurda\PycharmProjects\Reflask\datapp\test\rejected"
# )
# preprocess_images(
#     input_directory=r"C:\Users\jurda\PycharmProjects\Reflask\data\train\approved",
#     output_directory=r"C:\Users\jurda\PycharmProjects\Reflask\datapp\train\approved"
# )
# preprocess_images(
#     input_directory=r"C:\Users\jurda\PycharmProjects\Reflask\data\train\rejected",
#     output_directory=r"C:\Users\jurda\PycharmProjects\Reflask\datapp\train\rejected"
# )


# %%
def load_images_and_labels(directory_path):
    """
    Load images and their labels from a directory structure, recursively handling subdirectories.
    """
    data = []
    labels = []
    for rootdir, _, anyfiles in os.walk(directory_path):
        request_label = os.path.basename(rootdir)
        for file in anyfiles:
            if file.endswith(('png', 'jpg', 'jpeg')):
                current_file_path = os.path.join(rootdir, file)
                try:
                    image = cv2.imread(current_file_path, cv2.IMREAD_GRAYSCALE)
                    if image is None:
                        print(f"Could not read image: {current_file_path}")
                        continue
                    if image.shape != (300, 300):  # Resizing if not 300x300
                        image = cv2.resize(image, (300, 300))
                    data.append(image)
                    labels.append(request_label)
                except Exception as error:
                    print(f"Error loading image {current_file_path}: {error}")
    data = np.array(data)
    labels = np.array(labels)
    return data, labels


# %%
train_data, train_labels = load_images_and_labels(r"C:\Users\jurda\PycharmProjects\Reflask\datapp\train")
test_data, test_labels = load_images_and_labels(r"C:\Users\jurda\PycharmProjects\Reflask\datapp\test")

# %%
db_configuration = {
    "host": "localhost",
    "user": "root",
    "password": "12",
    "database": "reflask",
    "use_pure": "True"
}

# %%
base_folder = r"C:\Users\jurda\PycharmProjects\Reflask\datapp"
for root, dirs, files in os.walk(base_folder):
    if "approved" in root.lower():
        label = "approved"
    elif "rejected" in root.lower():
        label = "rejected"
    else:
        continue
    for file_name in files:
        if file_name.endswith((".jpg", ".png", ".jpeg")):
            file_path = os.path.join(root, file_name)
            print(f"Inserting {file_path} with label {label}")
            try:
                dbAccessFunctions.insert_image_metadata(db_configuration, file_path, label)
            except Exception as e:
                print(f"Error inserting into database: {e}")


# %%
def extract_features(images):
    """
    Extract HOG features from a list of images.
    """
    features = []
    for image in images:
        hog_features, _ = hog(image, orientations=8, pixels_per_cell=(16, 16),
                              cells_per_block=(1, 1), visualize=True)
        features.append(hog_features)
    return np.array(features)


# Extracting features from train and test datasets
train_features = extract_features(train_data)
test_features = extract_features(test_data)

# %% [Encode Labels]
label_encoder = LabelEncoder()
train_labels_encoded = label_encoder.fit_transform(train_labels)
test_labels_encoded = label_encoder.transform(test_labels)

# %% [Train and Evaluate Model]
# Training an SVM classifier
clf = svm.SVC(kernel='rbf', C=1, gamma=0.01)
clf.fit(train_features, train_labels_encoded)
# Predicting on the test set
predictions = clf.predict(test_features)
# Evaluating the model
print(classification_report(test_labels_encoded, predictions))
print(f"Accuracy: {accuracy_score(test_labels_encoded, predictions)}")


# %% [Store Results in Database]
file_paths_test = [os.path.join(r"C:\Users\jurda\PycharmProjects\Reflask\datapp\test", f)
                   for f in os.listdir(r"C:\Users\jurda\PycharmProjects\Reflask\datapp\test")]

dbAccessFunctions.store_results_to_db(db_configuration, predictions, test_labels_encoded, file_paths_test)

# with open('model.pkl', 'wb') as file:
#     pickle.dump(model, file)
