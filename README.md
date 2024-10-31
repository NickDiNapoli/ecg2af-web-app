# ecg2af-web-app

## Setup on MacOS

**Note**: ***I highly recommend <u>not</u> using an M2 chip Mac machine when trying to use the ml4h image***. There are many issues that arise with how TensorFlow gets built. Resolving how it gets built often causes incompatibility issues between Python version, `tensorflow`, and `tensorflow-<xxx>` libraries.

Initial setup steps:
- `git clone https://github.com/NickDiNapoli/ecg2af-web-app.git`
- `git clone https://github.com/broadinstitute/ml4h.git`
- If needed:
  - `brew install git-lfs`
  - `git lfs install`
- `cd ml4h`
- `git lfs pull --include "model_zoo/ECG2AF/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5"`

If using existing Docker image (I used for application):
- `cd ecg2af-web-app`
- `docker pull ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu`
- (change the model path to wherever you have it stored locally which is likely: ml4h/model_zoo/ECG2AF/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5) `docker run -it --rm -p 5001:5001 -v $(pwd):/app -v /Users/bellaluciani/Downloads/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5:/app/src/ecg2af_web_app/models/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5 ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu /bin/bash`
- `pip install .`
- `pip install -r requirements.txt`
- `cd src/ecg2af_web_app/`
- `python app.py`

If using Poetry (I used for running local ipynb):
- `pip install poetry`
- `poetry lock`
- if `poetry lock` fails with ml4h included in the dependencies, comment out the dependency
- `poetry install`
- `poetry shell` 
- if ml4h still needs to be installed: 
    - `pip install -r requirements.txt` OR
    - `cd ml4h` and `pip install .`
- select .venv for kernel

### Alternative approaches

If building Docker image:
- clone ecg2af_web_app repository
- `cd ecg2af-web-app`
- `docker build -t ecg2af-web-app .`
- `docker run -it ecg2af-web-app`
- (again change the model path to wherever you have it stored locally) `docker run -it --rm -p 5001:5001 -v $(pwd):/app -v /Users/nickdinapoli/Downloads/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5:/app/src/ecg2af_web_app/models/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5 ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu /bin/bash`
- `cd src/ecg2af_web_app/`
- `python app.py`

If using pip + virtual env
- clone ecg2af_web_app repository
- clone ml4h repository
- ensure you are using Python 3.8.10 (same as ml4h image)
- `python3 -m venv venv`
- `source venv/bin/activate`
- install ml4h project
  - Ex: `pip install -r requirements.txt` OR `cd ml4h` and then `pip install .`


## Application Usage

Once you have ran `python app.py`, the first HTTP address will navigate you to a simple welcome page seen below:

![welcome_page](images/welcome_page.png)

Click the "Choose File" button and upload the sample ECG data (`fake_0.hd5`) from wherever it is stored locally. Click the "Predict" button to run inference on the data. The page will update automatically with the prediction results as seen below. 

![results_page](images/results_page.png)

The figures are both interactive for an enhanced user experience. The user can click the boxplot and immediate receive some key statistics about the results as seen here:

![interactive_results](images/interactive_results.png)

Using the back button in your browser will allow the welcome page to reload if you wish to run inference using another ECG file. 