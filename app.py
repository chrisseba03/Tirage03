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
# POINT DE CONTRÔLE SÉCURISÉ (ENDPOINT INTERNE DE TIRAGE)
# ---------------------------------------------------------
query_params = st.query_params
if "action" in query_params and query_params["action"] == "execute_draw":
    data_live = load_data()
    # VÉRIFICATION INCONTESTABLE : Si aucun gagnant n'a encore été désigné et qu'il y a des participants
    if not data_live["gagnant"] and data_live["participants_acceptes"]:
        gagnant_officiel = random.choice(data_live["participants_acceptes"])
        data_live["gagnant"] = gagnant_officiel
        data_live["etat_tirage"] = "Termine"
        save_data(data_live)
    
    # Nettoyage des paramètres URL pour repartir sur une URL propre
    st.query_params.clear()
    st.rerun()

# Chargement des données actuelles pour l'affichage
data = load_data()

st.title("🎉 Le Grand Tirage au Sort en Direct")
st.write("Bienvenue sur le direct officiel ! Suivez le tirage au sort de chez vous en toute transparence. 🍀")

# ---------------------------------------------------------
# BARRE LATÉRALE - ESPACE ADMIN SÉCURISÉ
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
# AFFICHAGE PRINCIPAL : SI LE GAGNANT EXISTE DÉJÀ (VERROUILLÉ)
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
    
    st.success("🔒 **Tirage verrouillé par le système.** Même en actualisant la page, ce résultat est immuable.")

