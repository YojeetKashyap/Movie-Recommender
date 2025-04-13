from flask import Flask, render_template, request
import pickle
import requests
import os
import py7zr
app = Flask(__name__)

seven_zip_path = "similarity.7z"
similarity_file = "similarity.pkl"

if not os.path.exists(similarity_file):
    with py7zr.SevenZipFile(seven_zip_path, mode='r') as archive:
        all_files = archive.getnames()
        if similarity_file in all_files:
            archive.extract(targets=[similarity_file])
        else:
            print(f"{similarity_file} not found in archive.")




# Load data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# TMDb API to fetch poster (you can replace this with your own key or method)
def fetch_poster(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key=ea40ac416cf5cff6dc25ba774cb1d941&query={title}"
    #url = f"https://api.themoviedb.org/3/movie?api_key=ea40ac416cf5cff6dc25ba774cb1d941&language=en-US&query={title}"
    data = requests.get(url).json()
    if data['results']:
        poster_path = data['results'][0].get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return "https://via.placeholder.com/300x450?text=No+Poster"

def recommend(movie):
    movie = movie.lower().strip()
    if movie not in movies['title'].str.lower().values:
        return [], []

    movie_index = movies[movies['title'].str.lower() == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]

    recommended_movies = []
    poster_urls = []
    for i in movie_list:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        poster_urls.append(fetch_poster(title))
    return recommended_movies, poster_urls

@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    posters = []
    movie_name = ""
    if request.method == 'POST':
        movie_name = request.form['movie']
        recommendations, posters = recommend(movie_name)
    return render_template('index.html', recommendations=recommendations, posters=posters, movie_name=movie_name)

if __name__ == '__main__':
    app.run()
