import requests

MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
API_KEY = "4f888ee9db0bdf1b732b17070c4ad769"

image_url = "https://image.tmdb.org/t/p/w500"


def get_movies(movie):
    querystring = {
        "api_key": API_KEY,
        "query": movie
    }
    response = requests.get(MOVIE_DB_SEARCH_URL, querystring)
    results = response.json()["results"]
    return results


def find_movie(movie_id):
    movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_id}"
    response = requests.get(movie_api_url, params={"api_key": API_KEY, "language": "en-US"})
    data = response.json()
    return data

