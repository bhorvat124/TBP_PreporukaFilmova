import pymongo
import pandas as pd
import recommendations


client = pymongo.MongoClient("mongodb+srv://BojanHorvat:ee2pxp2u@cluster0.cfzmv.mongodb.net")
db = client.get_database("TBP")
_, dataset, csr_data, knn = recommendations.prepare_for_knn()


def create_movies_collection():
    collist = db.list_collection_names()
    if "movies" not in collist:
        db.create_collection("movies")


def populate_movies_collection():
    ratings = pd.read_csv('ratings.csv', sep=',', usecols=range(3), encoding="ISO-8859-1")
    movies = pd.read_csv('movies.csv', sep=',', usecols=range(3), encoding="ISO-8859-1")
    movies_merged = pd.merge(movies, ratings)
    unique_movies = movies_merged.drop_duplicates('movieId')
    all_movies = []
    for idx, row in unique_movies.iterrows():
        movie = {}
        movie_id = row['movieId']
        movie['_id'] = movie_id
        movie['title'] = row['title']
        genres = row['genres'].split('|')
        movie['genres'] = []
        movie['ratings'] = {}
        movie['ratings']['userId'] = []
        movie['ratings']['rating'] = []

        for genre in genres:
            movie['genres'].append(genre)
        current_movie = movies_merged.loc[movies_merged['movieId'] == movie_id]
        for c_idx, c_row in current_movie.iterrows():
            movie['ratings']['userId'].append(c_row['userId'])
            movie['ratings']['rating'].append(c_row['rating'])

        all_movies.append(movie)
    db.movies.insert_many(all_movies)


def get_all_movies():
    movies = db.movies.find()
    all_movies = list(movies)
    return all_movies


def get_recommended_movies(preferred_movies):
    recommended_movies = []
    for movie_id in preferred_movies:
        movie_title = get_movie_title(movie_id)
        all_movies = get_all_movies()
        recommendation_results = recommendations.get_movie_recommendation(movie_title, all_movies, dataset, csr_data, knn)
        for movie_recommendation in recommendation_results:
            if not any(movie['title'] == movie_recommendation['title'] for movie in recommended_movies):
                recommended_movies.append(movie_recommendation)

    recommended_movies = sorted(recommended_movies, key=lambda d: d['distance'])
    return recommended_movies[:10]
        

def get_movie_title(movie_id):
    movie = db.movies.find_one({"_id": int(movie_id)})
    return movie["title"]


def set_preferred_movie(movie_id, username):
    db.users.update_one({"username": username}, {"$addToSet": {"preferred_movies": int(movie_id)}})


def remove_preferred_movie(movie_id, username):
    db.users.update_one({"username": username}, {"$pull": {"preferred_movies": int(movie_id)}})


def insert_new_user(username, password):
    user = {"username": username, "password": password}
    db.users.insert_one(user)

def get_preferred_movies(username):
    user = db.users.find_one({"username": username})
    preferred_movies = []
    if "preferred_movies" in user:
        preferred_movies = user["preferred_movies"]
    return preferred_movies

#create_movies_collection()
#populate_movies_collection()

