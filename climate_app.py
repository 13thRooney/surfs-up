
# Dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

#Create a function that gets minimum, average, and maximum temperatures for a range of dates
# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):

    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# Flask Routes
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of date as key and prcp as the value."""
    print("Received precipitation request.")

    # Calculate the date 1 year ago from the last data point in the database
    start_date = dt.datetime(2017, 8, 23)
    year_ago = start_date - dt.timedelta(days=365)

    # Perform a query to retrieve the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > year_ago).all()

    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    results_dict = {}
    for result in results:
        results_dict[result[0]] = result[1]

    # Return the JSON representation of your dictionary.
    return jsonify(results_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    print("Received stations request.")

    #query stations list
    stations_data = session.query(Station).all()

    #create a list of dictionaries
    stations_list = []
    for station in stations_data:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""

    print("Received tobs request.")
    
    # Calculate the date 1 year ago from the last data point in the database
    start_date = dt.datetime(2017, 8, 23)
    year_ago = start_date - dt.timedelta(days=365)

    # Query for the dates and temperature observations from a year from the last data point.
    results = (session.query(Measurement.date, Measurement.station, Measurement.tobs).\
            filter(Measurement.date > year_ago).all())

    # Create list of dictionaries
    tobs_list = []
    for result in results:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        tobs_list.append(tobs_dict)

    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return JSON when given start only, calculate TMIN, TAVG, and TMAX
     for all dates greater than and equal to the start date."""

    print("Received start request.")

    #Find the last date in the database
    last_date_q = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    db_end_date = last_date_q[0][0]

    #Get Temperatures
    temps = calc_temps(start, db_end_date)

    #Create list of Temperature Observations
    obsv_list = []
    date_dict = {'start_date': start, 'end_date': db_end_date}
    obsv_list.append(date_dict)
    obsv_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    obsv_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    obsv_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(obsv_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return JSON when given the start and the end date, calculate the TMIN, TAVG, and TMAX
     for dates between the start and end date inclusive."""

    print("Received start and end request.")

    #Get Temperatures
    temps = calc_temps(start, end)

    #Create list of Temperature Observations
    obsv_list = []
    date_dict = {'start_date': start, 'end_date': end}
    obsv_list.append(date_dict)
    obsv_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    obsv_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    obsv_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(obsv_list)

#Let 'er rip!
if __name__ == '__main__':
    app.run(debug=True)

