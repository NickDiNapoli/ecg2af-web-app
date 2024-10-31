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
    """
    Convert an ECG data file in HD5 format to a np.ndarray for  ECG2AF model input.
    """
    try:
        with h5py.File(ecg_file, 'r') as hd5:
            tensor = np.zeros(ecg_settings.ECG_SHAPE, dtype=np.float32)
            for lead in ecg_settings.ECG_REST_LEADS:
                data = np.array(hd5[f'{ecg_settings.ECG_HD5_PATH}/{lead}/instance_0'])
                tensor[:, ecg_settings.ECG_REST_LEADS[lead]] = data
            tensor -= np.mean(tensor)
            tensor /= np.std(tensor) + 1e-6
    except Exception as e:
        app.logger.error(f"Error processing ECG file: {e}")
        raise ValueError("Invalid ECG file format or corrupted file.")
    
    return tensor


def make_results_figures(predictions: List, pred_df: pd.DataFrame) -> Tuple:
    """
    Generate Plotly figures of the model's predictions.
    """
    # First figure: box plot for the first prediction output
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

    # Second figure: table of additional predictions
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
    """
    Render the welcome page for uploading the ECG data file.
    """
    return render_template("index.html")


@app.route('/predict', methods=['POST'])
def predict():
    """
    Process uploaded ECG file and display prediction results.
    """
    if "ecg_file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    ecg_file = request.files["ecg_file"]

    try:
        # Convert uploaded ECG data file to tensor
        ecg_tensor = ecg_as_tensor(ecg_file)
        
        # Load model and make predictions
        custom_dict = get_custom_objects([mgb_afib_wrt_instance2, age_2_wide, af_dummy, sex_dummy3])
        model = tf.keras.models.load_model("models/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5", custom_objects=custom_dict)
        predictions = model.predict(np.expand_dims(ecg_tensor, axis=0))

        # Prepare DataFrame for table display
        pred_df = pd.DataFrame({"prediction": [
                                predictions[1].flatten().tolist(),
                                predictions[2].flatten().tolist(),
                                predictions[3].flatten().tolist()
                                ]
        }, index=["pred_2", "pred_3", "pred_4"])
        
        # Generate results figures
        fig1, fig2 = make_results_figures(predictions, pred_df)

        # Convert figures to JSON for front-end display on predictions page
        fig1_json = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        fig2_json = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template("results.html", fig1_json=fig1_json, fig2_json=fig2_json)

    except ValueError as e:
        return jsonify({"ERROR": str(e)}), 400
    except tf.errors.OpError as e:
        app.logger.error(f"TensorFlow error: {e}")
        return jsonify({"ERROR": "An error occurred during model inference."}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"Error": "An unexpected error occurred. Please try again."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
