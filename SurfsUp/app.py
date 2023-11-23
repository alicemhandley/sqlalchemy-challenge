from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import os

# Get the absolute path to the directory the script is in
basedir = os.path.abspath(os.path.dirname(__file__))

# Connect to the SQLite database file
engine = create_engine(f"sqlite:///{os.path.join(basedir, 'Resources', 'hawaii.sqlite')}")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
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
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the dates and precipitation for the last year
    one_year_ago = dt.date.today() - dt.timedelta(days=365)
    precipitation_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).all()

    session.close()

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for all stations
    stations = session.query(station.station).all()

    session.close()

    # Convert the Row objects into dictionaries
    stations = [row._asdict() for row in stations]

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the last year of temperature observation data for the most active station
    one_year_ago = dt.date.today() - dt.timedelta(days=365)
    most_active_station = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()[0]
    tobs_data = session.query(measurement.tobs).\
        filter(measurement.station == most_active_station).\
        filter(measurement.date >= one_year_ago).all()

    session.close()

    return jsonify(tobs_data)

@app.route("/api/v1.0/")
def api_home():
    return "Welcome to the API!"

@app.route("/api/v1.0/<start>")
def start(start):
    # Convert the start parameter to a datetime object
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query for the minimum temperature, the average temperature, and the maximum temperature for a given start
    temperature_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()
    
    session.close()
    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Convert the start and end parameters to datetime objects
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query for the minimum temperature, the average temperature, and the maximum temperature for a given start-end range
    temperature_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).\
        filter(measurement.date <= end_date).all()
    
    session.close()
    return jsonify(temperature_data)

if __name__ == '__main__':
    app.run(debug=True)