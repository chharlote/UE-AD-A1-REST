from flask import Flask, request, jsonify, make_response
import json
import sys
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

@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(movies), 200)
    return res

@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_byid(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            res = make_response(jsonify(movie),200)
            return res
    return make_response(jsonify({"error": "Movie ID not found"}), 404)

@app.route("/moviesbytitle", methods=['GET'])
def get_movie_bytitle():
    json = ""
    if request.args:
        req = request.args
        for movie in movies:
            if str(movie["title"]) == str(req["title"]):
                json = movie

    if not json:
        return make_response(jsonify({"error": "Movie title not found"}), 404)
    else:
        res = make_response(jsonify(json),200)
    return res


@app.route("/movies/<movieid>", methods=['POST'])
def add_movie(movieid):
    req = request.get_json()
    if not req:
        return make_response(jsonify({"error": "Invalid or missing JSON payload"}), 400)

    for movie in movies:
        if str(movie["id"]) == str(movieid):
            print(movie["id"])
            print(movieid)
            return make_response(jsonify({"error":"movie ID already exists"}),400)

    movies.append(req)
    write(movies)
    return make_response(jsonify({"message": "Movie added", "movie": req}), 201)


@app.route("/movies/<movieid>", methods=['PUT'])
def update_movie_rating(movieid):
    req_data = request.get_json()

    if not req_data:
        return make_response(jsonify({"error": "Aucune donnée JSON fournie"}), 400)

    for movie in movies:
        if str(movie["id"]) == str(movieid):
            for key, value in req_data.items():
                if key != "id":
                    movie[key] = value

            write(movies)
            return make_response(jsonify(movie),200)
    return make_response(jsonify({"error":"movie ID not found"}),404)


@app.route("/movies/<movieid>", methods=['DELETE'])
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
