import pickle
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rekomendasi Anime", page_icon="🎬", layout="wide")

@st.cache_data
def load_data():
    try:
        anime_df = pickle.load(open('model/anime_data.pkl', 'rb'))
        similarity = pickle.load(open('model/similarity_matrix.pkl', 'rb'))
        indices = pickle.load(open('model/indices.pkl', 'rb'))
        return anime_df, similarity, indices
    except FileNotFoundError:
        st.error("File model tidak ditemukan di folder 'model'. Pastikan path sudah benar.")
        return None, None, None

df_clean, cosine_sim, indices = load_data()

st.title("Anirec")
st.markdown("Temukan anime genre romance yang ceritanya mirip dengan favorit Anda.")

# fitur

if df_clean is not None:
    selected_anime = st.selectbox(
        "Pilih judul anime yang Anda suka:",
        df_clean['title'].values
    )

    if st.button("Cari Rekomendasi"):
        
        try:
            idx = indices[selected_anime]
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:11] # Ambil top 10
            
            anime_indices = [i[0] for i in sim_scores]
            
            st.subheader(f"Anime yang mirip dengan **{selected_anime}**:")
            
# tampilkan dalam tabel
            results = df_clean.iloc[anime_indices][['title', 'genres', 'score']]
            st.table(results)
            
        except KeyError:
            st.error("Terjadi kesalahan dalam menemukan data anime tersebut.")