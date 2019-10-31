import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Instructions/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation values"""
    # Query all passengers
    dates = session.query(Measurement.date).all()
    precips = session.query(Measurement.prcp).all()
    session.close()

    # Convert list of tuples into normal list
    all_dates = list(np.ravel(dates))
    all_precips = list(np.ravel(precips))

    precip_dict = []

    for i in range(len(all_dates)):
        precip_dict.append({all_dates[i]:all_precips[i]})

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of stations from the dataset.
    
    """Return a list of all stations"""
    # Query all stations
    stations = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session
    session = Session(engine)

    # Query dates and temps
    dates = session.query(Measurement.date).all()
    tobs = session.query(Measurement.tobs).all()
    session.close()

    for i in range(len(dates)):
        dates[i] = np.datetime64(dates[i][0])
   
    # Find max date
    max_date = max(dates)

    #Calculate cutoff date
    cutoff_date = max_date - 365

    valid_dates = []

    for i in range(len(dates)):
        if dates[i] >= cutoff_date:
            valid_dates.append(tobs[i])

    return jsonify(valid_dates)

@app.route("/api/v1.0/<start>")
def temp(start):
    session = Session(engine)

    #Put start in datetime form
    start_date = dt.strptime(start, '%Y%m%d')

    # Get max date in list
    dates = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date = dates[0][0]

    #Query the temps
    temps_list =  session.query(func.max(Measurement.tobs), func.min(Measurement.tobs),\
        func.avg(Measurement.tobs)).filter(Measurement.date >= start).\
            filter(Measurement.date <= max_date).all()

    #Combine max, min, and mean temps into list 
    final_stats = []
    dates_dict = {'Starting Date': start_date, 'End Date': max_date}
    final_stats.append(dates_dict)
    final_stats.append({'Max Temp':temps_list[0][0]})
    final_stats.append({'Min Temp': temps_list[0][1]})
    final_stats.append({'Mean Temp': temps_list[0][2]})

    return jsonify(final_stats)

@app.route("/api/v1.0/<start>/<end>")
def temp_end(start, end):
    session = Session(engine)

    # Put start and end in datetime form
    start_date = dt.strptime(start, '%Y%m%d')
    end_date = dt.strptime(end, '%Y%m%d')

    #Query the temps
    temps_list =  session.query(func.max(Measurement.tobs), func.min(Measurement.tobs),\
        func.avg(Measurement.tobs)).filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()

    #Combine max, min, and mean temps into list 
    final_stats = []
    dates_dict = {'Starting Date': start_date, 'End Date': end_date}
    final_stats.append(dates_dict)
    final_stats.append({'Max Temp':temps_list[0][0]})
    final_stats.append({'Min Temp':temps_list[0][1]})
    final_stats.append({'Mean Temp': temps_list[0][2]})

    return jsonify(final_stats)

if __name__ == '__main__':
    app.run(debug=True)