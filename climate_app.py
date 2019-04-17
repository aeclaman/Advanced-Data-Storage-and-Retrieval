from flask import Flask, jsonify, escape
import datetime as dt
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, text

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


# Flask Setup
app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"<html><body><h1>Welcome to my Climate Application API!</h1><br/>"
        f"<h2>Available Routes:</h2><br/>"
        f"/api/precipitation<br/>"
        f"/api/stations<br/>"
        f"/api/temperature<br/>"
        #f"/api/daterange/" + escape("<start_date>") + "<br/>"
        #f"/api/daterange/" + escape("<start_date>") + "/" + escape("<end_date>") + "<br/>"
        f"</body></html>"
    )

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

    #return jsonify(dict(results))

@app.route("/api/stations")
def all_stations():
    #stations = session.query(Station.station, Station.name)
    #return jsonify(dict(stations))
    stations = session.query(Station.name).all()
    all_stations = list(np.ravel(stations))
    return jsonify(all_stations)


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

    #return jsonify(dict(results))

@app.route("/api/daterange")
def temp_ranges_with_no_start_date():
#    """Fetch the min, max and avg temps for the dates from 
#       the start_date supplied by the user until current date, or a 404 if not."""

#    canonicalized = start_date.replace(" ", "")
    temp_result = calc_temps(dt.datetime.now(), dt.datetime.now())

    #for min, avg, max in temp_result:
    #    temp_list = [min, avg, max]
    #return jsonify(temp_list)
    
    return jsonify(temp_result)

@app.route("/api/daterange/<start_date>")
def temp_ranges_with_start_date(start_date=dt.datetime.now()):
#    """Fetch the min, max and avg temps for the dates from 
#       the start_date supplied by the user until current date, or a 404 if not."""

#    canonicalized = start_date.replace(" ", "")
    temp_result = calc_temps(start_date, dt.datetime.now())

    #for min, avg, max in temp_result:
    #    temp_list = [min, avg, max]
    #return jsonify(temp_list)
    
    return jsonify(temp_result)

#    return jsonify({"error": f"Character with real_name {real_name} not found."}), 404


@app.route("/api/daterange/<start_date>/<end_date>")
def temp_ranges_start_and_end_date(start_date, end_date=dt.datetime.now()):
#    """Fetch the min, max and avg temps for the dates from 
#       the start_date supplied by the user until current date, or a 404 if not."""

#    canonicalized = start_date.replace(" ", "")
    temp_result = calc_temps(start_date, end_date)

    return jsonify(temp_result)

#    return jsonify({"error": f"Character with real_name {real_name} not found."}), 404

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()



if __name__ == "__main__":
    app.run(debug=True)