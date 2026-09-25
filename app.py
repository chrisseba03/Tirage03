import json
import os
import random
import time
from datetime import datetime, timezone, timedelta
import streamlit as st
import streamlit.components.v1 as components

DATA_FILE = "tirage_data.json"
VISITS_FILE = "visits_count.json"

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
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

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
    with open(VISITS_FILE, "w") as f:
        json.dump({"count": visits}, f)
    return visits

if "visited" not in st.session_state:
    st.session_state["visited"] = True
    st.session_state["visit_count"] = track_visit()
else:
    if os.path.exists(VISITS_FILE):
        with open(VISITS_FILE, "r") as f:
            st.session_state["visit_count"] = json.load(f).get("count", 1)

data = load_data()

st.title("🎉 Le Grand Tirage au Sort en Direct !")
st.write("Suivez le tirage en temps réel et découvrez si la chance vous sourit ! 🍀")

st.sidebar.header("⚙️ Configuration")
mode = st.sidebar.radio("Je suis :", ["Spectateur / Participant", "Administrateur"])

# ---------------------------------------------------------
# MODE 1 : SPECTATEUR / PARTICIPANT
# ---------------------------------------------------------
if mode == "Spectateur / Participant":
    st.info("💡 **Info :** Cette page se met à jour régulièrement pour intégrer les nouveaux participants au fur et à mesure des validations !")
    
    # Compte à rebours dynamique en blocs (Style Jours / Heures / Minutes / Secondes)
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>⏳ Sablier du Tirage</h3>", unsafe_allow_html=True)
    
    # Code HTML + JS pour le compte à rebours fluide en direct (Objectif : 4 octobre 2026 à 20:00:00)
    countdown_html = """
    <div style="display: flex; justify-content: center; gap: 15px; text-align: center; font-family: sans-serif; margin-bottom: 10px;">
        <div style="background: #1e293b; color: white; padding: 12px; border-radius: 10px; min-width: 75px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <span id="days" style="font-size: 26px; font-weight: bold; display: block;">0</span>
            <span style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Jours</span>
        </div>
        <div style="background: #1e293b; color: white; padding: 12px; border-radius: 10px; min-width: 75px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <span id="hours" style="font-size: 26px; font-weight: bold; display: block;">0</span>
            <span style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Heures</span>
        </div>
        <div style="background: #1e293b; color: white; padding: 12px; border-radius: 10px; min-width: 75px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <span id="minutes" style="font-size: 26px; font-weight: bold; display: block;">0</span>
            <span style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Min</span>
        </div>
        <div style="background: #1e293b; color: white; padding: 12px; border-radius: 10px; min-width: 75px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <span id="seconds" style="font-size: 26px; font-weight: bold; display: block; color: #38bdf8;">0</span>
            <span style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Sec</span>
        </div>
    </div>
    <div style="text-align: center; font-size: 14px; color: gray; margin-bottom: 10px;">
        Fermeture et tirage le Dimanche 4 octobre 2026 à 20h00
    </div>

    <script>
        const countDownDate = new Date("October 4, 2026 20:00:00").getTime();

        const x = setInterval(function() {
            const now = new Date().getTime();
            const distance = countDownDate - now;

            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            document.getElementById("days").innerText = days;
            document.getElementById("hours").innerText = hours;
            document.getElementById("minutes").innerText = minutes;
            document.getElementById("seconds").innerText = seconds;

            if (distance < 0) {
                clearInterval(x);
                document.getElementById("days").innerText = "0";
                document.getElementById("hours").innerText = "0";
                document.getElementById("minutes").innerText = "0";
                document.getElementById("seconds").innerText = "0";
            }
        }, 1000);
    </script>
    """
    components.html(countdown_html, height=110)
    st.markdown("---")

    etat = data["etat_tirage"]
    if etat == "En attente":
        st.warning("⏳ Le tirage va bientôt commencer... Restez connectés !")
    elif etat == "En cours":
        st.info("🎰 Le suspense est à son comble... Le tirage est en cours !")
    elif etat == "Termine" and data["gagnant"]:
        st.success(f"🏆 Le grand gagnant est : **{data['gagnant']}** ! Félicitations ! 🥳")
    
    col1, col2 = st.columns(2)
    with col1:
        nb_participants = len(data["participants_acceptes"])
        st.subheader(f"✅ Participants Validés ({nb_participants})")
        if data["participants_acceptes"]:
            for p in data["participants_acceptes"]:
                st.write(f"- 👤 {p}")
        else:
            st.write("Aucun participant validé pour le moment.")
            
    with col2:
        nb_refuses = len(data["participants_refuses"])
        st.subheader(f"❌ Inscriptions Refusées ({nb_refuses})")
        if data["participants_refuses"]:
            for r in data["participants_refuses"]:
                st.write(f"- 🛑 **{r['nom']}** (*Raison : {r['raison']}*)")
        else:
            st.write("Aucun refus.")
            
    if st.button("🔄 Rafraîchir la page"):
        st.rerun()

