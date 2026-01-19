import pickle
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Anirec", page_icon="🎬", layout="wide")

@st.cache_data
def load_data():
    try:
        anime_df = pickle.load(open('model/anime_data.pkl', 'rb'))
        similarity = pickle.load(open('model/similarity_matrix.pkl', 'rb'))
        indices = pickle.load(open('model/indices.pkl', 'rb'))
        return anime_df, similarity, indices
    except FileNotFoundError:
        st.error("File model tidak ditemukan di folder 'model'.")
        return None, None, None

df_clean, cosine_sim, indices = load_data()

# dash
st.title("Anirec")
st.markdown("Temukan anime **Romance** yang ceritanya kurang lebih sama dengan favorit Anda.")
st.write("---")

# fitur search
if df_clean is not None:
    selected_anime = st.selectbox(
        label="Ketik atau pilih judul anime yang Anda suka:",
        options=df_clean['title'].values,
        index=None,
        placeholder="Contoh: Nisekoi, Go-Toubun no Hanayome, dan lain-lain..."
    )

    if selected_anime:
        if st.button("Cari Rekomendasi"):
            
            try:
                idx = indices[selected_anime]
                sim_scores = list(enumerate(cosine_sim[idx]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                sim_scores = sim_scores[1:11]
                
                anime_indices = [i[0] for i in sim_scores]
                
                st.success(f"Menampilkan 10 anime yang mirip dengan **{selected_anime}**:")
                
                results = df_clean.iloc[anime_indices][['title', 'genres', 'score']]
                
                results = results.reset_index(drop=True)
                results.index += 1 
                
# Tampilkan tabel
                st.table(results)
                
            except KeyError:
                st.error("Maaf, data anime tersebut tidak ditemukan dalam indeks sistem.")