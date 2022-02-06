from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import pymongo
import os
import database

app = Flask(__name__)
app.secret_key = os.urandom(12)
client = pymongo.MongoClient("mongodb+srv://BojanHorvat:ee2pxp2u@cluster0.cfzmv.mongodb.net")
db = client.get_database("TBP")
users_records = db.users


@app.route("/get_recommended_movies", methods=['POST'])
def get_recommended_movies():
	recommended_movies = []
	if request.method == "POST":
		preferred_movies = request.json['data']
		recommended_movies = database.get_recommended_movies(preferred_movies)
	return jsonify(recommended_movies)


@app.route("/remove_preferred_movie", methods=['POST'])
def remove_preferred_movie():
	if request.method == "POST":
		movie_id = request.json['data']
		database.remove_preferred_movie(movie_id, session["username"])
	return '', 200


@app.route("/get_preferred_movies", methods=['POST'])
def get_preferred_movies():
	preferred_movies = []
	if request.method == "POST":
		preferred_movies = database.get_preferred_movies(session["username"])
	return jsonify(preferred_movies)


@app.route("/set_preferred_movie", methods=['POST'])
def set_preferred_movie():
	if request.method == "POST":
		movie_id = request.json['data']
		database.set_preferred_movie(movie_id, session["username"])
	return '', 200


@app.route("/get_all_movies", methods=['GET'])
def get_all_movies():
	all_movies = database.get_all_movies()
	return jsonify(all_movies)


@app.route("/main", methods=["POST", "GET"])
def main():
	if "username" in session:
		return render_template("main.html")
	else:
		return redirect(url_for("login"))


@app.route("/logout", methods=["POST", "GET"])
def logout():
	if "username" in session:
		session.pop("username")
		return render_template("logout.html")
	else:
		return redirect(url_for("main"))


@app.route("/login", methods=["POST", "GET"])
def login():
	if "username" in session:
		return redirect(url_for("main"))

	if request.method == "POST":
		msg = ""
		username = request.form.get("username")
		password = request.form.get("password")
		found_user = users_records.find_one({"username": username})
		if found_user:
			found_password = found_user["password"]
			if found_password == password:
				session["username"] = username
				return redirect(url_for("main"))
			else:
				msg = "You have entered wrong password!"
				return render_template("login.html", error_msg=msg)
		else:
			msg = "Username not found!"
			return render_template("login.html", error_msg=msg)
	return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
	if "username" in session:
		return redirect(url_for("main"))

	if request.method == "POST":
		msg = ""
		username = request.form.get("username")
		password = request.form.get("password")
		repeated_password = request.form.get("repeated_password")

		found_user = users_records.find_one({"username": username})
		if found_user:
			msg = "There is already user registered with that name!"
			return render_template("register.html", error_msg=msg)
		if password != repeated_password:
			msg = "Entered passwords are not matching!"
			return render_template("register.html", error_msg=msg)

		database.insert_new_user(username, password)
		session["username"] = username
		return redirect(url_for("main"))
	return render_template("register.html")


@app.route("/", methods=["POST", "GET"])
def index():
	if "username" in session:
		return redirect(url_for("main"))
	else:
		return redirect(url_for("login"))


if __name__ == "__main__":
	app.run(debug=True)
