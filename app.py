import json
import os
import streamlit as st
import streamlit.components.v1 as components

# Configuration de la page
st.set_page_config(page_title="Le Grand Tirage au Sort en Direct", page_icon="🎉", layout="centered")

DATA_FILE = "tirage_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "participants_acceptes": [],
            "participants_refuses": [],
            "gagnant": None,
            "etat_tirage": "En attente"
        }
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

# Chargement des données
data = load_data()

st.title("🎉 Le Grand Tirage au Sort en Direct")
st.write("Bienvenue sur la page officielle du tirage pour le groupe **La Place du Village - Allier (03)** 🌲🏡")
st.markdown("---")

# ---------------------------------------------------------
# 1. AFFICHAGE DU RÉSULTAT SI LE TIRAGE A EU LIEU
# ---------------------------------------------------------
if data["gagnant"] or data["etat_tirage"] == "Termine":
    st.balloons()
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #059669, #047857); padding: 45px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3); border: 5px solid #6ee7b7; margin: 25px 0;">
        <h2 style="color: #6ee7b7; margin: 0; font-size: 24px; text-transform: uppercase; letter-spacing: 2px;">🏆 RÉSULTAT OFFICIEL - LE GAGNANT EST 🏆</h2>
        <h1 style="color: white; font-size: 55px; margin: 25px 0; font-weight: 900; text-shadow: 2px 2px 8px rgba(0,0,0,0.4);">{data['gagnant']}</h1>
        <p style="color: #d1fae5; font-size: 18px; margin: 0; font-weight: bold;">Toutes nos félicitations au grand gagnant ! 🎉🥂</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.success("🔒 Le tirage a été effectué par l'organisateur en direct.")

# ---------------------------------------------------------
# 2. EN ATTENTE : COMPTE À REBOURS ET LIEN VERS LE LIVE
# ---------------------------------------------------------
else:
    st.info("💡 **Comment ça se passe ?** Vérifiez votre présence dans la liste ci-dessous, suivez le compte à rebours, puis rejoignez le direct sur le groupe Facebook pour assister au tirage !")
    
    # Bouton d'accès au groupe ou au live Facebook
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <a href="https://www.facebook.com/groups/laplaceduvillageallier03" target="_blank" style="background-color: #1877f2; color: white; padding: 12px 25px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            📢 Rejoindre le groupe / Le Direct Facebook
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Animation visuelle du compte à rebours
    live_animation_html = """
    <div style="text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 10px;">
        <div style="font-size: 16px; color: #38bdf8; font-weight: 600; margin-bottom: 15px;">
            ⏳ En attente du lancement du tirage par l'organisateur...
        </div>
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
    </div>

    <script>
        let sec = 0;
        setInterval(() => {
            sec++;
            document.getElementById("seconds").innerText = sec % 60;
        }, 1000);
    </script>
    """
    components.html(live_animation_html, height=150)

# ---------------------------------------------------------
# 3. LISTE PUBLIQUE DES PARTICIPANTS VALIDÉS
# ---------------------------------------------------------
st.markdown("---")
nb_val = len(data["participants_acceptes"])
st.subheader(f"✅ Participants Validés ({nb_val})")

if data["participants_acceptes"]:
    # Affichage en colonnes ou sous forme de liste propre
    for p in sorted(data["participants_acceptes"], key=lambda x: x.lower()):
        st.write(f"- 👤 {p}")
else:
    st.info("Aucun participant validé pour le moment.")

# Bouton d'actualisation manuelle
st.markdown("---")
if st.button("🔄 Actualiser la page"):
    st.rerun()

st.markdown("""
<div style="text-align: center; padding: 15px; font-size: 13px; color: #64748b; background-color: #1e293b; border-radius: 10px; margin-top: 30px;">
    Application officielle développée par Seb Capturis pour le groupe La Place du Village - ALLIER (03) 🌲🏡
</div>
""", unsafe_allow_html=True)