# ---------------------------------------------------------
# MODE 2 : ADMINISTRATEUR (DOUBLE VUE + COMPTEUR)
# ---------------------------------------------------------
else:
    st.sidebar.success("🔒 Mode Administrateur activé")
    
    nb_visites = st.session_state.get("visit_count", 1)
    st.sidebar.markdown(f"📊 **Statistiques :** `{nb_visites}` visites sur l'appli.")

    st.header("🛠️ Espace Administrateur - Double Vue en Direct")
    
    col_admin, col_live = st.columns(2, gap="medium")
    
    with col_admin:
        st.subheader("⚙️ Panneau de Gestion")
        
        tab1, tab2, tab3 = st.tabs(["📝 Ajouter", "🎲 Tirage", "🗑️ Reset"])
        
        with tab1:
            st.markdown("##### Ajouter des participants")
            texte_noms = st.text_area("Collez les noms (un par ligne) :", height=120, placeholder="Nom 1\nNom 2...")
            if st.button("➕ Enregistrer"):
                if texte_noms.strip():
                    lignes = texte_noms.split("\n")
                    ajoutes = 0
                    for ligne in lignes:
                        nom = ligne.strip()
                        if nom and nom not in data["participants_acceptes"]:
                            data["participants_acceptes"].append(nom)
                            ajoutes += 1
                    save_data(data)
                    st.success(f"🎉 {ajoutes} ajoutés !")
                    st.rerun()
            
            st.markdown("---")
            st.markdown("##### Enregistrer un refus")
            with st.form("form_refus_rapide"):
                n_ref = st.text_input("Nom")
                r_ref = st.text_input("Raison (ex: Organisateur)")
                if st.form_submit_button("Ajouter aux refusés") and n_ref:
                    data["participants_refuses"].append({"nom": n_ref, "raison": r_ref})
                    save_data(data)
                    st.success("Refusé !")
                    st.rerun()

        with tab2:
            st.markdown("##### Lancer le Tirage")
            if data["participants_acceptes"]:
                st.write(f"Participants validés : {len(data['participants_acceptes'])}")
                if st.button("🎲 LANCER LE TIRAGE !"):
                    data["etat_tirage"] = "En cours"
                    save_data(data)
                    
                    with st.spinner("Suspense... 🪄"):
                        placeholder = st.empty()
                        for _ in range(10):
                            temp_winner = random.choice(data["participants_acceptes"])
                            placeholder.markdown(f"### 🌀 *{temp_winner}* ...")
                            time.sleep(0.3)
                        
                        gagnant = random.choice(data["participants_acceptes"])
                        data["gagnant"] = gagnant
                        data["etat_tirage"] = "Termine"
                        save_data(data)
                    
                    st.balloons()
                    st.rerun()
            else:
                st.warning("Ajoutez des participants d'abord.")

        with tab3:
            st.markdown("##### Réinitialisation")
            if st.button("🗑️ Tout effacer / Reset"):
                default_data = {
                    "participants_acceptes": [],
                    "participants_refuses": [],
                    "gagnant": None,
                    "etat_tirage": "En attente"
                }
                save_data(default_data)
                st.success("Remis à zéro !")
                st.rerun()

        st.markdown("---")
        st.markdown("##### 🗑️ Suppression rapide")
        with st.expander("Gérer / Supprimer des participants validés"):
            if data["participants_acceptes"]:
                for i, p in enumerate(data["participants_acceptes"]):
                    c_a, c_b = st.columns([3, 1])
                    c_a.write(f"👤 {p}")
                    if c_b.button("❌", key=f"del_acc_{i}"):
                        data["participants_acceptes"].pop(i)
                        save_data(data)
                        st.rerun()
            else:
                st.write("Aucun participant.")

        with st.expander("Gérer / Supprimer des refusés"):
            if data["participants_refuses"]:
                for i, r in enumerate(data["participants_refuses"]):
                    c_a, c_b = st.columns([3, 1])
                    c_a.write(f"🛑 {r['nom']}")
                    if c_b.button("❌", key=f"del_ref_{i}"):
                        data["participants_refuses"].pop(i)
                        save_data(data)
                        st.rerun()
            else:
                st.write("Aucun refus.")

    # --- COLONNE DE DROITE : APERÇU LIVE ---
    with col_live:
        st.markdown("### 👀 Aperçu Live (Vue Participant)")
        st.markdown("---")
        
        etat = data["etat_tirage"]
        if etat == "En attente":
            st.warning("⏳ Le tirage va bientôt commencer...")
        elif etat == "En cours":
            st.info("🎰 Le tirage est en cours...")
        elif etat == "Termine" and data["gagnant"]:
            st.success(f"🏆 Gagnant : **{data['gagnant']}** !")
            
        st.markdown("#### Listes affichées en direct :")
        sub_c1, sub_c2 = st.columns(2)
        with sub_c1:
            st.markdown(f"**✅ Validés ({len(data['participants_acceptes'])})**")
            if data["participants_acceptes"]:
                for p in data["participants_acceptes"]:
                    st.write(f"- {p}")
            else:
                st.write("Vide")
                
        with sub_c2:
            st.markdown(f"**❌ Refusés ({len(data['participants_refuses'])})**")
            if data["participants_refuses"]:
                for r in data["participants_refuses"]:
                    st.write(f"- {r['nom']}")
            else:
                st.write("Aucun")
