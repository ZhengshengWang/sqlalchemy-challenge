# Import the dependencies.
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
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
def home():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    latest_date = session.query(func.max(Measurement.date)).scalar()
    latest_date = dt.datetime.strptime(latest_date, "%Y-%m-%d")
    year_ago = latest_date - dt.timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= year_ago).all()
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all weather stations."""

    stations_data = session.query(Station.station).all()

    stations_list = list(np.ravel(stations_data))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations (tobs) for the last 12 months."""
    latest_date = session.query(func.max(Measurement.date)).scalar()
    latest_date = dt.datetime.strptime(latest_date, "%Y-%m-%d")
    year_ago = latest_date - dt.timedelta(days=365)

    most_active_station = session.query(Measurement.station, func.count(Measurement.station))\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()[0]
    
    tobs_data = session.query(Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= year_ago).all()

    tobs_list = list(np.ravel(tobs_data))
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return the min, avg, and max temperature for all dates after the start date."""
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")

    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start_date).all()
    summary = {
        "Start Date": start,
        "Min Temp": results[0][0],
        "Avg Temp": results[0][1],
        "Max Temp": results[0][2],
    }
    return jsonify(summary)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return the min, avg, and max temperature for dates between the start and end date."""
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start_date)\
        .filter(Measurement.date <= end_date).all()

    summary = {
        "Start Date": start,
        "End Date": end,
        "Min Temp": results[0][0],
        "Avg Temp": results[0][1],
        "Max Temp": results[0][2],
    }
    return jsonify(summary)

session.close()

if __name__ == "__main__":
    app.run(debug=True)