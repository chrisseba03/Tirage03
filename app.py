import json
import os
import random
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# Configuration de la page
st.set_page_config(page_title="Le Grand Tirage au Sort", page_icon="🎉", layout="centered")

DATA_FILE = "tirage_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "participants_acceptes": [],
            "participants_refuses": [],
            "gagnant": None,
            "etat_tirage": "En attente"
        }
        save_data(default_data)
        return default_data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "participants_acceptes": [],
            "participants_refuses": [],
            "gagnant": None,
            "etat_tirage": "En attente"
        }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Chargement des données actuelles
data = load_data()

st.title("🎉 Le Grand Tirage au Sort en Direct")
st.write("Bienvenue sur le direct officiel ! Suivez le tirage au sort de chez vous en toute transparence. 🍀")

# ---------------------------------------------------------
# AFFICHAGE DU RÉSULTAT FINAL (SI LE TIRAGE A EU LIEU)
# ---------------------------------------------------------
if data["gagnant"] or data["etat_tirage"] == "Termine":
    st.balloons()
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #059669, #047857); padding: 45px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3); border: 5px solid #6ee7b7; margin: 25px 0;">
        <h2 style="color: #6ee7b7; margin: 0; font-size: 24px; text-transform: uppercase; letter-spacing: 2px;">🏆 RÉSULTAT OFFICIEL - LE GAGNANT EST 🏆</h2>
        <h1 style="color: white; font-size: 55px; margin: 25px 0; font-weight: 900; text-shadow: 2px 2px 8px rgba(0,0,0,0.4);">{data['gagnant']}</h1>
        <p style="color: #d1fae5; font-size: 18px; margin: 0; font-weight: bold;">Toutes nos félicitations ! Le tirage est officiel et définitif. 🎉🥂</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Réinitialiser pour un nouveau tirage"):
        data["gagnant"] = None
        data["etat_tirage"] = "En attente"
        save_data(data)
        st.rerun()

# ---------------------------------------------------------
# COMPTE À REBOURS VISUEL (LOCAL / EN DIRECT)
# ---------------------------------------------------------
else:
    st.info("💡 **Le saviez-vous ?** Le compte à rebours ci-dessous indique le temps d'attente avant de lancer le tirage officiel !")
    st.markdown("---")
    
    # Bouton manuel immédiat pour vous sur votre PC
    if st.button("🚀 LANCER LE TIRAGE AU SORT MAINTENANT", type="primary", use_container_width=True):
        if data["participants_acceptes"]:
            gagnant_officiel = random.choice(data["participants_acceptes"])
            data["gagnant"] = gagnant_officiel
            data["etat_tirage"] = "Termine"
            save_data(data)
            st.rerun()
        else:
            st.warning("⚠️ Aucun participant trouvé dans le fichier de données.")

    # Animation visuelle du compte à rebours (purement décorative et fluide pour le public)
    live_animation_html = """
    <div style="text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 10px;">
        <div id="countdown-box" style="display: flex; justify-content: center; gap: 10px; margin-bottom: 15px;">
            <div style="background: #1e293b; color: white; padding: 12px; border-radius: 8px; min-width: 65px;">
                <span id="hours" style="font-size: 22px; font-weight: bold; display: block;">0</span>
                <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Heures</span>
            </div>
            <div style="background: #1e293b; color: white; padding: 12px; border-radius: 8px; min-width: 65px;">
                <span id="minutes" style="font-size: 22px; font-weight: bold; display: block;">0</span>
                <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Min</span>
            </div>
            <div style="background: #1e293b; color: white; padding: 12px; border-radius: 8px; min-width: 65px;">
                <span id="seconds" style="font-size: 22px; font-weight: bold; display: block; color: #38bdf8;">0</span>
                <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Sec</span>
            </div>
        </div>
        <div id="status-text" style="font-size: 14px; color: #38bdf8; font-weight: 600;">
            En attente du lancement par l'organisateur...
        </div>
    </div>
    """
    components.html(live_animation_html, height=120)

# ---------------------------------------------------------
# LISTES PUBLIQUES (PARTICIPANTS & REFUS)
# ---------------------------------------------------------
st.markdown("---")
col_g1, col_g2 = st.columns(2)

with col_g1:
    nb_val = len(data["participants_acceptes"])
    st.subheader(f"✅ Participants Validés ({nb_val})")
    if data["participants_acceptes"]:
        for p in sorted(data["participants_acceptes"], key=lambda x: x.lower()):
            st.write(f"- 👤 {p}")
    else:
        st.info("Aucun participant validé pour le moment.")

with col_g2:
    nb_ref = len(data["participants_refuses"])
    st.subheader(f"❌ Inscriptions Refusées ({nb_ref})")
    if data["participants_refuses"]:
        for r in sorted(data["participants_refuses"], key=lambda x: x['nom'].lower()):
            st.write(f"- 🛑 **{r['nom']}** (*{r['raison']}*)")
    else:
        st.info("Aucun refus.")

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 15px; font-size: 13px; color: #64748b; background-color: #1e293b; border-radius: 10px; margin-top: 30px;">
    Application officielle développée par Seb Capturis pour le groupe La Place du Village - ALLIER (03) 🌲🏡
</div>
""", unsafe_allow_html=True)
