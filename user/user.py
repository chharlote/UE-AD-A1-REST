from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
    users: list = json.load(jsf)["users"]


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"


def save():
    with open('{}/databases/users.json'.format("."), 'w') as f:
        json.dump({"users": users}, f)


@app.route("/users", methods=['GET'])
def get_users():
    res = make_response(jsonify(users), 200)
    return res


@app.route("/users", methods=['POST'])
def post_users():
    data = request.get_json()

    if not data:
        return make_response(jsonify({"error": "Invalid or missing JSON payload"}), 400)
    if not data["id"]:
        return make_response(jsonify({"error": "Missing id"}), 400)
    if not data["name"]:
        return make_response(jsonify({"error": "Missing name"}), 400)
    if not data["last_active"]:
        return make_response(jsonify({"error": "Missing last_active"}), 400)

    new_user = {
        "id": data["id"],
        "name": data["name"],
        "last_active": data["last_active"],
    }

    for user in users:
        if new_user["id"] == user["id"]:
            return make_response(jsonify({"error": "User's id already taken"}), 400)

    users.append()
    save()

    return make_response(jsonify({"message": "User added", "user": new_user}), 201)


@app.route("/users/<user_id>", methods=['GET'])
def get_user_id(user_id):
    for user in users:
        if user_id == user["id"]:
            return make_response(jsonify(user), 200)

    return make_response(jsonify({"error": "User not found"}), 404)


@app.route("/users", methods=['PUT'])
def put_user():
    data = request.get_json()

    if not data:
        return make_response(jsonify({"error": "Invalid or missing JSON payload"}), 400)
    if not data["id"]:
        return make_response(jsonify({"error": "Missing id"}), 400)
    if not data["name"]:
        return make_response(jsonify({"error": "Missing name"}), 400)
    if not data["last_active"]:
        return make_response(jsonify({"error": "Missing last_active"}), 400)

    new_user = {
        "id": data["id"],
        "name": data["name"],
        "last_active": data["last_active"],
    }

    for user in users:
        if new_user["id"] == user["id"]:
            user["name"] = new_user["name"]
            user["last_active"] = new_user["last_active"]
            save()
            return make_response(jsonify({"message": "User updated", "user": new_user}), 201)

    return make_response(jsonify({"error": "User not found"}), 404)


@app.route("/users/<user_id>", methods=['DELETE'])
def delete_user_id(user_id):
    for user in users:
        if user_id == user["id"]:
            users.remove(user)
            return make_response(jsonify({"message": "User deleted"}), 201)

    return make_response(jsonify({"error": "User not found"}), 404)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
