from flask import Flask, request, render_template
from src import data_ingestion
from src.data_transformation import DataTransformation
import pickle
import pandas as pd
from src.logger import logging
from src.exception import CustomException
from datetime import datetime
import sys
from flask_cors import cross_origin
from src.predict_pipeline import PredictPipeline, CustomData
app = Flask(__name__)


@app.route("/")
@cross_origin()
def home():
    return render_template("home.html")


@app.route("/predict", methods = ["GET", "POST"])
@cross_origin()
def predict():
    if request.method == "POST":
        try:
            result=" "
            # Date_of_Journey
            date_dep = request.form["Dep_Time"]
            Day = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").day)
            Month = int(pd.to_datetime(date_dep, format ="%Y-%m-%dT%H:%M").month)
            Dep_hour = int(pd.to_datetime(date_dep, format ="%Y-%m-%dT%H:%M").hour)
            Year = int(pd.to_datetime(date_dep, format ="%Y-%m-%dT%H:%M").year)
            Day_of_week = int(pd.to_datetime(date_dep, format ="%Y-%m-%dT%H:%M").day_of_week)

            
            #classifying the time object to our departure classes
            if Dep_hour >= 18 or Dep_hour < 6:
                Departure = 'After 6 PM'
            elif Dep_hour >= 12 and Dep_hour < 18:
                Departure = '12 PM - 6 PM'
            elif Dep_hour >= 6 and Dep_hour < 12:
                Departure = '6 AM - 12 PM'
            else:
                Departure = 'Before 6 AM'
                
            #classifying the time object to our departure classes
            if Dep_hour >= 18 or Dep_hour < 6:
                Arrival = 'After 6 PM'
            elif Dep_hour >= 12 and Dep_hour < 18:
                Arrival = '12 PM - 6 PM'
            elif Dep_hour >= 6 and Dep_hour < 12:
                Arrival = '6 AM - 12 PM'
            else:
                Arrival = 'Before 6 AM'

            # Calculate the number of days left until the departure date
            date_dep_for = datetime.strptime(date_dep, '%Y-%m-%dT%H:%M')
            Days_left = ((date_dep_for - datetime.now()).days)+1


            Duration_in_hours = request.form['Duration']
            Total_stops = (request.form["stops"])
            Airline=request.form['Airline']
            Classes=request.form['Classes']
            Source = request.form["Source"]
            Destination = request.form["Destination"]

            data = CustomData(
            Airline,
            Classes,
            Source,
            Departure,
            Total_stops,
            Arrival,
            Destination,
            Duration_in_hours,
            Days_left,
            Year,
            Month,
            Day,
            Day_of_week
            )
            logging.info("dataframe is created on the basis of user input")
        except Exception as e:
            raise CustomException(e,sys)
        try:          
            pred_df=data.get_data_as_data_frame()
            predict_pipeline=PredictPipeline()
            results=predict_pipeline.predict(pred_df)
            logging.info("predicted the output")
            result= int(results[0])
            result=abs(result)
            logging.info("prediction reached the app.py")
        except Exception as e:
            raise CustomException(e,sys)
          
        results = f"Approximate fare: INR {result}"
        return render_template('home.html',prediction_text=results)
    return render_template("home.html")



if __name__ == "__main__":
    app.run(debug=True)