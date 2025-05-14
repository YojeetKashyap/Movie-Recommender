import numpy as np
import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.stem.porter import PorterStemmer
from  sklearn.metrics.pairwise import cosine_similarity

credits_df = pd.read_csv("credits.csv")
movies_df = pd.read_csv("movies.csv")

movies_df = movies_df.merge(credits_df,on = "title")
movies_df.shape

movies_df = movies_df[['movie_id','title','overview','genres','keywords','cast','crew']]
movies_df.dropna(inplace = True)

def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i["name"])
    return L

movies_df['genres'] = movies_df['genres'].apply(convert)
movies_df['keywords'] = movies_df['keywords'].apply(convert)


def convert3(obj):
    L = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            L.append(i["name"])
            counter += 1
        else :
            break
        return L
    

movies_df['cast'] =  movies_df['cast'].apply(convert3)    

def fetch_director(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i["job"] == "Director" :
            L.append(i["name"])
    return L

movies_df['crew'] = movies_df['crew'].apply(fetch_director)

movies_df["overview"] = movies_df['overview'].apply(lambda x:x.split())

def process_list(lst):
    if lst is not None:
        return [i.replace(" ", "") for i in lst]
    else:
        return None

movies_df["genres"] = movies_df["genres"].apply(process_list)
movies_df["keywords"] = movies_df["keywords"].apply(process_list)
movies_df["cast"] = movies_df["cast"].apply(process_list)
movies_df["crew"] = movies_df["crew"].apply(process_list)

movies_df['tags'] =  movies_df['overview'] + movies_df['genres'] + movies_df["keywords"] + movies_df["cast"] + movies_df["crew"]

new_df = movies_df[["movie_id","title","tags"]]
new_df['tags'] = new_df['tags'].apply(lambda x: ' '.join(x) if isinstance(x, (list, tuple)) else '')

cv = CountVectorizer(max_features = 5000 , stop_words = 'english')
vectors = cv.fit_transform(new_df["tags"]).toarray()
ps = PorterStemmer()
def stem(text):
    y = []
    for i in text.split():
        y.append(ps.stem(i))
    return " ".join(y)

new_df['tags'] = new_df['tags'].apply(stem)

similarity = cosine_similarity(vectors)
similarity[0]
similarity[0].shape

sorted(list(enumerate(similarity[0])),reverse=True,key = lambda x:x[1:6])
def recommend(movie):
    movie_index = new_df[new_df['title']==movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:10]

    for i in movies_list:
        print(new_df.iloc[i[0]].title)
        