# ---------------------------------------------------------
# AFFICHAGE PRINCIPAL : EN ATTENTE DU TIRAGE (COMPTE À REBOURS + LIVE)
# ---------------------------------------------------------
else:
    st.info("💡 **Le saviez-vous ?** Le compte à rebours ci-dessous est synchronisé. À 18h52, l'animation se lancera automatiquement pour désigner le vainqueur sous vos yeux !")
    st.markdown("---")
    
    participants_json = json.dumps(data["participants_acceptes"], ensure_ascii=False)
    
    # Composant HTML/JS totalement autonome pour le live type FDJ
    live_animation_html = f"""
    <div style="text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 10px;">
        <!-- Compte à rebours -->
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

        <!-- Sphère de tirage animée (style Loto/FDJ) -->
        <div id="loto-container" style="display: none; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
            <h3 style="margin: 0 0 15px 0; font-size: 20px; letter-spacing: 1px;">🎰 TIRAGE AU SORT EN COURS...</h3>
            <div id="loto-ball" style="margin: 0 auto; width: 130px; height: 130px; background: #fbbf24; color: #1e293b; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: bold; text-align: center; padding: 10px; box-shadow: inset 0 5px 10px rgba(255,255,255,0.7), 0 8px 15px rgba(0,0,0,0.3); word-break: break-word;">
                Mélange...
            </div>
        </div>
    </div>

    <script>
        const participants = {participants_json};
        // Date cible du tirage : 25 septembre 2026 à 18h52:00
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

                    // Masquer le compte à rebours et afficher la boule de tirage
                    document.getElementById("countdown-box").style.display = "none";
                    document.getElementById("status-text").style.display = "none";
                    document.getElementById("loto-container").style.display = "block";

                    let counter = 0;
                    // Effet de roulement de tambour pendant ~3.5 secondes
                    const spinInterval = setInterval(function() {{
                        const randomName = participants[Math.floor(Math.random() * participants.length)];
                        document.getElementById("loto-ball").innerText = randomName;
                        counter++;
                        
                        if (counter > 22) {{
                            clearInterval(spinInterval);
                            // Redirection propre vers le point de validation sécurisé du serveur
                            const cleanBaseUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
                            window.top.location.href = cleanBaseUrl + "?action=execute_draw";
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
# LISTE PUBLIQUE DES PARTICIPANTS VALIDÉS & REFUSÉS
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
# PANNEAU ADMINISTRATEUR COMPLET (UNIQUEMENT ACCESSIBLE SI CONNECTÉ)
# ---------------------------------------------------------
if mode_actuel == "Admin":
    st.markdown("---")
    st.header("🛠️ Panneau de Gestion Administrateur")
    
    tab_add, tab_test, tab_reset = st.tabs(["📝 Gestion des Participants", "🎲 Actions & Tests", "🗑️ Réinitialisation"])
    
    with tab_add:
        st.subheader("➕ Ajouter des participants en masse")
        noms_input = st.text_area("Collez les noms (un par ligne) :", height=140, placeholder="Jean Dupont\nMarie Curie...")
        if st.button("Enregistrer les nouveaux participants"):
            if noms_input.strip():
                cur_data = load_data()
                lignes = noms_input.split("\n")
                added = 0
                duplicates = 0
                for ligne in lignes:
                    nom = ligne.strip()
                    if nom:
                        if nom not in cur_data["participants_acceptes"]:
                            cur_data["participants_acceptes"].append(nom)
                            added += 1
                        else:
                            duplicates += 1
                save_data(cur_data)
                st.success(f"✅ {added} participant(s) ajouté(s) avec succès ! ({duplicates} doublon(s) ignoré(s))")
                st.rerun()
                
        st.markdown("---")
        st.subheader("🛑 Enregistrer un refus")
        with st.form("refus_form"):
            ref_nom = st.text_input("Nom de la personne refusée")
            ref_raison = st.text_input("Motif du refus (ex: Hors délai, Organisateur...)")
            if st.form_submit_button("Ajouter aux refus") and ref_nom:
                cur_data = load_data()
                cur_data["participants_refuses"].append({"nom": ref_nom, "raison": ref_raison})
                save_data(cur_data)
                st.success("Refus enregistré.")
                st.rerun()

    with tab_test:
        st.subheader("🧪 Test à blanc de l'animation")
        st.write("Testez l'animation du tirage sans toucher aux données officielles.")
        if st.button("Lancer un test visuel à blanc"):
            cur_data = load_data()
            if cur_data["participants_acceptes"]:
                placeholder = st.empty()
                for _ in range(10):
                    t_win = random.choice(cur_data["participants_acceptes"])
                    placeholder.markdown(f"<h3 style='text-align: center; color: #2563eb;'>🌀 Simulation en cours : {t_win}</h3>", unsafe_allow_html=True)
                    import time
                    time.sleep(0.15)
                sim_win = random.choice(cur_data["participants_acceptes"])
                placeholder.empty()
                st.success(f"🧪 Résultat du test à blanc : **{sim_win}** 🎉")
            else:
                st.warning("Veuillez d'abord ajouter des participants.")

        st.markdown("---")
        st.subheader("⚡ Forcer le Vrai Tirage Immédiatement")
        st.write("Si vous souhaitez déclencher le tirage officiel avant l'heure prévue :")
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
            st.warning("Ajoutez des participants avant de lancer le tirage.")

    with tab_reset:
        st.subheader("🗑️ Remise à zéro")
        cur_data = load_data()
        
        if cur_data["gagnant"]:
            if st.button("🔄 Déverrouiller et effacer le gagnant (Nouveau tirage)"):
                cur_data["gagnant"] = None
                cur_data["etat_tirage"] = "En attente"
                save_data(cur_data)
                st.success("Jeu réinitialisé, prêt pour un nouveau tirage !")
                st.rerun()
            st.markdown("---")
            
        if st.button("🗑️ Effacer TOUTES les données (Participants, refus, gagnant)"):
            reset_data = {
                "participants_acceptes": [],
                "participants_refuses": [],
                "gagnant": None,
                "etat_tirage": "En attente"
            }
            save_data(reset_data)
            st.success("Remise à zéro complète effectuée.")
            st.rerun()

        st.markdown("---")
        with st.expander("Gérer / Supprimer des participants unitaires"):
            if cur_data["participants_acceptes"]:
                for p in sorted(cur_data["participants_acceptes"], key=lambda x: x.lower()):
                    col_a, col_b = st.columns([3, 1])
                    col_a.write(f"👤 {p}")
                    if col_b.button("Supprimer", key=f"del_p_{p}"):
                        cur_data["participants_acceptes"].remove(p)
                        save_data(cur_data)
                        st.rerun()
            else:
                st.write("Aucun participant.")

# ---------------------------------------------------------
# PIED DE PAGE OFFICIEL
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 15px; font-size: 13px; color: #64748b; background-color: #1e293b; border-radius: 10px; margin-top: 30px;">
    Application officielle développée par <a href="https://www.facebook.com/profile.php?id=100073514276062" target="_blank" style="color: #38bdf8; text-decoration: none; font-weight: bold;">Seb Capturis</a> 
    pour le groupe <a href="https://www.facebook.com/groups/bouce/" target="_blank" style="color: #38bdf8; text-decoration: none; font-weight: bold;">La Place du Village - ALLIER (03)</a> 🌲🏡
</div>
""", unsafe_allow_html=True)
