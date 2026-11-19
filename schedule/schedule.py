from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
import json
import sys
import requests
from werkzeug.exceptions import NotFound
from utils.jwt import token_required
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'


SWAGGER_URL = "/docs"
API_URL = "/openapi.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Schedule Service API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

try:

    with open('{}/databases/times.json'.format("."), "r") as jsf:
        times = json.load(jsf)["schedule"]
except FileNotFoundError:
    print("Error: times.py file not found.")
    sys.exit(1)

def write(times):
    with open('{}/databases/times.json'.format("."), 'w') as f:
        json.dump({"schedule": times}, f)


def verify_movie(movie_id: str) -> tuple[bool, int, str]:
    try:
        authorization = request.headers.get("Authorization")

        response = requests.get(
            "http://localhost:3200/movies/" + str(movie_id),
            headers={"Authorization": authorization} if authorization else {}
        )

        if response.status_code == 200:
            return True, 200, ""

        if response.status_code == 401:
            return False, 401, "Invalid or missing Authorization token"

        return False, response.status_code, "Movie service returned an error"

    except requests.exceptions.RequestException as e:
        return False, 503, f"Movie service unavailable: {str(e)}"

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

@app.route("/openapi.yaml", methods=["GET"])
def openapi_spec():
    return send_from_directory(".", "schedule.yaml", mimetype="application/yaml")


@app.route("/json", methods=['GET'])
@token_required()
def get_schedule():
    res = make_response(jsonify(times), 200)
    return res

@app.route("/timesbydate", methods=['GET'])
@token_required()
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
@token_required(admin_req=True)
def add_schedule():
    req = request.get_json()
    if not req:
        return make_response(jsonify({"error": "Invalid or missing JSON payload"}), 400)
    if not req["date"]:
        return make_response(jsonify({"error": "Missing date"}), 400)
    if not req["movies"]:
        return make_response(jsonify({"error": "Missing movies"}), 400)
    new_date = req['date']
    new_movies = req['movies']

    missing_movies = []
    for movie_id in new_movies:
        is_valid, status_code, error_message = verify_movie(movie_id)
        if not is_valid:
            missing_movies.append(movie_id)

    if missing_movies:
        return make_response(jsonify({"error": "The following movies are not found", "movies": missing_movies}), 404)

    for schedule in times:
        if schedule["date"] == new_date:
            return make_response(jsonify({"error": "This date already exists"}), 409)


    new_schedule = {
        "date": new_date,
        "movies": new_movies
    }
    times.append(new_schedule)
    write(times)
    return make_response(jsonify({"message": "Schedule added", "schedule": new_schedule}), 201)

@app.route('/times/<date>/movies', methods=['POST'])
@token_required(admin_req=True)
def add_movie_to_schedule(date):
    data = request.get_json()
    if not data or 'movies' not in data:
        return make_response(jsonify({"error": "No movies provided"}), 400)

    new_movies = data['movies']
    target_schedule = None
    for t in times:
        if t["date"] == date:
            target_schedule = t
            break
    if not target_schedule:
        return make_response(jsonify({"error": "Date not found"}), 404)

    missing_movies = []
    for movie_id in new_movies:
        is_valid, status_code, error_message = verify_movie(movie_id)
        if not is_valid:
            missing_movies.append(movie_id)
    if missing_movies:
        return make_response(jsonify({"error": "The following movies are not found", "movies": missing_movies}), 404)


    already_existing_movies = []
    for movie_id in new_movies:
        if movie_id in target_schedule["movies"]:
            already_existing_movies.append(movie_id)
    if already_existing_movies:
        return make_response(
            jsonify({
                "error": "The following movies are already scheduled for this date",
                "movies": already_existing_movies
            }),
            409
        )

    target_schedule["movies"].extend(new_movies)
    write(times)

    return make_response(
        jsonify({
            "message": "Films ajoutés avec succès",
            "schedule": target_schedule
        }),
        200
    )

@app.route('/times/<date>/<movie_id>', methods=['DELETE'])
@token_required(admin_req=True)
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
            "movie_id_deleted": movie_id,
            "new_schedule": target_schedule
        }),
        200
    )
@app.route('/times/<date>', methods=['DELETE'])
@token_required(admin_req=True)
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
