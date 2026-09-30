from flask import Flask, render_template, request, jsonify, make_response
import json
import sys
import requests
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

try:

    with open('{}/databases/times.json'.format("."), "r") as jsf:
        times = json.load(jsf)["schedule"]
except FileNotFoundError:
    print("Error: times.py file not found.")
    sys.exit(1)

def write(times):
    with open('{}/databases/times.json'.format("."), 'w') as f:
        json.dump({"schedule": times}, f)
@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(times), 200)
    return res

@app.route("/timesbydate", methods=['GET'])
def get_time_bydate():
    json = ""
    if request.args:
        req = request.args
        for time in times:
            if str(time["date"]) == str(req["date"]):
                json = time

    if not json:
        return make_response(jsonify({"error": "No movies for this date"}), 404)
    else:
        res = make_response(jsonify(json),200)
    return res

@app.route("/times/", methods=['POST'])
def add_schedule():
    req = request.get_json()
    if not req:
        return make_response(jsonify({"error": "Invalid or missing JSON payload"}), 400)
    if not req["date"]:
        return make_response(jsonify({"error": "Missing date"}), 400)

    new_date = req['date']

    for time in times:
        if time["date"] == new_date:
            return make_response(jsonify({"error": "This date already exists"}), 409)

    #TODO : Validate the date format (YYYY-MM-DD) using regex or datetime module
    # TODO : vérifier s'il y a des films dans le post
    new_schedule = {
        "date": new_date,
        "movies": []
    }
    times.append(new_schedule)
    write(times)
    return make_response(jsonify({"message": "Schedule added", "schedule": new_schedule}), 201)

@app.route('/times/<date>/movies', methods=['POST'])
def add_movie_to_schedule(date):
    data = request.get_json()
    if not data or 'movies' not in data:
        return make_response(jsonify({"error": "No movies provided"}), 400)

    movies = data['movies']

    target_schedule = None
    for t in times:
        if t["date"] == date:
            target_schedule = t
            break
    if not target_schedule:
        return make_response(jsonify({"error": "Date not found"}), 404)

    try:
        MOVIE_URL = "http://localhost:3200"
        for movie_id in movies:
            movie_response = requests.get(f"{MOVIE_URL}/movies/{movie_id}")

        if movie_response.status_code != 200:
            return make_response(
                jsonify({
                    "error": "Movie not found in movie service",
                    "movie_id": movie_id
                }),
                404
            )

    except requests.exceptions.RequestException as e:
        return make_response(jsonify({"error": "Error connecting to movie service", "details": str(e)}), 500)

    movies_to_add = []
    for movie_id in movies:
        if movie_id not in target_schedule["movies"]:
            if movie_id not in movies_to_add:
                movies_to_add.append(movie_id)


    if not movies_to_add:
        return make_response(
            jsonify({
                "message": "all movies already exist in the schedule",
                "schedule": target_schedule
            }),
            409
        )

    target_schedule["movies"].extend(movies_to_add)
    write(times)

    return make_response(
        jsonify({
            "message": "Films ajoutés avec succès",
            "schedule": target_schedule
        }),
        200
    )

@app.route('/times/<date>/<movie_id>', methods=['DELETE'])
def delete_movie_from_schedule(date, movie_id):
    target_schedule = None

    for t in times:
        if t["date"] == date:
            target_schedule = t
            break

    if not target_schedule:
        return make_response(
            jsonify({"error": "Date not found"}),
            404
        )

    if movie_id not in target_schedule["movies"]:
        return make_response(
            jsonify({
                "message": "The movie is not scheduled for this date",
                "movie_id": movie_id
            }),
            404
        )
    target_schedule["movies"].remove(movie_id)
    write(times)

    return make_response(
        jsonify({
            "message": "Movie deleted successfully",
            "movie_id": movie_id,
            "schedule": target_schedule
        }),
        200
    )
@app.route('/times/<date>', methods=['DELETE'])
def delete_schedule(date):
    for t in times:
        if t["date"] == date:
            times.remove(t)
            write(times)
            return make_response(
                jsonify({
                    "message": "Schedule deleted successfully",
                    "date": date,
                }),
                200
            )
    return make_response(jsonify({"error": "Schedule not found"}), 404)



if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
