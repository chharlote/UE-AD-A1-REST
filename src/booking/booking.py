from flask import Flask, request, jsonify, make_response, g, send_from_directory
import requests
import json
from ..utils.jwt import token_required
from ..utils import sigterm  # sigterm handler
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

SWAGGER_URL = "/docs"
API_URL = "/openapi.yaml"

MOVIE_SERVICE_URL = "http://127.0.0.1:3200"
SCHEDULE_SERVICE_URL = "http://127.0.0.1:3202"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Booking Service API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

with open('./src/booking/databases/bookings.json', "r") as jsf:
    bookings = json.load(jsf)["bookings"]

def save():
    with open('./src/booking/databases/bookings.json', 'w') as f:
        json.dump({"bookings": bookings}, f)


def verify_movie(movie_id: str) -> tuple[bool, int, str]:
    try:
        res = requests.get(f"{MOVIE_SERVICE_URL}/movies/{movie_id}")
        if res.status_code == 200:
            return True, 200, ""
        return False, 404, "Movie not found"
    except requests.exceptions.RequestException as e:
        return False, 503, f"Movie service unavailable: {str(e)}"


def verify_schedule(date: str, movie_id: str) -> tuple[bool, int, str]:
    try:
        res = requests.get(
            f"{SCHEDULE_SERVICE_URL}/timesbydate", params={"date": date})
        if res.status_code != 200:
            return False, 404, "No schedule found for this date"
        schedule = res.json()
        if str(movie_id) not in [str(m) for m in schedule.get("movies", [])]:
            return False, 404, "Movie is not scheduled on this date"
        return True, 200, ""
    except requests.exceptions.RequestException as e:
        return False, 503, f"Schedule service unavailable: {str(e)}"


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/openapi.yaml", methods=["GET"])
def openapi_spec():
    return send_from_directory(".", "booking.yaml", mimetype="application/yaml")



@app.route("/bookings", methods=['GET'])
@token_required()
def get_bookings():
    if g.admin:
        return make_response(jsonify(bookings), 200)
    for user_b in bookings:
        if user_b["userid"] == g.user_id:
            return make_response(jsonify([user_b]), 200)
    return make_response(jsonify([{"userid": g.user_id, "dates": []}]), 200)


@app.route("/bookings", methods=['POST'])
@token_required()
def add_booking():
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Invalid or missing JSON payload"}), 400)
    if not data.get("movie_id"):
        return make_response(jsonify({"error": "Missing movie_id"}), 400)
    if not data.get("date"):
        return make_response(jsonify({"error": "Missing date"}), 400)

    movie_id = str(data["movie_id"])
    date = str(data["date"])

    # Verify the movie exists in the Movie service
    movie_ok, status, err_msg = verify_movie(movie_id)
    if not movie_ok:
        return make_response(jsonify({"error": err_msg}), status)

    # Verify the date and movie exist in the Schedule service
    sched_ok, status, err_msg = verify_schedule(date, movie_id)
    if not sched_ok:
        return make_response(jsonify({"error": err_msg}), status)

    for user_b in bookings:
        if user_b["userid"] == g.user_id:
            for d in user_b["dates"]:
                if d["date"] == date:
                    if movie_id not in d["movies"]:
                        d["movies"].append(movie_id)
                        save()
                        return make_response(jsonify({"message": "Booking added"}), 201)
                    return make_response(jsonify({"message": "Already booked"}), 304)
            user_b["dates"].append({
                "date": date,
                "movies": [movie_id]
            })
            save()
            return make_response(jsonify({"message": "Booking added"}), 201)

    bookings.append({
        "dates": [
            {"date": date, "movies": [movie_id]},
        ],
        "userid": g.user_id,
    })
    save()
    return make_response(jsonify({"message": "Booking added"}), 201)


@app.route("/bookings", methods=['DELETE'])
@token_required()
def delete_own_booking_json():
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Invalid or missing JSON payload"}), 400)
    if not data.get("movie_id"):
        return make_response(jsonify({"error": "Missing movie_id"}), 400)
    if not data.get("date"):
        return make_response(jsonify({"error": "Missing date"}), 400)

    user_id, date, movie_id = g.user_id, str(
        data["date"]), str(data["movie_id"])
    for user_b in bookings:
        if user_b["userid"] == user_id:
            for d in user_b["dates"]:
                if d["date"] == date and movie_id in d["movies"]:
                    d["movies"].remove(movie_id)
                    if not d["movies"]:
                        user_b["dates"].remove(d)
                    save()
                    return make_response(jsonify({"message": "Booking deleted"}), 200)
            return make_response(jsonify({"error": "Booking not found for this date or movie"}), 404)
    return make_response(jsonify({"error": "No bookings found for this user"}), 404)


@app.route("/bookings/<user_id>", methods=['DELETE'])
@token_required(admin_req=True)
def delete_user_bookings(user_id):
    for user_b in bookings:
        if user_b["userid"] == user_id:
            bookings.remove(user_b)
            save()
            return make_response(jsonify({"message": f"All bookings deleted for user {user_id}"}), 200)
    return make_response(jsonify({"error": "No bookings found for this user"}), 404)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
