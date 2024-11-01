# ecg2af-web-app

# Getting Started
* [Setup on MacOS](#setup-on-macos)
* [Application Usage](#application-usage)
* [Scalability Question](#scalability-question)
* [Use of external resources](#use-of-external-resources)

## Setup on MacOS

***Note: I highly recommend <u>not</u> using an M2 chip Mac machine when trying to use the ml4h image***. There are many issues that arise with how TensorFlow gets built. Resolving how it gets built often causes incompatibility issues between Python version, `tensorflow`, and `tensorflow-<xxx>` libraries. You will likely encounter a message like the one below: 

***The TensorFlow library was compiled to use AVX instructions, but these aren't available on your machine. Aborted***

### Initial setup steps:
Clone this project from GitHub:
```
git clone https://github.com/NickDiNapoli/ecg2af-web-app.git
```
Clone the ML4H repository from GitHub:
```
git clone https://github.com/broadinstitute/ml4h.git
```
If needed, complete the following two steps. Installs Git Large File Storage (LFS) on your system using Homebrew:
```
brew install git-lfs
```
Set up Git to use Git LFS:
```
git lfs install
```
Migrate into the ml4h directory:
```
cd ml4h
```
Tell Git LFS to download only the specified model file:
```
git lfs pull --include "model_zoo/ECG2AF/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5"
```

### If using existing Docker image (I used for application):
Migrate into the ecg2af-web-app directory:
```
cd ecg2af-web-app
```
Pull the ML4H Docker image:
```
docker pull ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu
```
Run the Docker container and mount both the this ecg2af-web-app project as well as the ECG2AF model. Change the model path to wherever you have it stored locally which is likely: ml4h/model_zoo/ECG2AF/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5
```
docker run -it --rm -p 5001:5001 -v $(pwd):/app -v /Users/nickdinapoli/Downloads/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5:/app/src/ecg2af_web_app/models/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5 ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu /bin/bash
```
Install this (ecg2af-web-app) Python project:
```
pip install .
```
Install additional dependencies from requirements file:
```
pip install -r requirements.txt
```
Migrate into the directory which contains the application:
```
cd src/ecg2af_web_app/
```
Run the application using Python:
```
python app.py
```

### If using Poetry (I used for running local ipynb):
Install Poetry on machine if it is not already:
```
pip install poetry
```
Update `poetry.lock` file based on the dependencies in `pyproject.toml`. If `poetry lock` fails with ml4h included in the dependencies, comment out the dependency:
```
poetry lock
```
Install the dependencies in the `poetry.lock` file:
```
poetry install
```
Open new shell with activated virtual environment that Poetry has created:
```
poetry shell
```
If ml4h still needs to be installed, complete one the following two steps: 
```
pip install -r requirements.txt
``` 
OR:
```
cd ml4h
``` 
and then
```
pip install .
```
Select `.venv` for the kernel.

### Alternative approaches

### If building Docker image:
Clone ecg2af_web_app repository
```
cd ecg2af-web-app
```
```
docker build -t ecg2af-web-app .
```
```
docker run -it ecg2af-web-app
```
Again change the model path to wherever you have it stored locally. 
```
docker run -it --rm -p 5001:5001 -v $(pwd):/app -v /Users/nickdinapoli/Downloads/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5:/app/src/ecg2af_web_app/models/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5 ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu /bin/bash
```
```
cd src/ecg2af_web_app/
```
```
python app.py
```

### If using pip + virtual env
- Clone ecg2af_web_app repository
- Clone ml4h repository
- Ensure you are using Python 3.8.10 (same as ml4h image)
```
python3 -m venv venv
```
```
source venv/bin/activate
```
Install ml4h project:
```
pip install -r requirements.txt
``` 
OR: 
```
cd ml4h
```
and then 
```
pip install .
```

## Application Usage

For this project I chose to use to use Flask as the web framework for a few reasons. I do not have a ton of prior experience with web applications so I went with Flask because of its simplicity and because I had used it once or twice in my Master's coursework. 

Once you have ran `python app.py`, the first HTTP address will navigate you to a simple welcome page seen below:

![welcome_page](images/welcome_page.png)

Click the "Choose File" button and upload the sample ECG data (`fake_0.hd5`) from wherever it is stored locally. Click the "Predict" button to run inference on the data. The page will update automatically with the prediction results as seen below. 

![results_page](images/results_page.png)

The figures are both interactive for an enhanced user experience. The user can hover over the boxplot and immediately receive some key statistics about the results as seen here:

![interactive_results](images/interactive_results.png)

Using the back button in your browser will allow the welcome page to reload if you wish to run inference using another ECG file. 


## Scalability Question

*Explain how you would scale the solution to allow analysis of a larger volume of data (e.g., 10,000 ECGs) and accommodate more users.*

My first impression is to use cloud resources/tools. If the application is deployed on a cloud platform, the scaling of microservices and batch processing might be greatly simplified. For me in my experience with AWS ECR + Batch, I would re-write the application to accept many datasets and distrubute jobs amongst all available proceeses. I would also decouple the data pre processing and model inference steps into different modules/services which could provide additional speed up. Additional ideas that I have implemented in the past is model caching which allows for lower latency and efficient handling of jobs/requests. Lastly, I could also re-write the model inference to take further advantage of GPUs and batch processing. After my first impression comes a bit of research, and based on this research, I see that two more ideas for handling larger volumes of data are async processing as well as database optimization. If a proper database is set up to store datsets, predictions, and metadata, a more sound database might allow for quicker read/write of this data. 

## Use of external resources

I used ChatGPT to help build the HTML files as well as route the interactive plots through these pages as I have a little less experience with front-end. I also leveraged it to assist with setting up the proper Flask decorators. 