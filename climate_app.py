import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, text

from flask import Flask, jsonify
from cgi import escape

#Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# create our session link from python to the db
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Home route
@app.route("/")
def welcome():
    return (
        f"<html><body><h1>Welcome to my Climate Application API!</h1><br/>"
        f"<h2>Available Routes:</h2><br/></body></html>"
        f"/api/precipitation<br/>"
        f"/api/stations<br/>"
        f"/api/temperature<br/>"
        f"/api/daterange/" + escape("<start_date>") + "<br/>"
        f"/api/daterange/" + escape("<start_date>") + "/" + escape("<end_date>") + "<br/></br>"
        f"<i>*Please note that temperature data is only available from 2010-01-01 thru 2017-08-23.</i>"
    )

# Precipitation route
@app.route("/api/precipitation")
def precipitation_last_recorded_yr():
    # Calculate the date 1 year ago from the last data point in the database
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    query_date = dt.datetime.strptime(max_date, '%Y-%m-%d')  - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).\
        order_by(Measurement.date).all()

    all_precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        all_precip.append(precip_dict)

    return jsonify(all_precip)

# Stations route
@app.route("/api/stations")
def all_stations():
    # I chose to list the station names, not numbers
    stations = session.query(Station.name).all()
    all_stations = list(np.ravel(stations))
    return jsonify(all_stations)

# Temperature route
@app.route("/api/temperature")
def temp_observations_last_recorded_yr():
    # Query the last 12 months of temperature observation data
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    query_date = dt.datetime.strptime(max_date, '%Y-%m-%d')  - dt.timedelta(days=366)

    # Perform a query to retrieve the date and tobs
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= query_date).\
        order_by(Measurement.date).all()

    all_temps = []
    for date, tobs in results:
        all_temps.append(tobs)

    return jsonify(all_temps)

# Daterange route for <start_date>/<end_date> range
# Setting default end date as current date
@app.route("/api/daterange/<start_date>/", defaults={"end_date":dt.datetime.now().strftime("%Y-%m-%d")})
@app.route("/api/daterange/<start_date>/<end_date>")
def temp_ranges_start_and_end_date(start_date, end_date):
    """Fetch the min, max and avg temps for the dates from 
       the start_date supplied by the user until entered end date or current date, or a 404 if not."""

    if (not valid_date(start_date) or not valid_date(end_date)):
        return jsonify({"error":"Please enter the start_date and end_date in the yyyy-mm-dd format!"}), 404 

    if (dt.datetime.strptime(start_date, '%Y-%m-%d')) <= (dt.datetime.strptime(end_date, '%Y-%m-%d')):
        temp_result = calc_temps(start_date, end_date)
    else:
        return jsonify({"error":"The <start_date> must be equal or before the <end_date>. Try Again."}), 404

    temp_list = []
    for min_temp, avg_temp, max_temp in temp_result:
        temp_list.append(min_temp)
        temp_list.append(avg_temp)
        temp_list.append(max_temp)

    if all(x for x in temp_list):
        return jsonify(temp_list)

    return jsonify({"error":f"Invalid date input. There is no data for the date range entered."}), 404

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVG, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

def valid_date(datestring):
    try:
        dt.datetime.strptime(datestring, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    
if __name__ == "__main__":
    app.run(debug=True)