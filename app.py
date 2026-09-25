import datetime
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
            "etat_tirage": "En attente",
            "heure_fin_iso": "" # Pour stocker l'heure cible du compte à rebours
        }
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "heure_fin_iso" not in data:
                data["heure_fin_iso"] = ""
            return data
    except:
        return {
            "participants_acceptes": [],
            "participants_refuses": [],
            "gagnant": None,
            "etat_tirage": "En attente",
            "heure_fin_iso": ""
        }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Chargement des données
data = load_data()

# ---------------------------------------------------------
# PANNEAU ADMINISTRATEUR (DANS LA BARRE LATÉRALE)
# ---------------------------------------------------------
st.sidebar.title("🔐 Espace Administrateur")
mot_de_passe = st.sidebar.text_input("Mot de passe admin", type="password")

# Définissez votre mot de passe admin ici (ex: "allier03")
ADMIN_PASSWORD = "allier03"

est_admin = (mot_de_passe == ADMIN_PASSWORD)

if est_admin:
    st.sidebar.success("✅ Connecté en tant qu'administrateur")
    st.sidebar.markdown("---")
    st.sidebar.subheader("⏳ Réglage du Compte à Rebours")
    
    # Sélecteurs de date et d'heure pour le direct
    date_direct = st.sidebar.date_input("Date du tirage", value=datetime.date.today())
    heure_direct = st.sidebar.time_input("Heure du tirage", value=datetime.time(20, 30))
    
    if st.sidebar.button("💾 Enregistrer l'heure du live"):
        # Fusion date et heure en objet datetime
        dt_cible = datetime.datetime.combine(date_direct, heure_direct)
        data["heure_fin_iso"] = dt_cible.isoformat()
        save_data(data)
        st.sidebar.success("Heure du compte à rebours mise à jour avec succès ! 🎉")
        st.rerun()
        
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Réinitialiser le tirage (Effacer gagnant)"):
        data["gagnant"] = None
        data["etat_tirage"] = "En attente"
        save_data(data)
        st.sidebar.warning("Tirage réinitialisé !")
        st.rerun()
else:
    if mot_de_passe:
        st.sidebar.error("❌ Mot de passe incorrect")

# ---------------------------------------------------------
# INTERFACE PRINCIPALE (PARTICIPANTS & PUBLIC)
# ---------------------------------------------------------
st.title("🎉 Le Grand Tirage au Sort en Direct")
st.write("Bienvenue sur la page officielle du tirage pour le groupe **La Place du Village - Allier (03)** 🌲🏡")
st.markdown("---")

# 1. AFFICHAGE DU RÉSULTAT SI LE TIRAGE A EU LIEU
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

# 2. EN ATTENTE : VRAI COMPTE À REBOURS ET LIEN VERS LE LIVE
else:
    st.info("💡 **Comment ça se passe ?** Vérifiez votre présence dans la liste ci-dessous, suivez le compte à rebours, puis rejoignez le direct sur le groupe Facebook pour assister au tirage !")
    
    # Bouton d'accès au groupe / live Facebook
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <a href="https://www.facebook.com/groups/laplaceduvillageallier03" target="_blank" style="background-color: #1877f2; color: white; padding: 12px 25px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            📢 Rejoindre le groupe / Le Direct Facebook
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Récupération de l'heure cible enregistrée par l'admin
    heure_iso = data.get("heure_fin_iso", "")
    
    # Script JavaScript pour un compte à rebours dynamique réel basé sur l'heure de l'admin
    countdown_html = f"""
    <div style="text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 10px;">
        <div style="font-size: 16px; color: #38bdf8; font-weight: 600; margin-bottom: 15px;" id="status-text">
            ⏳ Compte à rebours avant le lancement du direct :
        </div>
        <div id="countdown-box" style="display: flex; justify-content: center; gap: 10px; margin-bottom: 15px;">
            <div style="background: #1e293b; color: white; padding: 12px; border-radius: 8px; min-width: 65px;">
                <span id="days" style="font-size: 22px; font-weight: bold; display: block;">0</span>
                <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Jours</span>
            </div>
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
        const targetDateStr = "{heure_iso}";
        
        function updateCountdown() {{
            if (!targetDateStr) {{
                document.getElementById("status-text").innerText = "⏳ En attente de la programmation de l'heure par l'organisateur...";
                return;
            }}
            
            const targetTime = new Date(targetDateStr).getTime();
            const now = new Date().getTime();
            const timeLeft = targetTime - now;
            
            if (timeLeft < 0) {{
                document.getElementById("status-text").innerText = "🔥 Le direct est imminent ou en cours ! Préparez-vous !";
                document.getElementById("days").innerText = "0";
                document.getElementById("hours").innerText = "0";
                document.getElementById("minutes").innerText = "0";
                document.getElementById("seconds").innerText = "0";
                return;
            }}
            
            const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
            
            document.getElementById("days").innerText = days;
            document.getElementById("hours").innerText = hours;
            document.getElementById("minutes").innerText = minutes;
            document.getElementById("seconds").innerText = seconds;
        }}
        
        setInterval(updateCountdown, 1000);
        updateCountdown();
    </script>
    """
    components.html(countdown_html, height=150)

# 3. LISTE PUBLIQUE DES PARTICIPANTS VALIDÉS
st.markdown("---")
nb_val = len(data["participants_acceptes"])
st.subheader(f"✅ Participants Validés ({nb_val})")

if data["participants_acceptes"]:
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
