
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from datetime import datetime, timedelta

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables

Base.prepare(autoload_with=engine)


# reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station


#flask setup
app = Flask(__name__)

#flask routes

@app.route("/")
def home():

    """List all the available routes."""
    return(
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>" 
        f"/api/v1.0/<start>/<end><br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    """ Return the precipitation data from last year """
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    precipitation_result = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()

    #print(precipitation_result)
    #prcp_dict = {date: prcp for date, prcp in precipitation}
    session.close()
    
    prcp_dict = list(np.ravel(precipitation_result))
    
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():

# Create session (link) from Python to the DB
    session = Session(engine)

    """"Return a JSON list of stations from the dataset."""
    results = session.query(Station.station).all()
    session.close()
    
    stations = list(np.ravel(results))

    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobs(): 
    """Query the dates and temperature observations\
        of the most-active station for the previous year of data."""

    session = Session(engine)
  
    #station with most observation
    active_station = "USC00519281"

    last_year = (dt.datetime(2017,8,23)) - dt.timedelta(days=365)

    # session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
    #             .filter(measurement.station == active_station).all()


    tobs_results = Session.query(
        func.MIN(Measurement.date), func.MAX(Measurement.tobs), 
        func.AVG(Measurement.tobs))\
        .filter(Measurement.station == active_station).all()
        #.filter(Measurement.date >= last_year).all())
    
    session.close()

    all_tobs = list(np.ravel(tobs_results))    

    return jsonify(tobs_results= all_tobs)

@app.route("/api/v1.0/temp/<start>")
def start(start=None, end=None):    

    session = Session(engine)

    """Return a JSON list of the minimum temperature,\
    the average temperature, and the maximum temperature\
    for a specified start or start-end range.."""

    sel = [func.MIN(Measurement.tobs), func.AVG(Measurement.tobs), func.MAX(Measurement.tobs)]

    if not end:
        results = session.query(*sel).filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        session.close()

        #return jsonify(temps=temps)

       
    # Create a dictionary from the start_temp_results data 
    """For a specified start, calculate TMIN, TAVG, and TMAX\
    for all the dates greater than or equal to the start date."""
    
    start_temps = []
    for result in results: 
        start_temps_dict = {}
        start_temps_dict["Date"] = result[0]
        start_temps_dict["Low Temp, TMIN"] = result[1]
        start_temps_dict["Average Temp, TAVG"] = result[2]
        start_temps_dict["High Temp, TMAX"] = result[3]
        start_temps.append(start_temps_dict)

    start_temps = list(np.ravel(start_temps))
    return jsonify(start_temps)


@app.route("/api/v1.0/temp/<start>/<end>")
def start_end(start=None, end=None):

    session = Session(engine)

    """For a specified start date and end date,\ 
    calculate TMIN, TAVG, and TMAX for the dates,\
    from the start date to the end date, inclusive."""

    sel = [func.MIN(Measurement.tobs), func.AVG(Measurement.tobs), func.MAX(Measurement.tobs)]

    if end:
        end_results = session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).group_by(Measurement.date).all()
        session.close()

    # Create a dictionary from the row data 
    temps_dict = []
    for results in end_results:
        temps_dict = {}
        temps_dict["Date"] = results[0]
        temps_dict["Low Temp,TMIN"] = results[1]
        temps_dict["Average Temp, TAVG"] = results[2]
        temps_dict["High Temp, TMAX"] = results[3]
        temps_dict.append(temps_dict)

        temps_dict = list(np.ravel(end_results))
        
        return jsonify(temps_dict)

if __name__ == '__main__':
    app.run(debug=True)
