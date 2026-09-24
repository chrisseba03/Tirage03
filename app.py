import json
import os
import random
import time
import streamlit as st

# Fichier pour stocker les données en temps réel pour tout le monde
DATA_FILE = "tirage_data.json"


def load_data():
  if not os.path.exists(DATA_FILE):
    # Données par défaut si le fichier n'existe pas encore
    default_data = {
        "participants_acceptes": ["Jean Dupont", "Marie Curie", "Lucie Martin"],
        "participants_refuses": [
            {"nom": "Marc Tremblay", "raison": "Inscription en double"},
            {"nom": "Sophie Durand", "raison": "Hors délai"},
        ],
        "gagnant": None,
        "etat_tirage": "En attente",  # 'En attente', 'En cours', 'Termine'
    }
    save_data(default_data)
    return default_data

  with open(DATA_FILE, "r", encoding="utf-8") as f:
    return json.load(f)


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# Chargement des données actuelles
data = load_data()

# --- INTERFACE UTILISATEUR ---
st.title("🎉 Le Grand Tirage au Sort en Direct !")
st.write("Suivez le tirage en temps réel et découvrez si la chance vous sourit ! 🍀")

# Barre latérale pour choisir le mode (Admin ou Public)
st.sidebar.header("⚙️ Configuration")
mode = st.sidebar.radio("Je suis :", ["Spectateur / Participant", "Administrateur"])

# ---------------------------------------------------------
# MODE 1 : SPECTATEUR / PARTICIPANT
# ---------------------------------------------------------
if mode == "Spectateur / Participant":
  st.info(
    "💡 Cette page se met à jour pour vous montrer les listes et le grand"
    " gagnant en direct !"
  )

  # Affichage de l'état du tirage
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

  # Petit bouton pour actualiser manuellement si besoin
  if st.button("🔄 Rafraîchir la page"):
    st.rerun()

# ---------------------------------------------------------
# MODE 2 : ADMINISTRATEUR (VOUS)
# ---------------------------------------------------------
else:
  st.sidebar.success("🔒 Mode Administrateur activé")
  st.header("🛠️ Espace de Gestion du Tirage")

  tab1, tab2, tab3 = st.tabs(
      ["👥 Gérer les Inscrits", "🎁 Lancer le Tirage", "🔄 Réinitialiser"]
  )

  with tab1:
    st.subheader("Ajouter ou modifier des participants")

    # Formulaire pour ajouter un accepté
    with st.form("add_accepted"):
      new_acc = st.text_input("Ajouter un participant validé")
      submit_acc = st.form_submit_button("Valider et Ajouter")
      if submit_acc and new_acc:
        data["participants_acceptes"].append(new_acc)
        save_data(data)
        st.success(f"Ajouté : {new_acc}")
        st.rerun()

    # Formulaire pour ajouter un refusé
    with st.form("add_refused"):
      new_ref = st.text_input("Nom de la personne refusée")
      reason_ref = st.text_input("Raison du refus (ex: Incomplet, Doublon...)")
      submit_ref = st.form_submit_button("Enregistrer le refus")
      if submit_ref and new_ref:
        data["participants_refuses"].append(
            {"nom": new_ref, "raison": reason_ref}
        )
        save_data(data)
        st.success(f"Refus enregistré pour {new_ref}")
        st.rerun()

  with tab2:
    st.subheader("🎰 Animation du Tirage au Sort")
    if data["participants_acceptes"]:
      st.write(
          f"Nombre de participants éligibles :"
          f" {len(data['participants_acceptes'])}"
      )

      if st.button("🎲 LANCER LE TIRAGE AU SORT EN DIRECT !"):
        data["etat_tirage"] = "En cours"
        save_data(data)

        # Petite animation de suspense
        with st.spinner("Suspense... Le sort is being cast... 🪄"):
          placeholder = st.empty()
          for _ in range(10):
            temp_winner = random.choice(data["participants_acceptes"])
            placeholder.markdown(f"### 🌀 En cours : *{temp_winner}* ...")
            time.sleep(0.3)

          # Choix final du gagnant
          gagnant = random.choice(data["participants_acceptes"])
          data["gagnant"] = gagnant
          data["etat_tirage"] = "Termine"
          save_data(data)

        st.balloons()
        st.success(f"🎉 Le gagnant désigné est : **{gagnant}** !")
        st.rerun()
    else:
      st.warning(
          "Il n'y a aucun participant validé pour l'instant pour lancer le"
          " tirage."
      )

  with tab3:
    if st.button("🗑️ Réinitialiser complètement le tirage"):
      default_data = {
          "participants_acceptes": [],
          "participants_refuses": [],
          "gagnant": None,
          "etat_tirage": "En attente",
      }
      save_data(default_data)
      st.success("Remis à zéro !")
      st.rerun()
