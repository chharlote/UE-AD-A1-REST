from flask import Flask, request, jsonify, make_response
import json
import sys
from jwt import token_required
import uuid

from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3200
HOST = '0.0.0.0'


try:
    with open('{}/databases/movies.json'.format("."), 'r') as jsf:
        movies = json.load(jsf)["movies"]
        print(movies)
except FileNotFoundError:
    print("Error: movies.json file not found")
    sys.exit(1)

def write(movies):
    with open('{}/databases/movies.json'.format("."), 'w') as f:
        full = {}
        full['movies']=movies
        json.dump(full, f)

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)


# @app.route("/movies", methods=['GET'])
# @token_required()
# def get_movies():
#     res = make_response(jsonify(movies), 200)
#     return res

@app.route("/movies", methods=['GET'])
@token_required()
def get_movies():
    filtered_movies = movies

    # Director filter
    director = request.args.get("director")
    if director:
        filtered_movies = [
            m for m in filtered_movies
            if director.lower() in m["director"].lower()
        ]

    # title filter
    title = request.args.get("title")
    if title:
        filtered_movies = [
            m for m in filtered_movies
            if title.lower() in m["title"].lower()
        ]

    # min_rating filter
    min_rating = request.args.get("min_rating")
    if min_rating:
        try:
            min_val = float(min_rating)
            filtered_movies = [
                m for m in filtered_movies
                if float(m["rating"]) >= min_val
            ]
        except ValueError:
            return make_response(jsonify({"error": "min_rating must be a number"}), 400)

    return make_response(jsonify(filtered_movies), 200)

@app.route("/movies/<movieid>", methods=['GET'])
@token_required()
def get_movie_byid(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            res = make_response(jsonify(movie),200)
            return res
    return make_response(jsonify({"error": "Movie ID not found"}), 404)


@app.route("/movies", methods=['POST'])
@token_required(admin_req=True)
def add_movie():
    req = request.get_json()
    if not req:
        return make_response(jsonify({"error": "Invalid or missing JSON payload"}), 400)

    if not req.get("title"):
        return make_response(jsonify({"error": "Missing title"}), 400)
    if not req.get("director"):
        return make_response(jsonify({"error": "Missing director"}), 400)
    if not req.get("rating"):
        return make_response(jsonify({"error": "Missing rating"}), 400)

    new_movie_id = str(uuid.uuid4())
    for movie in movies:
        if str(movie["id"]) == str(new_movie_id):
            print(movie["id"])
            print(new_movie_id)
            return make_response(jsonify({"error":"movie ID already exists"}),400)

    new_movie = {
        "id": new_movie_id,
        "title": req["title"],
        "director": req["director"],
        "rating": req.get("rating", 0)
    }

    movies.append(new_movie)
    write(movies)

    return make_response(jsonify({"message": "Movie added", "movie": new_movie}), 201)


@app.route("/movies/<movieid>", methods=['PUT'])
@token_required(admin_req=True)
def update_movie_rating(movieid):
    req_data = request.get_json()

    if not req_data:
        return make_response(jsonify({"error": "Invalid or missing JSON payload"}), 400)
    if not req_data.get("rating"):
        return make_response(jsonify({"error": "Missing rating"}), 400)
    if not req_data.get("title"):
        return make_response(jsonify({"error": "Missing title"}), 400)
    if not req_data.get("director"):
        return make_response(jsonify({"error": "Missing director"}), 400)

    for movie in movies:
        if str(movie["id"]) == str(movieid):
            for key, value in req_data.items():
                if key != "id":
                    movie[key] = value

            write(movies)
            return make_response(jsonify(movie),200)
    return make_response(jsonify({"error":"movie ID not found"}),404)


@app.route("/movies/<movieid>", methods=['DELETE'])
@token_required(admin_req=True)
def del_movie(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movies.remove(movie)
            write(movies)
            return make_response(jsonify(movie),200)

    return make_response(jsonify({"error": "Movie ID not found"}), 404)

if __name__ == "__main__":
    #p = sys.argv[1]
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
