from datetime import datetime
import dbAccessFunctions
import json
import os
from pathlib import Path
import requests

# Folder paths
current = os.getcwd()
BASE = Path(current).resolve().parent / "reflask"
image_folder = BASE / "night_img"
output_folder = BASE / "night_predict"
image_folder.mkdir(parents=True, exist_ok=True)
output_folder.mkdir(parents=True, exist_ok=True)

# Endpoint for batch predictions
url = "http://127.0.0.1:5000/predict_batch"


def batch_predict():
    processed_files = dbAccessFunctions.fetch_processed_files(dbAccessFunctions.db_configuration)
    files_to_process = [
        ('files', (file, open(os.path.join(image_folder, file), 'rb')))
        for file in os.listdir(image_folder)
        if file.endswith(('.jpg', '.png', '.jpeg')) and file not in processed_files
    ]

    if not files_to_process:
        print("No images to process.")
        return

    # Generating a file name with the current date
    date_stamp = datetime.now().strftime("%Y%m%d")
    output_file = output_folder / f"batch_results_{date_stamp}.json"

    # Sending files to the Flask app
    try:
        response = requests.post(url, files=files_to_process)
        if response.status_code == 200:
            # Saving results
            with open(output_file, 'w') as f:
                json.dump(response.json(), f, indent=4)
            print(f"Batch prediction results saved to {output_file}")
            # Marking files as processed
            for _, file_info in files_to_process:
                dbAccessFunctions.save_processed_file(dbAccessFunctions.db_configuration, file_info[0])
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Failed to process batch prediction: {e}")


if __name__ == "__main__":
    batch_predict()
