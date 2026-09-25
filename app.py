import json
import os
import random
import time
from datetime import datetime, timezone, timedelta
import streamlit as st
import streamlit.components.v1 as components

DATA_FILE = "tirage_data.json"
VISITS_FILE = "visits_count.json"

ADMIN_PASSWORD = "admin170767"

# Heure officielle du tirage automatique (modifiable ou fixée ici)
# Format : datetime (par exemple, aujourd'hui à 16:40)
# Vous pouvez aussi stocker cela dans le JSON pour le modifier depuis l'admin si besoin.

def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "participants_acceptes": [],
            "participants_refuses": [],
            "gagnant": None,
            "etat_tirage": "En attente",
            "heure_tirage": "2026-09-25 16:40:00" # Heure cible par défaut modifiable
        }
        save_data(default_data)
        return default_data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "heure_tirage" not in data:
            data["heure_tirage"] = "2026-09-25 16:40:00"
        return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def track_visit():
    visits = 1
    if os.path.exists(VISITS_FILE):
        try:
            with open(VISITS_FILE, "r", encoding="utf-8") as f:
                visits = json.load(f).get("count", 1) + 1
        except:
            pass
    with open(VISITS_FILE, "w", encoding="utf-8") as f:
        json.dump({"count": visits}, f)
    return visits

if "visited" not in st.session_state:
    st.session_state["visited"] = True
    st.session_state["visit_count"] = track_visit()
else:
    if os.path.exists(VISITS_FILE):
        with open(VISITS_FILE, "r") as f:
            st.session_state["visit_count"] = json.load(f).get("count", 1)

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

data = load_data()

# --- VÉRIFICATION AUTOMATIQUE DU TEMPS CIBLE ---
try:
    target_dt = datetime.strptime(data["heure_tirage"], "%Y-%m-%d %H:%M:%S")
    now_dt = datetime.now()
    if data["etat_tirage"] == "En attente" and now_dt >= target_dt and data["participants_acceptes"]:
        # Le temps est écoulé : on déclenche le tirage automatiquement !
        gagnant_auto = random.choice(data["participants_acceptes"])
        data["etat_tirage"] = "Termine"
        data["gagnant"] = gagnant_auto
        save_data(data)
except Exception as e:
    pass

st.title("🎉 Le Grand Tirage au Sort en Direct !")
st.write("Suivez le tirage en temps réel et découvrez si la chance vous sourit ! 🍀")

# ---------------------------------------------------------
# BARRE LATERALE - CONNEXION ADMIN SECURISEE
# ---------------------------------------------------------
st.sidebar.header("⚙️ Espace Sécurisé")

if not st.session_state["is_admin"]:
    st.sidebar.info("👥 Vous êtes connecté en tant que **Spectateur / Participant**.")
    st.sidebar.markdown("---")
    
    with st.sidebar.expander("🔐 Accès Administrateur"):
        pwd_input = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if pwd_input == ADMIN_PASSWORD:
                st.session_state["is_admin"] = True
                st.success("Connecté !")
                st.rerun()
            else:
                st.error("Mot de passe incorrect.")
    
    mode = "Spectateur / Participant"
else:
    st.sidebar.success("🔒 Mode Administrateur Actif")
    if st.sidebar.button("🚪 Se déconnecter de l'admin"):
        st.session_state["is_admin"] = False
        st.rerun()
    mode = "Administrateur"

