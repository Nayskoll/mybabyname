import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import ast
import urllib.parse
import streamlit.components.v1 as components

st.set_page_config(page_title="👶 My Baby Name Generator", layout="wide")

# Chargement du CSV
df = pd.read_csv("prenoms_embed_dedup.csv", encoding="utf-8")
df["name"] = df["name"].str.capitalize().str.strip()
df["embedding"] = df["embedding"].apply(ast.literal_eval)
df["gender"] = df["gender"].str.upper().str.strip()
df["total_popularity"] = pd.to_numeric(df["total_popularity"], errors="coerce")

all_names = sorted(df["name"].unique())

# Initialise favorites en session state s’ils n’existent pas
if "favorites" not in st.session_state:
    st.session_state.favorites = []

def suggest_names(input_names, gender, top_n=30):
    df_gender = df[df["gender"] == gender]
    if not input_names:
        return df_gender.sort_values(by="total_popularity", ascending=False).head(top_n)
    
    input_vectors = np.vstack(df[df["name"].isin(input_names)]["embedding"].values)
    avg_vector = np.mean(input_vectors, axis=0).reshape(1, -1)
    all_embeddings = np.vstack(df_gender["embedding"].values)
    similarities = cosine_similarity(avg_vector, all_embeddings)[0]
    
    df_gender = df_gender.copy()
    df_gender["similarity"] = similarities
    suggestions = df_gender[~df_gender["name"].isin(input_names)]
    suggestions = suggestions.sort_values(by=["similarity", "total_popularity"], ascending=[False, False])
    
    return suggestions.head(top_n)

# UI améliorée
st.title("👶 My Baby Name Generator")
st.write("Découvrez des prénoms similaires à ceux que vous aimez, avec des infos utiles sur leur origine, signification et popularité.")

