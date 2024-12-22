from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)

# Load the model
with open('model.pkl', 'rb') as file:
    model = pickle.load(file)


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    # Example: Use data['image_path'] to load and preprocess an image
    # prediction = model.predict([processed_image])
    return jsonify({"prediction": "approved"})  # Replace with actual prediction


if __name__ == "__main__":
    app.run(debug=True)