# ---------------------------------------------------------
# MODE 1 : SPECTATEUR / PARTICIPANT
# ---------------------------------------------------------
if mode == "Spectateur / Participant":
    st.info("💡 **Info :** Cette page se met à jour régulièrement pour intégrer les nouveaux participants au fur et à mesure des validations !")
    
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>⏳ Sablier du Tirage & En Direct</h3>", unsafe_allow_html=True)
    
    participants_js = json.dumps(data["participants_acceptes"], ensure_ascii=False)
    gagnant_actuel = data["gagnant"] if data["gagnant"] else ""
    etat_actuel = data["etat_tirage"]
    string_heure_js = data["heure_tirage"].replace(" ", "T") # Format ISO pour JS

    live_html = f"""
    <div id="container" style="text-align: center; font-family: sans-serif; padding: 5px;">
        <!-- Compte à rebours fluide -->
        <div id="countdown-box" style="display: flex; justify-content: center; gap: 12px; margin-bottom: 10px;">
            <div style="background: #1e293b; color: white; padding: 10px; border-radius: 8px; min-width: 65px;">
                <span id="days" style="font-size: 22px; font-weight: bold; display: block;">0</span>
                <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Jours</span>
            </div>
            <div style="background: #1e293b; color: white; padding: 10px; border-radius: 8px; min-width: 65px;">
                <span id="hours" style="font-size: 22px; font-weight: bold; display: block;">0</span>
                <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Heures</span>
            </div>
            <div style="background: #1e293b; color: white; padding: 10px; border-radius: 8px; min-width: 65px;">
                <span id="minutes" style="font-size: 22px; font-weight: bold; display: block;">0</span>
                <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Min</span>
            </div>
            <div style="background: #1e293b; color: white; padding: 10px; border-radius: 8px; min-width: 65px;">
                <span id="seconds" style="font-size: 22px; font-weight: bold; display: block; color: #38bdf8;">0</span>
                <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Sec</span>
            </div>
        </div>
        <div id="countdown-text" style="font-size: 13px; color: gray; margin-bottom: 10px;">
            En attente du tirage officiel
        </div>

        <!-- Résultat final si déjà tiré -->
        <div id="winner-box" style="display: none; background: #d1fae5; color: #065f46; padding: 15px; border-radius: 10px; border: 2px solid #34d399;">
            <h2 style="margin: 0; font-size: 18px;">🏆 TADAM ! Le grand gagnant est :</h2>
            <p id="winner-name" style="font-size: 22px; font-weight: bold; margin: 5px 0 0 0;"></p>
        </div>
    </div>

    <script>
        const countDownDate = new Date("{string_heure_js}").getTime();
        let etatAdmin = "{etat_actuel}";
        let gagnantAdmin = "{gagnant_actuel}";

        function showWinnerUI(winner) {{
            document.getElementById("countdown-box").style.display = "none";
            document.getElementById("countdown-text").style.display = "none";
            document.getElementById("winner-box").style.display = "block";
            document.getElementById("winner-name").innerText = winner;
        }}

        if (etatAdmin === "Termine" && gagnantAdmin) {{
            showWinnerUI(gagnantAdmin);
        }} else {{
            const x = setInterval(function() {{
                const now = new Date().getTime();
                const distance = countDownDate - now;

                if (distance < 0) {{
                    clearInterval(x);
                    document.getElementById("days").innerText = "0";
                    document.getElementById("hours").innerText = "0";
                    document.getElementById("minutes").innerText = "0";
                    document.getElementById("seconds").innerText = "0";
                    document.getElementById("countdown-text").innerText = "⏰ Temps écoulé ! Actualisation imminente du gagnant...";
                    // Rafraîchir automatiquement la page pour déclencher l'affichage du gagnant calculé par Python
                    setTimeout(function() {{ window.location.reload(); }}, 2000);
                }} else {{
                    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

                    document.getElementById("days").innerText = days;
                    document.getElementById("hours").innerText = hours;
                    document.getElementById("minutes").innerText = minutes;
                    document.getElementById("seconds").innerText = seconds;
                }}
            }}, 1000);
        }}
    </script>
    """
    components.html(live_html, height=180)
    st.markdown("---")
    
    etat = data["etat_tirage"]
    if etat == "Termine" and data["gagnant"]:
        st.success(f"🏆 Le grand gagnant est : **{data['gagnant']}** ! Félicitations ! 🥳")
        st.balloons()
    else:
        st.warning("⏳ Le tirage va bientôt commencer... Restez connectés !")
        
    st.markdown("---")
    
    nb_participants = len(data["participants_acceptes"])
    st.subheader(f"✅ Participants Validés ({nb_participants})")
    
    if data["participants_acceptes"]:
        participants_tries = sorted(data["participants_acceptes"], key=lambda x: x.lower())
        col_p1, col_p2, col_p3 = st.columns(3)
        
        tiers = len(participants_tries) // 3
        reste = len(participants_tries) % 3
        fin_col1 = tiers + (1 if reste > 0 else 0)
        fin_col2 = fin_col1 + tiers + (1 if reste > 1 else 0)
        
        with col_p1:
            for p in participants_tries[:fin_col1]: st.write(f"- 👤 {p}")
        with col_p2:
            for p in participants_tries[fin_col1:fin_col2]: st.write(f"- 👤 {p}")
        with col_p3:
            for p in participants_tries[fin_col2:]: st.write(f"- 👤 {p}")
    else:
        st.write("Aucun participant validé pour le moment.")
        
    st.markdown("---")
    nb_refuses = len(data["participants_refuses"])
    st.subheader(f"❌ Inscriptions Refusées ({nb_refuses})")
    if data["participants_refuses"]:
        for r in sorted(data["participants_refuses"], key=lambda x: x['nom'].lower()):
            st.write(f"- 🛑 **{r['nom']}** (*Raison : {r['raison']}*)")
    else:
        st.write("Aucun refus.")
        
    if st.button("🔄 Rafraîchir la page"):
        st.rerun()

