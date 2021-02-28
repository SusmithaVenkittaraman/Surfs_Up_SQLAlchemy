import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask,jsonify
#Database setup
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement=Base.classes.measurement
Station=Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


@app.route("/")
def welcome():
    """List all available api routes."""
    session = Session(engine)
    return (
        # Create our session (link) from Python to the DB
        f"Welcome to Hawaai climate analysis API! <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )
    session.close()

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Calculate the date one year from the last date in data set.
    last_year_date=dt.date(2017,8,23)-dt.timedelta(days=365)
    #Query
    precipitation=session.query(measurement.date,measurement.prcp).\
            filter(measurement.date>=last_year_date).all()
    #dictionary
    precipitation_dict={date:prcp for date,prcp in precipitation}
    session.close()
    return jsonify(precipitation_dict)
    

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    #query
    stations= session.query(Station.station).all()  
    #dictionary
    station_dict=list(np.ravel(stations))
    session.close()
    return jsonify(station_dict)
    

@app.route("/api/v1.0/tobs")
def temp():
    session = Session(engine)
    prev_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    results=session.query(measurement.tobs).filter(measurement.station=='USC00519281').filter(measurement.date>=prev_year).all()
    temps=list(np.ravel(results))
    session.close()
    return jsonify(temps)
    
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    session = Session(engine)
    sel=[func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)]
    if not end:
        results=session.query(*sel).filter(measurement.date>=start).all()
        temps=list(np.ravel(results))
        return jsonify(temps)
    results=session.query(*sel).filter(measurement.date>=start).filter(measurement.date<=end).all()
    temps=list(np.ravel(results))
    session.close()
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)
