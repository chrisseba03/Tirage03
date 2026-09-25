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
            "etat_tirage": "En attente",
            "test_mode": False  # Indicateur pour forcer l'animation à blanc
        }
        save_data(default_data)
        return default_data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        # Sécurité pour les anciennes structures de données
        if "test_mode" not in data:
            data["test_mode"] = False
        return data

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
        with open(VISITS_FILE, "r", encoding="utf-8") as f:
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
    
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>⏳ Sablier du Tirage & Animation Automatique</h3>", unsafe_allow_html=True)
    
    participants_js = json.dumps(data["participants_acceptes"], ensure_ascii=False)
    gagnant_actuel = data["gagnant"] if data["gagnant"] else ""
    etat_actuel = data["etat_tirage"]
    test_mode_actif = "true" if data.get("test_mode", False) else "false"

    loto_html = f"""
    <div id="container" style="text-align: center; font-family: sans-serif; padding: 15px;">
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
        <div id="countdown-text" style="font-size: 13px; color: gray; margin-bottom: 15px;">
            Fermeture et tirage automatique le Dimanche 4 octobre 2026 à 20h00
        </div>

        <!-- Zone d'Animation Loto -->
        <div id="loto-display" style="display: none; background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.2);">
            <h2 id="loto-title" style="margin: 0; font-size: 20px;">🎰 Tirage en cours de la boule magique...</h2>
            <div id="ball" style="margin: 20px auto; width: 140px; height: 140px; background: #fbbf24; color: #1e293b; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; text-align: center; padding: 10px; box-shadow: inset 0 5px 10px rgba(255,255,255,0.6), 0 8px 15px rgba(0,0,0,0.3); word-break: break-word;">
                ...
            </div>
        </div>

        <!-- Résultat final si déjà tiré -->
        <div id="winner-box" style="display: none; background: #d1fae5; color: #065f46; padding: 20px; border-radius: 12px; border: 2px solid #34d399;">
            <h2 id="winner-title" style="margin: 0; font-size: 22px;">🏆 TADAM ! Le grand gagnant est :</h2>
            <p id="winner-name" style="font-size: 26px; font-weight: bold; margin: 10px 0 0 0;"></p>
        </div>
    </div>

    <script>
        const participants = {participants_js};
        const countDownDate = new Date("October 4, 2026 20:00:00").getTime();
        const etatAdmin = "{etat_actuel}";
        const gagnantAdmin = "{gagnant_actuel}";
        const isTestMode = {test_mode_actif};

        function showWinnerUI(winner, isTest = false) {{
            document.getElementById("countdown-box").style.display = "none";
            document.getElementById("countdown-text").style.display = "none";
            document.getElementById("loto-display").style.display = "none";
            document.getElementById("winner-box").style.display = "block";
            document.getElementById("winner-name").innerText = winner;
            if (isTest) {{
                document.getElementById("winner-title").innerText = "🧪 [TEST À BLANC] Le gagnant simulé est :";
            }}
        }}

        function lancerAnimationLoto(isTest = false) {{
            document.getElementById("countdown-box").style.display = "none";
            document.getElementById("countdown-text").style.display = "none";
            document.getElementById("loto-display").style.display = "block";
            if (isTest) {{
                document.getElementById("loto-title").innerText = "🧪 [TEST À BLANC] Boules en action...";
            }}

            if (participants.length === 0) {{
                document.getElementById("loto-display").innerHTML = "<h3>🚨 Aucun participant enregistré pour effectuer le tirage !</h3>";
                return;
            }}

            let counter = 0;
            const animInterval = setInterval(function() {{
                const randomIndex = Math.floor(Math.random() * participants.length);
                document.getElementById("ball").innerText = participants[randomIndex];
                counter++;
                
                if (counter > 20) {{
                    clearInterval(animInterval);
                    const finalWinner = participants[Math.floor(Math.random() * participants.length)];
                    showWinnerUI(finalWinner, isTest);
                }}
            }}, 200);
        }}

        // Si l'admin a déclenché un test à blanc
        if (isTestMode) {{
            lancerAnimationLoto(true);
        }} else if (etatAdmin === "Termine" && gagnantAdmin) {{
            showWinnerUI(gagnantAdmin, false);
        }} else {{
            const x = setInterval(function() {{
                const now = new Date().getTime();
                const distance = countDownDate - now;

                if (distance < 0 && etatAdmin !== "Termine") {{
                    clearInterval(x);
                    lancerAnimationLoto(false);
                }} else if (etatAdmin !== "Termine") {{
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
    components.html(loto_html, height=230)
    st.markdown("---")

    etat = data["etat_tirage"]
    if etat == "Termine" and data["gagnant"] and not data.get("test_mode", False):
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
        # Si on rafraîchit, on désactive le mode test pour remettre le vrai compte à rebours
        if data.get("test_mode", False):
            data["test_mode"] = False
            save_data(data)
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
        
        tab1, tab2, tab3 = st.tabs(["📝 Ajouter", "🎲 Tirage & Tests", "🗑️ Reset"])
        
        with tab1:
            st.markdown("##### Ajouter des participants")
            texte_noms = st.text_area("Collez les noms (un par ligne) :", height=120, placeholder="Nom 1\nNom 2...")
            if st.button("➕ Enregistrer"):
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
            st.markdown("##### 🧪 Test à blanc de l'animation")
            st.write("Testez l'animation des boules de loto et le TADAM en direct (sans modifier le vrai résultat).")
            if st.button("🧪 LANCER UN TEST À BLANC"):
                if data["participants_acceptes"]:
                    data["test_mode"] = True
                    save_data(data)
                    st.success("Test à blanc lancé ! Basculez sur l'onglet 'Spectateur / Participant' pour voir l'animation en direct.")
                    st.rerun()
                else:
                    st.warning("Ajoutez d'abord quelques participants pour faire tourner les boules !")

            st.markdown("---")
            st.markdown("##### Lancer le Vrai Tirage (Manuel)")
            if data["participants_acceptes"]:
                st.write(f"Participants validés : {len(data['participants_acceptes'])}")
                if st.button("🎲 LANCER LE VRAI TIRAGE MAINTENANT !"):
                    data["etat_tirage"] = "Termine"
                    data["test_mode"] = False
                    data["gagnant"] = random.choice(data["participants_acceptes"])
                    save_data(data)
                    st.balloons()
                    st.success("Tirage officiel effectué !")
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
                    "etat_tirage": "En attente",
                    "test_mode": False
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
        if data.get("test_mode", False):
            st.info("🧪 [MODE TEST] L'animation de test est en cours sur la vue participant.")
        elif etat == "En attente":
            st.warning("⏳ Le tirage va bientôt commencer...")
        elif etat == "Termine" and data["gagnant"]:
            st.success(f"🏆 Gagnant officiel : **{data['gagnant']}** !")
            
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