# ---------------------------------------------------------
# MODE 2 : ADMINISTRATEUR
# ---------------------------------------------------------
else:
    nb_visites = st.session_state.get("visit_count", 1)
    st.sidebar.markdown(f"📊 **Statistiques :** `{nb_visites}` visites sur l'appli.")

    st.header("🛠️ Espace Administrateur - Panneau de Gestion")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📝 Participants", "⏰ Heure & Tirage", "🗑️ Gestion & Reset"])
    
    with tab1:
        st.subheader("➕ Ajouter des participants")
        texte_noms = st.text_area("Collez les noms (un par ligne) :", height=150)
        if st.button("Enregistrer les participants"):
            if texte_noms.strip():
                ajoutes = 0
                for ligne in texte_noms.split("\n"):
                    nom = ligne.strip()
                    if nom and nom not in data["participants_acceptes"]:
                        data["participants_acceptes"].append(nom)
                        ajoutes += 1
                save_data(data)
                st.success(f"🎉 {ajoutes} ajouté(s) avec succès !")
                st.rerun()

    with tab2:
        st.subheader("⏰ Configurer l'heure du tirage automatique")
        st.write(f"Heure actuelle enregistrée : `{data['heure_tirage']}`")
        
        # Formulaire simple pour changer l'heure cible si besoin
        nouvelle_heure = st.text_input("Modifier l'heure (Format AAAA-MM-JJ HH:MM:SS)", value=data["heure_tirage"])
        if st.button("Enregistrer la nouvelle heure cible"):
            data["heure_tirage"] = nouvelle_heure
            save_data(data)
            st.success("Heure de tirage mise à jour avec succès !")
            st.rerun()

        st.markdown("---")
        st.subheader("🎲 Tirage Manuel Immédiat")
        if data["participants_acceptes"]:
            if data["etat_tirage"] == "Termine":
                st.warning(f"⚠️ Le tirage a déjà été effectué ! Le gagnant actuel est **{data['gagnant']}**.")
            
            if st.button("🎲 LANCER LE VRAI TIRAGE MAINTENANT !"):
                gagnant = random.choice(data["participants_acceptes"])
                data["etat_tirage"] = "Termine"
                data["gagnant"] = gagnant
                save_data(data)
                st.balloons()
                st.success(f"🏆 Le grand gagnant officiel est : **{gagnant}** !")
                st.rerun()
        else:
            st.warning("Ajoutez des participants d'abord.")

        if data["etat_tirage"] == "Termine":
            st.markdown("---")
            if st.button("🔄 Effacer le gagnant / Réinitialiser le tirage"):
                data["etat_tirage"] = "En attente"
                data["gagnant"] = None
                save_data(data)
                st.success("Tirage réinitialisé !")
                st.rerun()

    with tab3:
        st.subheader("🗑️ Gestion et Réinitialisation")
        if st.button("🗑️ Tout effacer (Participants + Refus + Gagnant)"):
            default_data = {
                "participants_acceptes": [],
                "participants_refuses": [],
                "gagnant": None,
                "etat_tirage": "En attente",
                "heure_tirage": "2026-09-25 16:40:00"
            }
            save_data(default_data)
            st.success("Remis à zéro complet !")
            st.rerun()

# ---------------------------------------------------------
# PIED DE PAGE (FOOTER)
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 15px; font-size: 13px; color: #64748b; background-color: #1e293b; border-radius: 10px; margin-top: 30px;">
    Codé en Python par <a href="https://www.facebook.com/profile.php?id=100073514276062" target="_blank" style="color: #38bdf8; text-decoration: none; font-weight: bold;">Seb Capturis</a> 
    pour le groupe Facebook <a href="https://www.facebook.com/groups/bouce/" target="_blank" style="color: #38bdf8; text-decoration: none; font-weight: bold;">La Place du Village - ALLIER (03)</a> 🌲🏡
</div>
""", unsafe_allow_html=True)
