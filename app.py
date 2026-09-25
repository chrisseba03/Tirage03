import json
import os
import random
import time
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

DATA_FILE = "tirage_data.json"
VISITS_FILE = "visits_count.json"

ADMIN_PASSWORD = "admin170767"

def load_data():
    # Désactivation du cache Streamlit pour forcer la lecture du fichier disque à chaque fois
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
else:
    if os.path.exists(VISITS_FILE):
        with open(VISITS_FILE, "r") as f:
            st.session_state["visit_count"] = json.load(f).get("count", 1)

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# Chargement permanent des données fraîches depuis le fichier disque
data = load_data()

# ---------------------------------------------------------
# ENDPOINT INTERNE : VERROUILLAGE DU TIRAGE CÔTÉ SERVEUR
# ---------------------------------------------------------
query_params = st.query_params
if "trigger_draw" in query_params:
    # Rechargement frais pour éviter les conflits de dernière seconde
    data_fresh = load_data()
    if data_fresh["etat_tirage"] == "En attente" and data_fresh["participants_acceptes"]:
        # Choix aléatoire unique basé sur les participants du fichier
        gagnant = random.choice(data_fresh["participants_acceptes"])
        data_fresh["etat_tirage"] = "Termine"
        data_fresh["gagnant"] = gagnant
        save_data(data_fresh)
    
    st.query_params.clear()
    st.rerun()

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
    # On rafraîchit l'état depuis le fichier pour voir si une autre machine a tiré le gagnant
    data = load_data()
    etat_actuel = data["etat_tirage"]
    
    if etat_actuel == "Termine" and data["gagnant"]:
        st.balloons()
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #10b981, #047857); padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.4); border: 6px solid #a7f3d0; margin-top: 20px; margin-bottom: 30px;">
            <h2 style="color: #a7f3d0; margin: 0; font-size: 26px; text-transform: uppercase; letter-spacing: 3px;">🏆 Le Grand Gagnant est 🏆</h2>
            <h1 style="color: white; font-size: 55px; margin: 25px 0; font-weight: 900; text-shadow: 3px 3px 10px rgba(0,0,0,0.5);">{data['gagnant']}</h1>
            <p style="color: #d1fae5; font-size: 20px; margin: 0; font-weight: bold;">Toutes nos félicitations ! 🎉🥂</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("🔒 **Le tirage est terminé et le résultat est définitivement verrouillé.** Le même gagnant s'affiche partout sur tous vos appareils.")

    else:
        st.info("💡 **Info :** Le tirage se lancera automatiquement à 18h37 dès que le compte à rebours arrivera à zéro !")
        st.markdown("---")
        st.markdown("<h3 style='text-align: center;'>⏳ Sablier du Tirage & En Direct</h3>", unsafe_allow_html=True)
        
        participants_js = json.dumps(data["participants_acceptes"], ensure_ascii=False)

        live_html = f"""
        <div id="container" style="text-align: center; font-family: sans-serif; padding: 10px;">
            <!-- Compte à rebours -->
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
                Tirage au sort automatique à l'échéance (18h37)
            </div>

            <!-- Zone d'Animation Loto -->
            <div id="loto-display" style="display: none; background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 25px; border-radius: 12px; box-shadow: 0 10px 20px rgba(0,0,0,0.2);">
                <h2 style="margin: 0 0 15px 0; font-size: 22px;">🎰 Le tirage est en cours !</h2>
                <div id="ball" style="margin: 0 auto; width: 140px; height: 140px; background: #fbbf24; color: #1e293b; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; text-align: center; padding: 10px; box-shadow: inset 0 4px 8px rgba(255,255,255,0.6), 0 6px 12px rgba(0,0,0,0.3); word-break: break-word;">
                    Suspense...
                </div>
            </div>
        </div>

        <script>
            const participants = {participants_js};
            const countDownDate = new Date("September 25, 2026 18:37:00").getTime();
            let animationLancee = false;

            const x = setInterval(function() {{
                const now = new Date().getTime();
                const distance = countDownDate - now;

                if (distance < 0) {{
                    clearInterval(x);
                    document.getElementById("days").innerText = "0";
                    document.getElementById("hours").innerText = "0";
                    document.getElementById("minutes").innerText = "0";
                    document.getElementById("seconds").innerText = "0";
                    
                    if (participants.length > 0) {{
                        if (animationLancee) return;
                        animationLancee = true;

                        document.getElementById("countdown-box").style.display = "none";
                        document.getElementById("countdown-text").style.display = "none";
                        document.getElementById("loto-display").style.display = "block";

                        let counter = 0;
                        const animInterval = setInterval(function() {{
                            const randomIndex = Math.floor(Math.random() * participants.length);
                            document.getElementById("ball").innerText = participants[randomIndex];
                            counter++;
                            
                            if (counter > 25) {{
                                clearInterval(animInterval);
                                const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
                                window.top.location.href = cleanUrl + "?trigger_draw=true";
                            }}
                        }}, 150);
                    }} else {{
                        document.getElementById("countdown-text").innerText = "Temps écoulé ! Aucun participant.";
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
        components.html(live_html, height=220)
        
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
            for p in participants_tries[:fin_col1]:
                st.write(f"- 👤 {p}")
        with col_p2:
            for p in participants_tries[fin_col1:fin_col2]:
                st.write(f"- 👤 {p}")
        with col_p3:
            for p in participants_tries[fin_col2:]:
                st.write(f"- 👤 {p}")
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
# MODE 2 : ADMINISTRATEUR (PANNEAU UNIQUE PLEINE PAGE)
# ---------------------------------------------------------
else:
    nb_visites = st.session_state.get("visit_count", 1)
    st.sidebar.markdown(f"📊 **Statistiques :** `{nb_visites}` visites sur l'appli.")

    st.header("🛠️ Espace Administrateur - Panneau de Gestion")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📝 Ajouter des participants", "🎲 Tirage & Tests", "🗑️ Gestion & Reset"])
    
    with tab1:
        st.subheader("➕ Ajouter des participants")
        texte_noms = st.text_area("Collez les noms (un par ligne) :", height=150, placeholder="Nom 1\nNom 2...")
        if st.button("Enregistrer les participants"):
            if texte_noms.strip():
                current_data = load_data()
                lignes = texte_noms.split("\n")
                ajoutes = 0
                doublons = 0
                for ligne in lignes:
                    nom = ligne.strip()
                    if nom:
                        if nom not in current_data["participants_acceptes"]:
                            current_data["participants_acceptes"].append(nom)
                            ajoutes += 1
                        else:
                            doublons += 1
                            
                save_data(current_data)
                msg = f"🎉 {ajoutes} ajouté(s) avec succès !"
                if doublons > 0:
                    msg += f" (⚠️ {doublons} doublon(s) ignoré(s))"
                st.success(msg)
                st.rerun()
        
        st.markdown("---")
        st.subheader("🛑 Enregistrer un refus")
        with st.form("form_refus_rapide"):
            n_ref = st.text_input("Nom du participant refusé")
            r_ref = st.text_input("Raison (ex: Organisateur, Hors critères...)")
            if st.form_submit_button("Ajouter aux refusés") and n_ref:
                current_data = load_data()
                current_data["participants_refuses"].append({"nom": n_ref, "raison": r_ref})
                save_data(current_data)
                st.success("Refusé enregistré !")
                st.rerun()

    with tab2:
        st.subheader("🧪 Test à blanc de l'animation")
        if st.button("🧪 LANCER UN TEST À BLANC"):
            current_data = load_data()
            if current_data["participants_acceptes"]:
                st.info("🎰 Mélange des boules magiques...")
                placeholder = st.empty()
                for _ in range(12):
                    temp_winner = random.choice(current_data["participants_acceptes"])
                    placeholder.markdown(f"<h3 style='text-align: center; color: #3b82f6;'>🌀 Boule en cours : {temp_winner}</h3>", unsafe_allow_html=True)
                    time.sleep(0.2)
                
                gagnant_test = random.choice(current_data["participants_acceptes"])
                placeholder.empty()
                st.success(f"🧪 **[TEST À BLANC] TADAM ! Le gagnant simulé est : {gagnant_test}** 🥳")
                st.balloons()
            else:
                st.warning("Ajoutez d'abord des participants !")

        st.markdown("---")
        st.subheader("🎲 Lancer le Vrai Tirage Manuel")
        current_data = load_data()
        if current_data["participants_acceptes"]:
            st.write(f"Participants validés actuels : {len(current_data['participants_acceptes'])}")
            if st.button("🎲 LANCER LE VRAI TIRAGE MAINTENANT !"):
                gagnant = random.choice(current_data["participants_acceptes"])
                current_data["etat_tirage"] = "Termine"
                current_data["gagnant"] = gagnant
                save_data(current_data)
                st.balloons()
                st.success(f"🏆 Le grand gagnant est : **{gagnant}** !")
                st.rerun()
        else:
            st.warning("Ajoutez des participants d'abord.")

    with tab3:
        st.subheader("🗑️ Gestion et Réinitialisation")
        current_data = load_data()
        
        if current_data["etat_tirage"] == "Termine":
            if st.button("🔄 Déverrouiller et Effacer le gagnant (Remise à zéro du jeu)"):
                current_data["etat_tirage"] = "En attente"
                current_data["gagnant"] = None
                save_data(current_data)
                st.success("Le tirage est de nouveau en attente. Prêt pour un nouveau lancer !")
                st.rerun()
            st.markdown("---")
            
        if st.button("🗑️ Tout effacer (Participants + Refus + Gagnant)"):
            default_data = {
                "participants_acceptes": [],
                "participants_refuses": [],
                "gagnant": None,
                "etat_tirage": "En attente"
            }
            save_data(default_data)
            st.success("Remis à zéro complet !")
            st.rerun()

        st.markdown("---")
        with st.expander("Gérer / Supprimer des participants validés"):
            if current_data["participants_acceptes"]:
                for p in sorted(current_data["participants_acceptes"], key=lambda x: x.lower()):
                    c_a, c_b = st.columns([3, 1])
                    c_a.write(f"👤 {p}")
                    if c_b.button("❌", key=f"del_acc_{p}"):
                        current_data["participants_acceptes"].remove(p)
                        save_data(current_data)
                        st.rerun()
            else:
                st.write("Aucun participant.")

        with st.expander("Gérer / Supprimer des refusés"):
            if current_data["participants_refuses"]:
                for i, r in enumerate(current_data["participants_refuses"]):
                    c_a, c_b = st.columns([3, 1])
                    c_a.write(f"🛑 {r['nom']}")
                    if c_b.button("❌", key=f"del_ref_{i}"):
                        current_data["participants_refuses"].pop(i)
                        save_data(current_data)
                        st.rerun()
            else:
                st.write("Aucun refus.")

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
