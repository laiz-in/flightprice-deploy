from flask import Flask, request, render_template
import pandas as pd
from datetime import datetime
from flask_cors import cross_origin
import dill


app = Flask(__name__)


#============================================================   LOADING MODEL AND PREPROCESSOR    ============================================================================================

with open('models/preprocessor.pkl', 'rb') as file:
    preprocessor = dill.load(file)
with open('models/random_forest_model.pkl', 'rb') as file:
    model = dill.load(file)


#=================================================================   LOADING HOME PAGE    ============================================================================================

@app.route("/")
@cross_origin()
def home():
    return render_template("home.html")

#====================================================================== PREDICT METHOD ===================================================================================
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

#===================================================================  CREATING THE DATAFRAME ===============================================================================
          
            custom_data_input_dict = {
                "Airline": Airline,
                "Classes": Classes,
                "Source": Source,
                "Departure": Departure,
                "Total_stops":Total_stops,
                "Arrival": Arrival,
                "Destination":Destination,
                "Duration_in_hours": Duration_in_hours,
                "Days_left": Days_left,
                "Year": Year,
                "Month": Month,
                "Day": Day,
                "Day_of_week":Day_of_week,
            }
            dataframe = pd.DataFrame(custom_data_input_dict,index=[0])

        except Exception as e:
            pass
        try:          
            data_Scaled = preprocessor.transform(dataframe)
            prediction =model.predict(data_Scaled)
            result = abs(int(prediction[0]))
        except:
            pass
        results = f"Approximate fare: INR {result}"
        return render_template('home.html',prediction_text=results)
    else:
        return render_template("home.html")



if __name__ == "__main__":
    app.run(debug=True)