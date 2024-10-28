import h5py
import numpy as np
import tensorflow as tf

import ecg2af_web_app.ecg_settings as ecg_settings

from flask import Flask, jsonify, render_template, request

#app = Flask(__name__)
app = Flask(__name__, template_folder="html_template")


def ecg_as_tensor(ecg_file):
        with h5py.File(ecg_file, 'r') as hd5:
            tensor = np.zeros(ecg_settings.ECG_SHAPE, dtype=np.float32)
            for lead in ecg_settings.ECG_REST_LEADS:
                data = np.array(hd5[f'{ecg_settings.ECG_HD5_PATH}/{lead}/instance_0'])
                tensor[:, ecg_settings.ECG_REST_LEADS[lead]] = data
            tensor -= np.mean(tensor)
            tensor /= np.std(tensor) + 1e-6
        return tensor


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/predict', methods=['POST'])
def predict():
    if 'ecg_file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    ecg_file = request.files['ecg_file']
    ecg_tensor = ecg_as_tensor(ecg_file)  # function provided in the prompt
    
    # Load model and make prediction
    model = tf.keras.models.load_model("/app/ml4h/model_zoo/ECG2AF/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5")
    predictions = model.predict(np.expand_dims(ecg_tensor, axis=0))
    
    # Return predictions as JSON
    return jsonify({
        "prediction_1": float(predictions[0][0]),
        "prediction_2": float(predictions[0][1]),
        "prediction_3": float(predictions[0][2]),
        "prediction_4": float(predictions[0][3])
    })
