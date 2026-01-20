import pickle
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Anirec", layout="wide")

st.markdown("""
<style>
    .anime-container {
        margin-bottom: 20px;
    }
    .anime-title {
        height: 50px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2; 
        -webkit-box-orient: vertical;
        font-weight: bold;
        font-size: 14px;
        margin-top: 5px;
    }
    .anime-score {
        color: #ff4b4b;
        font-weight: bold;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

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
st.write("Temukan anime rekomendasi berdasarkan kemiripan cerita.")
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
                
                candidates = sim_scores[1:50]
                final_indices = []
                
                query_main = selected_anime.split(':')[0].lower().strip()
                
                for i in candidates:
                    if len(final_indices) >= 10:
                        break
                        
                    anime_idx = i[0]
                    row_data = df_clean.iloc[anime_idx]
                    anime_title = row_data['title']
                    anime_score = row_data['score']
                    
                    if pd.isna(anime_score) or anime_score == 0:
                        continue

                    title_lower = anime_title.lower()
                    if query_main in title_lower:
                        continue
                        
                    final_indices.append(anime_idx)
                
                if final_indices:
                    st.subheader(f"Hasil rekomendasi untuk {selected_anime}:")
                    st.write("")
                    
                    cols1 = st.columns(5)
                    for i in range(5):
                        if i < len(final_indices):
                            idx = final_indices[i]
                            data = df_clean.iloc[idx]
                            with cols1[i]:
                                st.image(data['image_url'], use_container_width=True)
                                st.markdown(f"<div class='anime-title'>{data['title']}</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='anime-score'>Score: {data['score']}</div>", unsafe_allow_html=True)
                                st.caption(data['genres'].split(',')[0])

                    st.write("")
                    
                    cols2 = st.columns(5)
                    for i in range(5):
                        if i + 5 < len(final_indices):
                            idx = final_indices[i + 5]
                            data = df_clean.iloc[idx]
                            with cols2[i]:
                                st.image(data['image_url'], use_container_width=True)
                                st.markdown(f"<div class='anime-title'>{data['title']}</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='anime-score'>Score: {data['score']}</div>", unsafe_allow_html=True)
                                st.caption(data['genres'].split(',')[0])

                else:
                    st.warning("Tidak ditemukan rekomendasi yang unik.")
                
            except KeyError:
                st.error("Data anime tidak ditemukan.")