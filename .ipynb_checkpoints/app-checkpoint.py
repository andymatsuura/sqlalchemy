# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return (
        f"Welcome to Honolulu Weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
)
#looked up via chatgpt how to add to the list in this way 
@app.route("/api/v1.0/precipitation")
def precipitation():
    annual_precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()
    precip_dict = {}
    for date, prcp in annual_precip:
        precip_dict[str(date)] = prcp
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    list_stations = session.query(Station.station, Station.name).all()
    station_dict = {}
    for stations, name in list_stations:
        station_dict[str(stations)] = name
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    temps_observed = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').all()
    temps_dict = {}
    for date, tobs in temps_observed:
        temps_dict[str(date)] = tobs
    return jsonify(temps_dict)

#link for how to set up default in readme
@app.route("/api/v1.0/<start>", defaults={'end':None})
@app.route("/api/v1.0/<start>/<end>")
def temperature_date_range(start, end):
    if end is not None:
        temp_range = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >=start).filter(Measurement.date <= end).all()
    else:
        temp_range = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    #convert the query to jsonify,dict. set no_data to false in case query date's out of range
    temperature_dict = {}
    no_data = False
    for t_min, t_max, t_avg in temp_range:
        if t_min is None or t_max is None or t_avg is None:
            no_data = True
        temperature_dict["Min Temp"] = t_min
        temperature_dict["Max Temp"] = t_max
        temperature_dict["Avg Temp"] = t_avg
    if no_data == True:
        return "No data found for this date range"
    else:
        return jsonify(temperature_dict)

if __name__ == '__main__':
    app.run(debug=True)