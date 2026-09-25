import json
import os
import random
import time
import streamlit as st

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
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

st.title("🎉 Le Grand Tirage au Sort en Direct !")
st.write("Suivez le tirage en temps réel et découvrez si la chance vous sourit ! 🍀")

st.sidebar.header("⚙️ Configuration")
mode = st.sidebar.radio("Je suis :", ["Spectateur / Participant", "Administrateur"])

# ---------------------------------------------------------
# MODE 1 : SPECTATEUR / PARTICIPANT
# ---------------------------------------------------------
if mode == "Spectateur / Participant":
    st.info("💡 Cette page se met à jour pour vous montrer les listes et le grand gagnant en direct !")
    
    etat = data["etat_tirage"]
    if etat == "En attente":
        st.warning("⏳ Le tirage va bientôt commencer... Restez connectés !")
    elif etat == "En cours":
        st.info("🎰 Le suspense est à son comble... Le tirage est en cours !")
    elif etat == "Termine" and data["gagnant"]:
        st.success(f"🏆 Le grand gagnant est : **{data['gagnant']}** ! Félicitations ! 🥳")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Participants Validés")
        if data["participants_acceptes"]:
            for p in data["participants_acceptes"]:
                st.write(f"- 👤 {p}")
        else:
            st.write("Aucun participant validé pour le moment.")
            
    with col2:
        st.subheader("❌ Inscriptions Refusées")
        if data["participants_refuses"]:
            for r in data["participants_refuses"]:
                st.write(f"- 🛑 **{r['nom']}** (*Raison : {r['raison']}*)")
        else:
            st.write("Aucun refus.")
            
    if st.button("🔄 Rafraîchir la page"):
        st.rerun()

# ---------------------------------------------------------
# MODE 2 : ADMINISTRATEUR (TOUT-EN-UN)
# ---------------------------------------------------------
else:
    st.sidebar.success("🔒 Mode Administrateur activé")
    st.header("🛠️ Espace de Gestion (Tout-en-un)")
    
    tab1, tab2, tab3 = st.tabs(["👥 Ajouter des Noms", "🎁 Lancer le Tirage", "🔄 Réinitialiser"])
    
    with tab1:
        st.subheader("📝 Ajouter des participants en bloc")
        texte_noms = st.text_area("Collez votre liste de noms ici (un par ligne) :", height=150, placeholder="Christophe Brasseur\nMagali Lefebvre\n...")
        
        if st.button("➕ Enregistrer ces participants"):
            if texte_noms.strip():
                lignes = texte_noms.split("\n")
                ajoutes = 0
                for ligne in lignes:
                    nom = ligne.strip()
                    if nom and nom not in data["participants_acceptes"]:
                        data["participants_acceptes"].append(nom)
                        ajoutes += 1
                save_data(data)
                st.success(f"🎉 {ajoutes} participants ajoutés avec succès !")
                st.rerun()
                
        st.markdown("---")
        st.subheader("🛑 Enregistrer un refus")
        with st.form("form_refus"):
            c_ref1, c_ref2 = st.columns(2)
            n_ref = c_ref1.text_input("Nom de la personne")
            r_ref = c_ref2.text_input("Raison (ex: Organisateur)")
            if st.form_submit_button("Ajouter aux refusés") and n_ref:
                data["participants_refuses"].append({"nom": n_ref, "raison": r_ref})
                save_data(data)
                st.success("Refus enregistré !")
                st.rerun()
                
    with tab2:
        st.subheader("🎰 Animation du Tirage au Sort")
        if data["participants_acceptes"]:
            st.write(f"Nombre de participants en lice : {len(data['participants_acceptes'])}")
            
            if st.button("🎲 LANCER LE TIRAGE AU SORT EN DIRECT !"):
                data["etat_tirage"] = "En cours"
                save_data(data)
                
                with st.spinner("Suspense... Le sort est jeté... 🪄"):
                    placeholder = st.empty()
                    for _ in range(10):
                        temp_winner = random.choice(data["participants_acceptes"])
                        placeholder.markdown(f"### 🌀 En cours : *{temp_winner}* ...")
                        time.sleep(0.3)
                    
                    gagnant = random.choice(data["participants_acceptes"])
                    data["gagnant"] = gagnant
                    data["etat_tirage"] = "Termine"
                    save_data(data)
                
                st.balloons()
                st.success(f"🏆 Le gagnant désigné est : **{gagnant}** !")
                st.rerun()
        else:
            st.warning("Ajoutez des participants dans l'onglet 1 pour lancer le jeu.")
            
    with tab3:
        if st.button("🗑️ Réinitialiser complètement le tirage"):
            default_data = {
                "participants_acceptes": [],
                "participants_refuses": [],
                "gagnant": None,
                "etat_tirage": "En attente"
            }
            save_data(default_data)
            st.success("Remis à zéro !")
            st.rerun()

    # --- APERÇU EN DIRECT INTÉGRÉ POUR L'ADMIN ---
    st.markdown("---")
    st.header("👀 Aperçu en direct et suppression rapide")
    
    etat_actuel = data["etat_tirage"]
    if etat_actuel == "Termine" and data["gagnant"]:
        st.success(f"🏆 Gagnant affiché sur le live : **{data['gagnant']}**")
    else:
        st.info(f"État actuel du tirage : **{etat_actuel}**")
        
    col_prev1, col_prev2 = st.columns(2)
    
    with col_prev1:
        st.subheader(f"✅ Validés ({len(data['participants_acceptes'])})")
        if data["participants_acceptes"]:
            for i, p in enumerate(data["participants_acceptes"]):
                c_a, c_b = st.columns([4, 1])
                c_a.write(f"👤 {p}")
                if c_b.button("❌", key=f"del_acc_{i}"):
                    data["participants_acceptes"].pop(i)
                    save_data(data)
                    st.rerun()
        else:
            st.write("Aucun participant validé.")
            
    with col_prev2:
        st.subheader(f"❌ Refusés ({len(data['participants_refuses'])})")
        if data["participants_refuses"]:
            for i, r in enumerate(data["participants_refuses"]):
                c_a, c_b = st.columns([4, 1])
                c_a.write(f"🛑 {r['nom']} (*{r['raison']}*)")
                if c_b.button("❌", key=f"del_ref_{i}"):
                    data["participants_refuses"].pop(i)
                    save_data(data)
                    st.rerun()
        else:
            st.write("Aucun refus.")
            
