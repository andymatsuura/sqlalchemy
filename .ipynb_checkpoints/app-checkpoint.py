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

def temperature_date_range(start=None, end=None):
    # Select statement
    select = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%Y-%m-%d")
        results = session.query(*select).\
            filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d")

    results = session.query(*select).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)

# def stats(start=None, end=None):
  

   