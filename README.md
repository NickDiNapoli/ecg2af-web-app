# ecg2af-web-app

## Setup on MacOS (M2)

If using poetry:
- `pip install poetry`
- `poetry lock`
- `poetry install`
- `poetry shell` 


If using docker + Git LFS: 
- `docker pull ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu`
- `git clone https://github.com/broadinstitute/ml4h.git`
- `brew install git-lfs`
- `git lfs install`
- `cd ml4h`
- `git lfs pull --include "model_zoo/ECG2AF/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5"`
- `docker run -it --rm --platform linux/amd64 -p 5000:5000 -v $(pwd):/app ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu /bin/bash`
- `pip install Flask`
- `cd /app`


If using pip + virtual env
- clone ecg2af_web_app repository
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `cd src/ecg2af_web_app/`

