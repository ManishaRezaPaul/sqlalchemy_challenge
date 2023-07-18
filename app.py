# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy import create_engine, inspect, func


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurements = Base.classes.measurement
stations = Base.classes.station

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
    prcp_data = session.query(measurements.date, measurements.prcp).all()
    
    prcp_dict = {}
    for date, prcp in prcp_data:
        prcp_dict[date] = prcp
    return jsonify(prcp_dict)



@app.route("/api/v1.0/stations")
def get_stations():
    station_list = session.query(stations.station, stations.name).all()
    station_dict = {}
    for station, name in station_list:
        station_dict[station] = name
    return jsonify(station_dict)



@app.route("/api/v1.0/tobs")
def tobs():
    last_date = "2016-08-23"
    tobs_data = session.query(measurements.date, measurements.tobs).\
        filter(measurements.station == 'USC00519281').\
        filter(measurements.date >= last_date).all()
    
    tobs_dict = {}
    for date, tobs in tobs_data:
        tobs_dict[date] = tobs
    return jsonify(tobs_dict)


# ... (previous code)

@app.route("/api/v1.0/<start>")
def temp_change_start(start):
    temp_data = session.query(measurements.date, func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).\
        filter(measurements.date >= start).\
        group_by(measurements.date).all()

    temp_list = []
    for date, tmin, tavg, tmax in temp_data:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["TMIN"] = tmin
        temp_dict["TAVG"] = tavg
        temp_dict["TMAX"] = tmax
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_change_end(start, end):
    temp_data = session.query(func.min(measurements.date, measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs)).\
        filter(measurements.date >= start).\
        filter(measurements.date <= end).\
        group_by(measurements.date).all()

    temp_list = []
    for date, tmin, tavg, tmax in temp_data:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["TMIN"] = tmin
        temp_dict["TAVG"] = tavg
        temp_dict["TMAX"] = tmax
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)


session.close()

if __name__ == '__main__':
    app.run(debug=True)