st.markdown("""
    <style>
    .styled-card {
        background: linear-gradient(135deg, #f9f9f9 60%, #e3e6f3 100%);
        padding: 18px 20px 18px 20px;
        border-radius: 18px;
        box-shadow: 0 2px 12px rgba(80,80,120,0.08);
        margin-bottom: 18px;
        min-height: 230px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border: 1.5px solid #ececf2;
        transition: box-shadow 0.2s;
    }
    .styled-card:hover {
        box-shadow: 0 4px 18px rgba(80,80,120,0.16);
        border: 1.5px solid #b3b6d4;
    }
    .styled-card h3 {
        color: #7e3af2;
        margin-bottom: 0.4rem;
        font-size: 1.3rem;
        font-weight: 700;
    }
    .progress-container {
        background-color: #ececf2;
        border-radius: 8px;
        height: 8px;
        width: 100%;
        margin-bottom: 4px;
    }
    .progress-bar {
        background: linear-gradient(90deg, #7e3af2 60%, #a5b4fc 100%);
        height: 100%;
        border-radius: 8px;
    }
    .styled-card p {
        margin-bottom: 0.3rem;
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)





with st.form("name_form"):
    selected_names = st.multiselect(
        "Choisissez un ou plusieurs prénoms de référence :",
        options=all_names
    )
    gender = st.radio("Sexe", ["M", "F"], horizontal=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        submitted = st.form_submit_button("✨ Générer des suggestions")
    with col2:
        add_to_favs = st.form_submit_button("💖 Ajouter à mes favoris")

    if submitted and selected_names:
        st.session_state["last_selected_names"] = selected_names
        st.session_state["last_gender"] = gender
        st.session_state["suggestions"] = suggest_names(selected_names, gender=gender.upper(), top_n=30)

    if add_to_favs and selected_names:
        added = []
        for name in selected_names:
            if name not in st.session_state.favorites:
                st.session_state.favorites.append(name)
                added.append(name)
        if added:
            st.success(f"{', '.join(added)} ajouté(s) aux favoris !")
        else:
            st.info("Tous ces prénoms sont déjà dans vos favoris.")

if "suggestions" in st.session_state:
    suggestions = st.session_state["suggestions"]

    st.subheader("Suggestions de prénoms")
    st.write("Voici 30 prénoms qui pourraient vous plaire :")

    cols_per_row = 3
    rows = [suggestions.iloc[i:i + cols_per_row] for i in range(0, len(suggestions), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (_, suggestion) in zip(cols, row.iterrows()):
            with col:
                with st.form(f"form_{suggestion['name']}"):
                    st.markdown(f"""
                        <div class="styled-card">
                            <h3 style="margin-bottom:0.2rem; color:#7e3af2;">{suggestion['name']}</h3>
                            <p><strong>⭐️ Similarité :</strong> {int(suggestion.get('similarity', 0) * 100)}%</p>
                            <p><strong>🔥 Popularité :</strong> {int(suggestion['total_popularity'])} naissances</p>
                            <div class="progress-container">
                                <div class="progress-bar" style="width: {min(int(suggestion['total_popularity']) / df['total_popularity'].max() * 100, 100)}%;"></div>
                            </div>
                            <p><strong>🌍 Origine :</strong> {suggestion['origin']}</p>
                            <p><strong>💬 Signification :</strong> {suggestion['meaning']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.form_submit_button("❤️ Ajouter aux favoris"):
                        if suggestion["name"] not in st.session_state.favorites:
                            st.session_state.favorites.append(suggestion["name"])
                            st.success(f"{suggestion['name']} ajouté aux favoris !")

elif submitted and not selected_names:
    st.warning("Veuillez sélectionner au moins un prénom dans la liste !")

st.subheader("💖 Mes prénoms favoris")

if st.session_state.favorites:
    favs_df = df[df["name"].isin(st.session_state.favorites)]
    cols_per_row = 3
    rows = [favs_df.iloc[i:i + cols_per_row] for i in range(0, len(favs_df), cols_per_row)]

    st.markdown("""
    <style>
    .delete-x {
        position: absolute;
        top: 8px;
        right: 12px;
        z-index: 10;
        background: transparent;
        border: none;
        color: #999;
        font-size: 1.3em;
        cursor: pointer;
        padding: 0;
    }
    .fav-card-container {
        position: relative;
    }
    </style>
    """, unsafe_allow_html=True)

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (df_index, fav) in zip(cols, row.iterrows()):
            gender_icon = "♂️" if fav["gender"] == "M" else "♀️"
            bg_color = "#e6f0ff" if fav["gender"] == "M" else "#f9d6e3"
            border_color = "#3b82f6" if fav["gender"] == "M" else "#db7093"
            title_color = "#3b82f6" if fav["gender"] == "M" else "#db7093"
            delete_key = f"delete_{fav['name']}_{df_index}"
            with col:
                st.markdown('<div class="fav-card-container">', unsafe_allow_html=True)
                if st.button("✖", key=delete_key, help="Supprimer ce favori"):
                    st.session_state.favorites.remove(fav["name"])
                    st.rerun()
                st.markdown(f"""
                    <div class="styled-card" style="border: 2px solid {border_color}; background: {bg_color}; margin-top:0px;">
                        <h3 style="color:{title_color};">{gender_icon} {fav['name']}</h3>
                        <p><strong>🌍 Origine :</strong> {fav['origin']}</p>
                        <p><strong>💬 Signification :</strong> {fav['meaning']}</p>
                        <p><strong>🔥 Popularité :</strong> {int(fav['total_popularity'])} naissances</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🗑️ Vider tous les favoris"):
        st.session_state.favorites.clear()
        st.rerun()
else:
    st.info("Aucun prénom favori pour le moment.")



import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

# Message et URL à partager
message = "Découvre ma liste de prénoms et leur signification sur mybabyname.app 🎈"
url = "https://mybabyname.app"
full_message = f"{message} {url}"
encoded_message = urllib.parse.quote(full_message)
encoded_url = urllib.parse.quote(url)

# Messenger
app_id = "145634995501895"
messenger_url = (
    f"https://www.facebook.com/dialog/send?"
    f"app_id={app_id}&link={encoded_url}&redirect_uri={encoded_url}&display=popup"
)

# X (ex-Twitter)
x_url = (
    "https://twitter.com/intent/tweet?"
    f"text={urllib.parse.quote(message)}&url={encoded_url}"
)

# WhatsApp
whatsapp_url = f"https://wa.me/?text={encoded_message}"

# Facebook
facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"

# Affichage des logos de partage
components.html(
    f"""
    <style>
    .modern-share {{
        display: flex;
        gap: 22px;
        margin: 28px 0 10px 0;
        justify-content: flex-start;
        flex-wrap: wrap;
    }}
    .modern-share a {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: #fff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        transition: box-shadow 0.18s, transform 0.18s, background 0.18s;
        text-decoration: none;
        border: none;
        outline: none;
    }}
    .modern-share a:hover {{
        box-shadow: 0 4px 16px rgba(0,0,0,0.13);
        transform: scale(1.11);
        background: #f3f3f3;
    }}
    .modern-share img {{
        width: 26px; height: 26px;
        display: block;
    }}
    </style>
    <div class="modern-share">
        <a href="{whatsapp_url}" target="_blank" title="Partager sur WhatsApp">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp"/>
        </a>
        <a href="{messenger_url}" target="_blank" title="Partager sur Messenger">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Facebook_Messenger_logo_2020.svg/1024px-Facebook_Messenger_logo_2020.svg.png" alt="Messenger"/>
        </a>
        <a href="{x_url}" target="_blank" title="Partager sur X">
            <img src="https://upload.wikimedia.org/wikipedia/commons/c/ce/X_logo_2023.svg" alt="X"/>
        </a>
        <a href="{facebook_url}" target="_blank" title="Partager sur Facebook">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook"/>
        </a>
    </div>
    """,
    height=80,
)
