from flask import Flask, render_template, request, jsonify, make_response, g
import json
from werkzeug.exceptions import NotFound
from jwt import token_required, create_jwt

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


@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get("id"):
        return make_response(jsonify({"error": "Missing id"}), 400)

    id_ = data["id"]
    user = list(filter(lambda x: x["id"] == id_, users))
    if len(user) == 0:
        return make_response(jsonify({"error": "Bad password"}), 401)
    user = user[0]
    admin = user["admin"]

    # Was too lazy to add passwords
    token = create_jwt(id_, admin)
    return make_response(jsonify({"message": "Login successful", "token": token}), 200)


@app.route("/users", methods=['GET'])
@token_required(admin_req=True)
def get_users():
    return make_response(jsonify(users), 200)


@app.route("/users", methods=['POST'])
@token_required(admin_req=True)
def post_users():
    data = request.get_json()

    if not data:
        return make_response(jsonify({"error": "Invalid or missing JSON payload"}), 400)
    if not data.get("id"):
        return make_response(jsonify({"error": "Missing id"}), 400)
    if not data.get("name"):
        return make_response(jsonify({"error": "Missing name"}), 400)
    if not data.get("last_active"):
        return make_response(jsonify({"error": "Missing last_active"}), 400)
    if "admin" not in data:
        return make_response(jsonify({"error": "Missing admin"}), 400)

    new_user = {
        "id": data["id"],
        "name": data["name"],
        "last_active": data["last_active"],
        "admin": data["admin"],
    }

    for user in users:
        if new_user["id"] == user["id"]:
            return make_response(jsonify({"error": "User's id already taken"}), 400)

    users.append(new_user)  # Fixed: added 'new_user' inside append()
    save()

    return make_response(jsonify({"message": "User added", "user": new_user}), 201)


@app.route("/users", methods=['PUT'])
@token_required()
def put_user():
    data = request.get_json()

    if not g.admin and g.user_id != user_id:
        return make_response(jsonify({"error": "You don't have the rights"}), 401)

    if not data:
        return make_response(jsonify({"error": "Invalid or missing JSON payload"}), 400)
    if not data.get("id"):
        return make_response(jsonify({"error": "Missing id"}), 400)
    if not data.get("name"):
        return make_response(jsonify({"error": "Missing name"}), 400)
    if not data.get("last_active"):
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
@token_required()
def delete_user_id(user_id):
    if not g.admin and g.user_id != user_id:
        return make_response(jsonify({"error": "You don't have the rights"}), 401)
    for user in users:
        if user_id == user["id"]:
            users.remove(user)
            save()
            return make_response(jsonify({"message": "User deleted"}), 201)

    return make_response(jsonify({"error": "User not found"}), 404)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
