import pickle
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Anirec", layout="wide")

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding-top: 20px;
        padding-bottom: 20px;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        color: #FF4B4B;
        margin-bottom: 0;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #555;
        margin-top: -10px;
    }
    .anime-card {
        padding: 10px;
        background-color: #f9f9f9;
        border-radius: 15px;
        margin-bottom: 5px;
    }
    .poster-img {
        width: 100%;
        height: 300px;
        object-fit: cover;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .preview-img {
        width: 100%;
        max-width: 250px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .anime-title {
        height: 45px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2; 
        -webkit-box-orient: vertical;
        font-weight: bold;
        font-size: 14px;
        line-height: 1.2;
        margin-bottom: 4px;
        color: #333;
    }
    .anime-score {
        color: #ff4b4b;
        font-weight: bold;
        font-size: 13px;
    }
    .anime-genre {
        font-size: 12px;
        color: #888;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
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

@st.dialog("Detail Anime")
def show_detail(row):
    col_img, col_info = st.columns([1, 2])
    with col_img:
        st.image(row['image_url'], use_container_width=True)
    with col_info:
        st.subheader(row['title'])
        st.markdown(f"**Score:** ⭐ {row['score']}")
        st.markdown(f"**Type:** {row['type']}")
        st.markdown(f"**Episodes:** {row['episodes']}")
        st.markdown(f"**Genre:** {row['genres']}")
    
    st.write("---")
    st.write("### Sinopsis")
    st.write(row['synopsis'])

st.markdown("""
<div class="main-header">
    <div class="main-title">ANIREC</div>
    <div class="sub-title">Anime Romance Recommendation</div>
</div>
""", unsafe_allow_html=True)

st.write("---")

if df_clean is not None:
    col_search, col_space = st.columns([2, 1])
    
    with col_search:
        selected_anime = st.selectbox(
            label="Mulai pencarian Anda:",
            options=df_clean['title'].values,
            index=None,
            placeholder="Ketik judul anime..."
        )

    if selected_anime:
        selected_row = df_clean[df_clean['title'] == selected_anime].iloc[0]
        
        st.write("")
        with st.container():
            c1, c2 = st.columns([1, 4])
            with c1:
                st.markdown(f'<img src="{selected_row["image_url"]}" class="preview-img">', unsafe_allow_html=True)
            with c2:
                st.subheader(selected_row['title'])
                st.markdown(f"**Score:** {selected_row['score']}")
                st.markdown(f"**Genre:** {selected_row['genres']}")
                try:
                    synopsis_preview = selected_row['synopsis'][:400] + "..." if len(selected_row['synopsis']) > 400 else selected_row['synopsis']
                    st.caption(synopsis_preview)
                except:
                    pass

        st.write("")
        
        if st.button("Cari Rekomendasi Serupa"):
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
                    st.divider()
                    st.subheader(f"Rekomendasi Terbaik:")
                    st.write("")
                    
                    cols1 = st.columns(5)
                    for i in range(5):
                        if i < len(final_indices):
                            idx = final_indices[i]
                            data = df_clean.iloc[idx]
                            with cols1[i]:
                                st.markdown(f"""
                                <div class="anime-card">
                                    <img src="{data['image_url']}" class="poster-img">
                                    <div class="anime-title">{data['title']}</div>
                                    <div class="anime-score">Score: {data['score']}</div>
                                    <div class="anime-genre">{data['genres'].split(',')[0]}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                if st.button("Lihat Detail", key=f"btn_1_{i}"):
                                    show_detail(data)

                    st.write("")
                    
                    cols2 = st.columns(5)
                    for i in range(5):
                        if i + 5 < len(final_indices):
                            idx = final_indices[i + 5]
                            data = df_clean.iloc[idx]
                            with cols2[i]:
                                st.markdown(f"""
                                <div class="anime-card">
                                    <img src="{data['image_url']}" class="poster-img">
                                    <div class="anime-title">{data['title']}</div>
                                    <div class="anime-score">Score: {data['score']}</div>
                                    <div class="anime-genre">{data['genres'].split(',')[0]}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                if st.button("Lihat Detail", key=f"btn_2_{i}"):
                                    show_detail(data)

                else:
                    st.warning("Rekomendasi tidak ditemukan.")
                
            except KeyError:
                st.error("Data anime tidak ditemukan.")