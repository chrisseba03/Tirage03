import json
import os
import random
import time
from datetime import datetime, timezone, timedelta
import streamlit as st
from streamlit_autorefresh import st_autorefresh

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
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

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
        with open(VISITS_FILE, "r", encoding="utf-8") as f:
            st.session_state["visit_count"] = json.load(f).get("count", 1)

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

data = load_data()

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
    # Rafraîchissement automatique de la page toutes les 3 secondes pour voir le direct
    st_autorefresh(interval=3000, key="datarefresh")

    st.info("💡 **Info :** Cette page se met à jour régulièrement pour intégrer les nouveaux participants au fur et à mesure des validations !")
    
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>⏳ Sablier du Tirage & Compte à Rebours</h3>", unsafe_allow_html=True)
    
    tz_france = timezone(timedelta(hours=2))
    cible = datetime(2026, 10, 4, 20, 0, 0, tzinfo=tz_france)
    maintenant = datetime.now(tz_france)
    delta = cible - maintenant
    
    if delta.total_seconds() > 0 and data["etat_tirage"] == "En attente":
        jours = delta.days
        heures, reste = divmod(delta.seconds, 3600)
        minutes, secondes = divmod(reste, 60)
        
        st.markdown(f"""
        <div style="text-align: center; font-size: 20px; font-weight: bold; background-color: #1e293b; color: white; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
            ⏳ {jours} Jours, {heures}h {minutes}m {secondes}s restants<br>
            <span style="font-size: 13px; color: #38bdf8;">Fermeture et tirage le Dimanche 4 octobre 2026 à 20h00</span>
        </div>
        """, unsafe_allow_html=True)
    
    etat = data["etat_tirage"]
    if etat == "En cours":
        st.warning("🎰 **Le tirage est en train d'être effectué en direct ! Restez attentifs...**")
    elif etat == "Termine" and data["gagnant"]:
        st.success(f"🏆 **TADAM ! Le grand gagnant est : {data['gagnant']}** ! Félicitations ! 🥳")
        st.balloons()
    else:
        st.warning("⏳ Le tirage va bientôt commencer... Restez connectés !")
        
    st.markdown("---")
    
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
                lignes = texte_noms.split("\n")
                ajoutes = 0
                doublons = 0
                for ligne in lignes:
                    nom = ligne.strip()
                    if nom:
                        if nom not in data["participants_acceptes"]:
                            data["participants_acceptes"].append(nom)
                            ajoutes += 1
                        else:
                            doublons += 1
                            
                save_data(data)
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
                data["participants_refuses"].append({"nom": n_ref, "raison": r_ref})
                save_data(data)
                st.success("Refusé enregistré !")
                st.rerun()

    with tab2:
        st.subheader("🧪 Test à blanc de l'animation")
        st.write("Testez l'animation des boules de loto et le TADAM directement ici.")
        if st.button("🧪 LANCER UN TEST À BLANC"):
            if data["participants_acceptes"]:
                st.info("🎰 Mélange des boules magiques...")
                placeholder = st.empty()
                for _ in range(12):
                    temp_winner = random.choice(data["participants_acceptes"])
                    placeholder.markdown(f"<h3 style='text-align: center; color: #3b82f6;'>🌀 Boule en cours : {temp_winner}</h3>", unsafe_allow_html=True)
                    time.sleep(0.2)
                
                gagnant_test = random.choice(data["participants_acceptes"])
                placeholder.empty()
                st.success(f"🧪 **[TEST À BLANC] TADAM ! Le gagnant simulé est : {gagnant_test}** 🥳")
                st.balloons()
            else:
                st.warning("Ajoutez d'abord des participants pour faire tourner les boules !")

        st.markdown("---")
        st.subheader("🎲 Lancer le Vrai Tirage Officiel")
        if data["participants_acceptes"]:
            st.write(f"Participants validés actuels : {len(data['participants_acceptes'])}")
            if st.button("🎲 LANCER LE VRAI TIRAGE MAINTENANT !"):
                # 1. On passe l'état en "En cours" pour que la vue participant affiche le suspense
                data["etat_tirage"] = "En cours"
                save_data(data)
                
                # 2. Animation des boules dans l'admin
                with st.spinner("Suspense... Les boules tournent dans le boulier ! 🪄"):
                    placeholder = st.empty()
                    for _ in range(15):
                        temp_winner = random.choice(data["participants_acceptes"])
                        placeholder.markdown(f"<h3 style='text-align: center; color: #f59e0b;'>🎰 Tirage... {temp_winner}</h3>", unsafe_allow_html=True)
                        time.sleep(0.25)
                    
                    # 3. Désignation finale du gagnant
                    gagnant = random.choice(data["participants_acceptes"])
                    data["gagnant"] = gagnant
                    data["etat_tirage"] = "Termine"
                    save_data(data)
                    placeholder.empty()
                
                st.balloons()
                st.success(f"🏆 Le grand gagnant officiel est : **{gagnant}** !")
                st.rerun()
        else:
            st.warning("Ajoutez des participants d'abord.")

        st.markdown("---")
        if data["etat_tirage"] == "Termine":
            if st.button("🔄 Effacer le gagnant / Réinitialiser le tirage"):
                data["etat_tirage"] = "En attente"
                data["gagnant"] = None
                save_data(data)
                st.success("Tirage réinitialisé ! Le gagnant a été effacé.")
                st.rerun()

    with tab3:
        st.subheader("🗑️ Gestion et Réinitialisation")
        
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
        st.markdown("##### Suppression ciblée")
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
