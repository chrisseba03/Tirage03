import json
import os
import random
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# Configuration de la page
st.set_page_config(page_title="Le Grand Tirage au Sort", page_icon="🎉", layout="centered")

DATA_FILE = "tirage_data.json"
VISITS_FILE = "visits_count.json"
ADMIN_PASSWORD = "admin170767"

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

def track_visit():
    visits = 1
    if os.path.exists(VISITS_FILE):
        try:
            with open(VISITS_FILE, "r") as f:
                visits = json.load(f).get("count", 1) + 1
        except:
            pass
    with open(VISITS_FILE, "w", encoding="utf-8") as f:
        json.dump({"count": visits}, f)
    return visits

if "visited" not in st.session_state:
    st.session_state["visited"] = True
    st.session_state["visit_count"] = track_visit()

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# ---------------------------------------------------------
# POINT DE CONTRÔLE SÉCURISÉ (ENREGISTREMENT DU GAGNANT EXACT)
# ---------------------------------------------------------
query_params = st.query_params
if "action" in query_params and query_params["action"] == "execute_draw":
    data_live = load_data()
    if not data_live["gagnant"] and data_live["participants_acceptes"]:
        # On récupère LE nom exact sur lequel l'animation s'est arrêtée
        gagnant_recu = query_params.get("winner", None)
        if gagnant_recu and gagnant_recu in data_live["participants_acceptes"]:
            data_live["gagnant"] = gagnant_recu
        else:
            # Sécurité de secours si le paramètre est absent
            data_live["gagnant"] = data_live["participants_acceptes"][0]
            
        data_live["etat_tirage"] = "Termine"
        save_data(data_live)
    
    st.query_params.clear()
    st.rerun()

data = load_data()

st.title("🎉 Le Grand Tirage au Sort en Direct")
st.write("Bienvenue sur le direct officiel ! Suivez le tirage au sort de chez vous en toute transparence. 🍀")

# ---------------------------------------------------------
# BARRE LATÉRALE - ESPACE ADMIN
# ---------------------------------------------------------
st.sidebar.header("⚙️ Espace Sécurisé")

if not st.session_state["is_admin"]:
    st.sidebar.info("👥 Mode : **Spectateur / Participant** (Lecture seule)")
    st.sidebar.markdown("---")
    
    with st.sidebar.expander("🔐 Accès Administrateur"):
        pwd_input = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if pwd_input == ADMIN_PASSWORD:
                st.session_state["is_admin"] = True
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Mot de passe incorrect.")
    mode_actuel = "Public"
else:
    st.sidebar.success("🔒 Mode Administrateur Actif")
    if st.sidebar.button("🚪 Se déconnecter"):
        st.session_state["is_admin"] = False
        st.rerun()
    mode_actuel = "Admin"

# ---------------------------------------------------------
# AFFICHAGE DU RÉSULTAT FINAL (VERROUILLÉ)
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
    
    st.success("🔒 **Tirage verrouillé par le système.** Même en actualisant la page 100 fois, ce résultat est immuable.")

# ---------------------------------------------------------
# EN ATTENTE DU TIRAGE (COMPTE À REBOURS + ANIMATION UNIQUE)
# ---------------------------------------------------------
else:
    st.info("💡 **Le saviez-vous ?** Le compte à rebours ci-dessous est synchronisé. À l'heure dite, l'animation désignera le vainqueur sous vos yeux !")
    st.markdown("---")
    
    participants_json = json.dumps(data["participants_acceptes"], ensure_ascii=False)
    
    live_animation_html = f"""
    <div style="text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 10px;">
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
        <div id="status-text" style="font-size: 14px; color: #64748b; margin-bottom: 15px; font-weight: 500;">
            En attente de l'heure du tirage (18h52)...
        </div>

        <div id="loto-container" style="display: none; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
            <h3 style="margin: 0 0 15px 0; font-size: 20px; letter-spacing: 1px;">🎰 TIRAGE AU SORT EN COURS...</h3>
            <div id="loto-ball" style="margin: 0 auto; width: 130px; height: 130px; background: #fbbf24; color: #1e293b; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: bold; text-align: center; padding: 10px; box-shadow: inset 0 5px 10px rgba(255,255,255,0.7), 0 8px 15px rgba(0,0,0,0.3); word-break: break-word;">
                Mélange...
            </div>
        </div>
    </div>

    <script>
        const participants = {participants_json};
        const targetTime = new Date("September 25, 2026 18:52:00").getTime();
        let animationTriggered = false;

        const timer = setInterval(function() {{
            const now = new Date().getTime();
            const distance = targetTime - now;

            if (distance < 0) {{
                clearInterval(timer);
                document.getElementById("days").innerText = "0";
                document.getElementById("hours").innerText = "0";
                document.getElementById("minutes").innerText = "0";
                document.getElementById("seconds").innerText = "0";
                
                if (participants.length > 0) {{
                    if (animationTriggered) return;
                    animationTriggered = true;

                    document.getElementById("countdown-box").style.display = "none";
                    document.getElementById("status-text").style.display = "none";
                    document.getElementById("loto-container").style.display = "block";

                    let counter = 0;
                    let selectedWinner = "";
                    
                    const spinInterval = setInterval(function() {{
                        selectedWinner = participants[Math.floor(Math.random() * participants.length)];
                        document.getElementById("loto-ball").innerText = selectedWinner;
                        counter++;
                        
                        if (counter > 22) {{
                            clearInterval(spinInterval);
                            // TRANSMISSION DIRECTE DU GAGNANT EXACT VISUEL AU SERVEUR
                            const cleanBaseUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
                            window.top.location.href = cleanBaseUrl + "?action=execute_draw&winner=" + encodeURIComponent(selectedWinner);
                        }}
                    }}, 150);
                }} else {{
                    document.getElementById("status-text").innerText = "Heure atteinte, mais aucun participant enregistré !";
                }}
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
    </script>
    """
    components.html(live_animation_html, height=225)

