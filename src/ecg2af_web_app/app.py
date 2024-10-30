from typing import List, Tuple
import h5py
import json
import numpy as np
import pandas as pd
import tensorflow as tf
import plotly
import plotly.graph_objs as go

import ecg2af_web_app.ecg_settings as ecg_settings

from flask import Flask, jsonify, render_template, request
from ml4h.models.model_factory import get_custom_objects
from ml4h.tensormap.ukb.survival import mgb_afib_wrt_instance2
from ml4h.tensormap.ukb.demographics import age_2_wide, af_dummy, sex_dummy3

app = Flask(__name__, template_folder="html_template")


def ecg_as_tensor(ecg_file: str) -> np.ndarray:
    with h5py.File(ecg_file, 'r') as hd5:
        tensor = np.zeros(ecg_settings.ECG_SHAPE, dtype=np.float32)
        for lead in ecg_settings.ECG_REST_LEADS:
            data = np.array(hd5[f'{ecg_settings.ECG_HD5_PATH}/{lead}/instance_0'])
            tensor[:, ecg_settings.ECG_REST_LEADS[lead]] = data
        tensor -= np.mean(tensor)
        tensor /= np.std(tensor) + 1e-6
    return tensor


def make_results_figures(predictions: List, pred_df: pd.DataFrame) -> Tuple:
    box_data = go.Box(
        y=predictions[0].flatten(),
        name='pred_1',
        boxmean='sd',
        marker=dict(color='blue'),
        boxpoints='all',
        pointpos=0
    )

    fig1 = go.Figure(data=[box_data])

    fig1.update_layout(
        title="Box Plot of First Predicted Output with Points Overlayed",
        yaxis_title="Values",
        xaxis_title="",
    )

    fig2 = go.Figure(data=[go.Table(
                    header=dict(values=["Output", "Prediction"], 
                                fill_color='lightblue', 
                                align='left'),
                    cells=dict(values=[pred_df.index, 
                                    pred_df['prediction']],
                                    fill_color='white', 
                                    align='left'))
    ])

    fig2.update_layout(title="Output of of Predictions 2-4")
    
    return fig1, fig2


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/predict', methods=['POST'])
def predict():
    if 'ecg_file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    ecg_file = request.files['ecg_file']
    ecg_tensor = ecg_as_tensor(ecg_file)
    
    custom_dict = get_custom_objects([mgb_afib_wrt_instance2, age_2_wide, af_dummy, sex_dummy3])
    model = tf.keras.models.load_model("models/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5", custom_objects=custom_dict)
    predictions = model.predict(np.expand_dims(ecg_tensor, axis=0))

    pred_df = pd.DataFrame({"prediction": [
                            predictions[1].flatten().tolist(),
                            predictions[2].flatten().tolist(),
                            predictions[3].flatten().tolist()
                            ]
    }, index=["pred_2", "pred_3", "pred_4"])
    
    fig1, fig2 = make_results_figures(predictions, pred_df)

    fig1_json = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    fig2_json = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    #print(render_template("results.html", fig1_json=fig1_json, fig2_json=fig2_json))

    return render_template("results.html", fig1_json=fig1_json, fig2_json=fig2_json)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
