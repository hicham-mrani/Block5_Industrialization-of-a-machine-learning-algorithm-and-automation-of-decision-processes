import uvicorn
from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel
from typing import Union
import joblib
import json

# description will apear in the doc
description = """
![GetAround](https://lever-client-logos.s3.amazonaws.com/2bd4cdf9-37f2-497f-9096-c2793296a75f-1568844229943.png)
\n\n
[GetAround](https://www.getaround.com/?wpsrc=Google+Organic+Search) is the Airbnb for cars. You can rent cars from any person for a few hours to a few days! Founded in 2009,
this company has known rapid growth. In 2019, they count over 5 million users and about 20K available cars worldwide.
\n\n
The goal of Getaround API is to serve data that help users estimate daily rental value of their car.

## Preview

* `/preview` a some random rows in the historical record

## ML-Model-Prediction
 
* `/predict` insert your car details to receive an AI-based estimation on daily rental car price.

"""

# tags to identify different endpoints
tags_metadata = [
    {
        "name": "Preview",
        "description": "Preview the random cases in dataset",
    },

    {
        "name": "ML-Model-Prediction",
        "description": "Estimate rental price based on machine learning model trained with historical data and XGBoost algorithm"
    }
]

app = FastAPI(
    title="🚗 Getaround API",
    description=description,
    version="1.0",
    contact={
        "name": "My GitHub",
        "url": "https://github.com/hicham-mrani",
    },
    openapi_tags=tags_metadata
)


class PredictionFeatures(BaseModel):
    model_key: str
    mileage: Union[int, float]
    engine_power: Union[int, float]
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool


@app.get("/", tags=["Preview"])
async def random_data(rows: int = 5):
    fname = "https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv"
    df = pd.read_csv(fname, index_col=0, low_memory=False)
    sample = df.sample(rows)
    response = sample.to_json(orient='records')
    return response

# preparing labels that will be replaced as other
list_model_other = ['Maserati', 'Suzuki', 'Porsche', 'Ford',
                    'KIA Motors', 'Alfa Romeo', 'Fiat',
                    'Lexus', 'Lamborghini', 'Mini', 'Mazda',
                    'Honda', 'Yamaha', 'Other']

list_fuel_other = ['hybrid_petrol', 'electro', 'other']

list_color_other = ['green', 'orange', 'other']


def other_re(x, list_):
    y = x
    if x in list_:
        y = 'others'
    return y


msg = """ 
    Error! PLease check your input. It should be in json format. Example input:\n\n
    "model_key": "Volkswagen",\n
    "mileage": 17500,\n
    "engine_power": 190,\n
    "fuel": "diesel",\n
    "paint_color": "black",\n
    "car_type": "convertible",\n
    "private_parking_available": true,\n
    "has_gps": true,\n
    "has_air_conditioning": true,\n
    "automatic_car": true,\n
    "has_getaround_connect": true,\n
    "has_speed_regulator": true,\n
    "winter_tires": true\n
    """


@app.post("/predict", tags=["ML-Model-Prediction"])
async def predict(predictionFeatures: PredictionFeatures):
    """
    Prediction for single set of input variables. Possible input values in order are:\n\n
    model_key: str\n
    mileage: float\n
    engine_power: float\n
    fuel: str\n
    paint_color: str\n
    car_type: str\n
    private_parking_available: bool\n
    has_gps: bool\n
    has_air_conditioning: bool\n
    automatic_car: bool\n
    has_getaround_connect: bool\n
    has_speed_regulator: bool\n
    winter_tires: bool\n\n

    Endpoint will return a dictionnary like this:
    \n\n
    ```
    {'prediction': rental_price_per_day}
    ```
    \n\n
    You need to give this endpoint all columns values as a dictionnary, or a form data.
    becarefull to fill with true and not True with cap
    """
    if predictionFeatures.json:
        # Printing JSON as dictionnary for user to check variables
        df = pd.DataFrame(dict(predictionFeatures), index=[0])
        preprocess = joblib.load('preprocessor.joblib') # preprocessing model
        regressor = joblib.load('model.joblib') # random forest model

        df['model_key'] = df['model_key'].apply(
            lambda x: other_re(x, list_model_other))
        df['fuel'] = df['fuel'].apply(lambda x: other_re(x, list_fuel_other))
        df['paint_color'] = df['paint_color'].apply(
            lambda x: other_re(x, list_color_other))

        try:
            X_val = preprocess.transform(df.head(16))
            Y_pred = regressor.predict(X_val)
            # Return the result as JSON but first we need to transform the
            response = {'Predicted rental price per day in dollars': round(Y_pred.tolist()[0], 1)}
        except:
            response = json.dumps({"message": msg})
        return response
    else:
        msg = json.dumps({"message": msg})
        return msg

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, debug=True, reload=True)