# ---------------------------------------------------------
# LISTES PUBLIQUE
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

if st.button("🔄 Rafraîchir la page"):
    st.rerun()

# ---------------------------------------------------------
# PANNEAU ADMIN
# ---------------------------------------------------------
if mode_actuel == "Admin":
    st.markdown("---")
    st.header("🛠️ Panneau de Gestion Administrateur")
    
    tab_add, tab_test, tab_reset = st.tabs(["📝 Gestion des Participants", "🎲 Actions & Tests", "🗑️ Réinitialisation"])
    
    with tab_add:
        st.subheader("➕ Ajouter des participants")
        noms_input = st.text_area("Collez les noms (un par ligne) :", height=140)
        if st.button("Enregistrer les nouveaux participants"):
            if noms_input.strip():
                cur_data = load_data()
                lignes = noms_input.split("\n")
                added = 0
                for ligne in lignes:
                    nom = ligne.strip()
                    if nom and nom not in cur_data["participants_acceptes"]:
                        cur_data["participants_acceptes"].append(nom)
                        added += 1
                save_data(cur_data)
                st.success(f"✅ {added} participant(s) ajouté(s) !")
                st.rerun()
                
        st.markdown("---")
        st.subheader("🛑 Enregistrer un refus")
        with st.form("refus_form"):
            ref_nom = st.text_input("Nom")
            ref_raison = st.text_input("Motif")
            if st.form_submit_button("Ajouter aux refus") and ref_nom:
                cur_data = load_data()
                cur_data["participants_refuses"].append({"nom": ref_nom, "raison": ref_raison})
                save_data(cur_data)
                st.success("Refus enregistré.")
                st.rerun()

    with tab_test:
        st.subheader("⚡ Forcer le Vrai Tirage Immédiatement")
        cur_data = load_data()
        if cur_data["participants_acceptes"]:
            if st.button("🎲 DÉCLENCHER LE TIRAGE OFFICIEL MAINTENANT"):
                if not cur_data["gagnant"]:
                    gagnant_force = random.choice(cur_data["participants_acceptes"])
                    cur_data["gagnant"] = gagnant_force
                    cur_data["etat_tirage"] = "Termine"
                    save_data(cur_data)
                    st.success(f"🏆 Gagnant officiel désigné : {gagnant_force}")
                    st.rerun()
        else:
            st.warning("Ajoutez des participants avant.")

    with tab_reset:
        st.subheader("🗑️ Remise à zéro")
        cur_data = load_data()
        
        if cur_data["gagnant"]:
            if st.button("🔄 Déverrouiller et effacer le gagnant (Nouveau tirage)"):
                cur_data["gagnant"] = None
                cur_data["etat_tirage"] = "En attente"
                save_data(cur_data)
                st.success("Jeu réinitialisé !")
                st.rerun()
            st.markdown("---")
            
        if st.button("🗑️ Effacer TOUTES les données"):
            reset_data = {
                "participants_acceptes": [],
                "participants_refuses": [],
                "gagnant": None,
                "etat_tirage": "En attente"
            }
            save_data(reset_data)
            st.success("Remise à zéro complète.")
            st.rerun()

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 15px; font-size: 13px; color: #64748b; background-color: #1e293b; border-radius: 10px; margin-top: 30px;">
    Application officielle développée par Seb Capturis pour le groupe La Place du Village - ALLIER (03) 🌲🏡
</div>
""", unsafe_allow_html=True)
