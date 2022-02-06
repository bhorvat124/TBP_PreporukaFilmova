import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors


def prepare_for_knn():
    ratings = pd.read_csv('ratings.csv', sep=',', usecols=range(3), encoding="ISO-8859-1")
    movies = pd.read_csv('movies.csv', sep=',', usecols=range(3), encoding="ISO-8859-1")
    movies_merged = pd.merge(movies, ratings)
    full_dataset = movies_merged.pivot(index='movieId', columns='userId', values='rating')
    full_dataset.fillna(0, inplace=True)

    no_user_voted = movies_merged.groupby('movieId')['rating'].agg('count')
    no_movies_voted = movies_merged.groupby('userId')['rating'].agg('count')
    full_dataset = full_dataset.loc[no_user_voted[no_user_voted > 10].index, :]
    full_dataset = full_dataset.loc[:, no_movies_voted[no_movies_voted > 30].index]

    csr_data = csr_matrix(full_dataset.values)
    full_dataset.reset_index(inplace=True)
    knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
    knn.fit(csr_data)
    return movies, full_dataset, csr_data, knn


def get_movie_recommendation(movie_name, all_movies, dataset, csr_data, knn):
    num_movies_to_reccomend = 10
    all_movies = pd.DataFrame(all_movies)
    target_movie = all_movies.loc[all_movies["title"] == movie_name]
    recommended_movies = []
    if len(target_movie) > 0:
        movie_idx = target_movie.iloc[0]['_id']
        if len(dataset.loc[dataset["movieId"] == movie_idx]) > 0:
            movie_idx = dataset[dataset['movieId'] == movie_idx].index[0]
            distances, indices = knn.kneighbors(csr_data[movie_idx], n_neighbors=num_movies_to_reccomend + 2)
            rec_movie_indices = sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())),
                                       key=lambda x: x[1], reverse=True)[:0:-1]

            for val in rec_movie_indices[1:]:
                movie_idx = dataset.iloc[val[0]]['movieId']
                idx = all_movies[all_movies['_id'] == movie_idx].index
                recommended_movies.append({'title': all_movies.iloc[idx]['title'].values[0],
                                           'genres': all_movies.iloc[idx]['genres'].values[0], 'distance': val[1],
                                          'ratings': all_movies.iloc[idx]['ratings'].values[0]})
    return recommended_movies
