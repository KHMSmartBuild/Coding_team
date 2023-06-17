from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pickle
from Model_Deployment_Integration import ModelDeployer

app = FastAPI()

class ModelDeployer:
    # ... (keep the same class definition as in the previous script)
    def __init__(self, model):
        self.model = model

class InputData(BaseModel):
    features: List[float]

model_deployer = ModelDeployer(None)
model_deployer.load_model("trained_model.pkl")

@app.post("/predict")
def make_prediction(input_data: InputData):
    features = np.array(input_data.features).reshape(1, -1)
    prediction = model_deployer.make_prediction(features)
    return {"prediction": int(prediction[0])}

"This script sets up a simple FastAPI application with"
"an endpoint /predict that accepts POST requests with "
"input data in JSON format. The InputData class is a "
"Pydantic model that defines the expected input format."
"The script uses the same ModelDeployer class from the "
"previous script to handle the trained machine learning model."
"To use this script, you'll need to install FastAPI"
"and an ASGI server like uvicorn."