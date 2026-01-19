import pickle
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Anirec", layout="wide")

@st.cache_data
def load_data():
    try:
        anime_df = pickle.load(open('model/anime_data.pkl', 'rb'))
        similarity = pickle.load(open('model/similarity_matrix.pkl', 'rb'))
        indices = pickle.load(open('model/indices.pkl', 'rb'))
        return anime_df, similarity, indices
    except FileNotFoundError:
        st.error("File model tidak ditemukan.")
        return None, None, None

df_clean, cosine_sim, indices = load_data()

st.title("Anirec")
st.write("Temukan rekomendasi anime yang mirip dengan yang Anda cari.")
st.write("---")

if df_clean is not None:
    selected_anime = st.selectbox(
        label="Ketik atau pilih judul anime:",
        options=df_clean['title'].values,
        index=None,
        placeholder="Cari judul anime..."
    )

    if selected_anime:
        if st.button("Cari Rekomendasi"):
            try:
                idx = indices[selected_anime]
                sim_scores = list(enumerate(cosine_sim[idx]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                
                candidates = sim_scores[1:31]
                
                final_indices = []
                query_lower = selected_anime.lower()
                
                for i in candidates:
                    if len(final_indices) >= 10:
                        break
                        
                    anime_idx = i[0]
                    anime_title = df_clean.iloc[anime_idx]['title']
                    title_lower = anime_title.lower()
                    
                    if query_lower in title_lower or title_lower in query_lower:
                        continue
                        
                    final_indices.append(anime_idx)
                
                if final_indices:
                    st.subheader(f"Hasil rekomendasi untuk {selected_anime}:")
                    
                    results = df_clean.iloc[final_indices][['title', 'genres', 'score']]
                    results = results.reset_index(drop=True)
                    results.index += 1 
                    
                    st.table(results)
                else:
                    st.warning("Tidak ditemukan rekomendasi yang unik.")
                
            except KeyError:
                st.error("Data anime tidak ditemukan dalam sistem.")