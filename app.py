import streamlit as st
import pickle
import requests
import pandas as pd

# Page title
st.title("🎬 Movie Recommender System")

# Load data
movies_list = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Convert to DataFrame if it's not already
if isinstance(movies_list, list):
    movies = pd.DataFrame(movies_list)
else:
    movies = movies_list

# Ensure required columns exist
if 'title' not in movies.columns or 'movie_id' not in movies.columns:
    st.error("❌ 'movies.pkl' must contain 'title' and 'movie_id' columns.")
    st.stop()

# Function to fetch movie poster from TMDB
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=490319ec1962043242cd1cefd562851f&language=en-US"
        response = requests.get(url)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/300x450?text=No+Image"
    except Exception as e:
        print(f"Error fetching poster for movie_id {movie_id}: {e}")
        return "https://via.placeholder.com/300x450?text=Error"

# Recommendation logic
def recommend(movie_title):
    try:
        movie_index = movies[movies['title'] == movie_title].index[0]
        distances = similarity[movie_index]
        movies_list_sorted = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])

        recommended_movie_names = []
        recommended_movie_posters = []
        for i in movies_list_sorted[1:6]:
            movie_id = movies.iloc[i[0]]['movie_id']
            recommended_movie_names.append(movies.iloc[i[0]]['title'])
            recommended_movie_posters.append(fetch_poster(movie_id))

        return recommended_movie_names, recommended_movie_posters
    except Exception as e:
        st.error(f"Something went wrong while recommending: {e}")
        return [], []

# Dropdown to select movie
selected_movie = st.selectbox(
    "Select a movie to get recommendations 👇",
    movies['title'].values,
    index=None,
    placeholder="search your favourite moveis..."
)

st.write("You Selected:", selected_movie)

# Button to get recommendations
if st.button('🎥 Show Recommendations'):
    names, posters = recommend(selected_movie)
    if names:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])
    else:
        st.warning("No recommendations found.")
