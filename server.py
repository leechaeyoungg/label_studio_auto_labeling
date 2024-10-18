from flask import Flask, request, jsonify
from ultralytics import YOLO
from PIL import Image
import io
import requests
import traceback
import json

app = Flask(__name__)

# 모델 경로 설정
model_path = r"C:\Users\dromii\Downloads\FOD10_agumented_best.pt"
model = YOLO(model_path)

# Label Studio 설정
LABEL_STUDIO_HOST = "http://127.0.0.1:8080"
API_TOKEN = "84809a8eede0a82b2e6d0ff439f9a9f6703afffe"

def send_predictions_to_label_studio(task_id, predictions):
    url = f"{LABEL_STUDIO_HOST}/api/tasks/{task_id}/annotations/"
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "model_version": "YOLOv8",
        "result": predictions
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 201:
        app.logger.error(f"Failed to send predictions to Label Studio: {response.status_code}, {response.text}")
    response.raise_for_status()

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/setup', methods=['POST'])
def setup():
    return jsonify({
        "label_config": """
        <View>
            <Image name="image" value="$image"/>
            <RectangleLabels name="label" toName="image">
                <Label value="Bolttrack_idkeyframe"/>
                <Label value="MetalParttrack_idkeyframe"/>
                <Label value="Nuttrack_idkeyframe"/>
                <Label value="PlasticParttrack_idkeyframe"/>
                <Label value="Rocktrack_idkeyframe"/>
                <Label value="Wiretrack_idkeyframe"/>
                <Label value="Woodtrack_idkeyframe"/>
                <Label value="Wrenchtrack_idkeyframe"/>
                <Label value="Brick"/>
                <Label value="paper"/>
                <Label value="balloon"/>
            </RectangleLabels>
        </View>
        """,
        "labels": {
            "Bolttrack_idkeyframe": "Bolttrack_idkeyframe",
            "MetalParttrack_idkeyframe": "MetalParttrack_idkeyframe",
            "Nuttrack_idkeyframe": "Nuttrack_idkeyframe",
            "PlasticParttrack_idkeyframe": "PlasticParttrack_idkeyframe",
            "Rocktrack_idkeyframe": "Rocktrack_idkeyframe",
            "Wiretrack_idkeyframe": "Wiretrack_idkeyframe",
            "Woodtrack_idkeyframe": "Woodtrack_idkeyframe",
            "Wrenchtrack_idkeyframe": "Wrenchtrack_idkeyframe",
            "Brick": "Brick",
            "paper": "paper",
            "balloon": "balloon"
        }
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        app.logger.info(f"Received data: {data}")
        tasks = data.get('tasks', [])
        predictions = []

        for task in tasks:
            task_id = task.get('id')
            image_url = task['data']['image']

            if not image_url.startswith("http"):
                image_url = LABEL_STUDIO_HOST + image_url

            headers = {"Authorization": f"Token {API_TOKEN}"}
            response = requests.get(image_url, headers=headers)
            if response.status_code != 200:
                raise ValueError(f"Failed to retrieve image from {image_url}, status code: {response.status_code}")

            image = Image.open(io.BytesIO(response.content))

            results = model.predict(image)
            boxes = results[0].boxes

            annotation_result = []
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                label = model.names[int(box.cls[0])]
                score = float(box.conf[0])
                annotation_result.append({
                    "from_name": "label",
                    "to_name": "image",
                    "type": "rectanglelabels",
                    "value": {
                        "x": (x1 / image.width) * 100,
                        "y": (y1 / image.height) * 100,
                        "width": ((x2 - x1) / image.width) * 100,
                        "height": ((y2 - y1) / image.height) * 100,
                        "rotation": 0
                    },
                    "score": score,
                    "label": [label]
                })

            send_predictions_to_label_studio(task_id, annotation_result)
            predictions.append({
                "result": annotation_result,
                "task_id": task_id
            })

        return jsonify(predictions)
    except Exception as e:
        app.logger.error(f"Error during prediction: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)




