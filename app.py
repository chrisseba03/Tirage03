import json
import os
import random
import time
import pandas as pd
import streamlit as st

DATA_FILE = "tirage_data.json"


def load_data():
  if not os.path.exists(DATA_FILE):
    default_data = {
        "participants_acceptes": [],
        "participants_refuses": [],
        "gagnant": None,
        "etat_tirage": "En attente",
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
st.write(
    "Suivez le tirage en temps réel et découvrez si la chance vous sourit ! 🍀"
)

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

  etat = data["etat_tirage"]
  if etat == "En attente":
    st.warning("⏳ Le tirage va bientôt commencer... Restez connectés !")
  elif etat == "En cours":
    st.info("🎰 Le suspense est à son comble... Le tirage est en cours !")
  elif etat == "Termine" and data["gagnant"]:
    st.success(
        f"🏆 Le grand gagnant est : **{data['gagnant']}** ! Félicitations ! 🥳"
    )

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
# MODE 2 : ADMINISTRATEUR (VOUS)
# ---------------------------------------------------------
else:
  st.sidebar.success("🔒 Mode Administrateur activé")
  st.header("🛠️ Espace de Gestion du Tirage")

  tab1, tab2, tab3, tab4 = st.tabs([
      "📥 Importer & Vérifier les Noms",
      "👥 Gérer les Listes",
      "🎁 Lancer le Tirage",
      "🔄 Réinitialiser",
  ])

  # ONGLET 1 : IMPORTATION AVEC TABLEAU DE CONTRÔLE
  with tab1:
    st.subheader("📥 Extraction et Validation des Noms")
    st.write(
        "Collez les commentaires ci-dessous. L'application va repérer les"
        " auteurs et vous présenter un tableau de contrôle avant de valider."
    )

    texte_fb = st.text_area(
        "Collez les commentaires Facebook ici :",
        height=200,
        placeholder="Collez tout le texte brut ici...",
    )

    if "noms_detectes" not in st.session_state:
      st.session_state["noms_detectes"] = []

    if st.button("🔍 Analyser le texte"):
      if texte_fb.strip():
        lignes = texte_fb.split("\n")
        noms_trouves = []

        # Analyse intelligente des lignes courtes (souvent les noms sur Facebook)
        for ligne in lignes:
          ligne_propre = ligne.replace("👤", "").strip()
          # Un nom Facebook fait rarement plus de 4 mots et ne contient pas de longs pavés de texte
          if (
              ligne_propre
              and len(ligne_propre) < 35
              and " " in ligne_propre
              and not any(
                  m in ligne_propre.lower()
                  for m in [
                      "répondre",
                      "partager",
                      "modifié",
                      "commentaire",
                      "http",
                      "www",
                      "comment",
                  ]
              )
          ):
            # Éviter les doublons dans la détection
            if (
                ligne_propre not in noms_trouves
                and ligne_propre not in data["participants_acceptes"]
            ):
              noms_trouves.append(ligne_propre)

        st.session_state["noms_detectes"] = noms_trouves
        if noms_trouves:
          st.success(
              f"✨ {len(noms_trouves)} noms potentiels détectés ! Vérifiez-les"
              " ci-dessous :"
          )
        else:
          st.warning(
              "Aucun nom n'a pu être isolé automatiquement. Essayez de coller"
              " une liste plus propre."
          )
      else:
        st.warning("Veuillez coller du texte.")

    # Si des noms ont été trouvés, on affiche un tableau éditable (cases à cocher)
    if st.session_state["noms_detectes"]:
      st.write("### 📝 Cochez les participants à valider :")

      # Création d'un tableau interactif
      df_temp = pd.DataFrame({
          "Nom": st.session_state["noms_detectes"],
          "Valider": [True] * len(st.session_state["noms_detectes"]),
      })

      edited_df = st.data_editor(df_temp, hide_index=True, use_container_width=True)

      if st.button("🚀 Ajouter les participants cochés à la liste officielle"):
        # Récupérer uniquement ceux qui sont cochés à True
        a_ajouter = edited_df[edited_df["Valider"] == True]["Nom"].tolist()
        ajout_count = 0
        for nom in a_ajouter:
          if nom not in data["participants_acceptes"]:
            data["participants_acceptes"].append(nom)
            ajout_count += 1

        save_data(data)
        st.session_state["noms_detectes"] = []  # On vide la mémoire
        st.success(
            f"🎉 {ajout_count} participants ont été ajoutés avec succès !"
        )
        st.rerun()

  # ONGLET 2 : GESTION CLASSIQUE
  with tab2:
    st.subheader("👥 Gérer les participants et refus")
    col_a, col_b = st.columns(2)

    with col_a:
      st.write("### Validés")
      if data["participants_acceptes"]:
        for i, p in enumerate(data["participants_acceptes"]):
          c1, c2 = st.columns([4, 1])
          c1.write(f"👤 {p}")
          if c2.button("❌", key=f"del_acc_{i}"):
            data["participants_acceptes"].pop(i)
            save_data(data)
            st.rerun()
      else:
        st.write("Aucun participant.")

    with col_b:
      st.write("### Refusés")
      if data["participants_refuses"]:
        for i, r in enumerate(data["participants_refuses"]):
          c1, c2 = st.columns([4, 1])
          c1.write(f"🛑 {r['nom']} (*{r['raison']}*)")
          if c2.button("❌", key=f"del_ref_{i}"):
            data["participants_refuses"].pop(i)
            save_data(data)
            st.rerun()
      else:
        st.write("Aucun refus.")

      st.markdown("---")
      with st.form("add_refused_solo"):
        n_ref = st.text_input("Refuser un nom précis")
        r_ref = st.text_input("Raison du refus")
        if st.form_submit_button("Enregistrer le refus") and n_ref:
          data["participants_refuses"].append({"nom": n_ref, "raison": r_ref})
          save_data(data)
          st.rerun()

  # ONGLET 3 : LANCER LE TIRAGE
  with tab3:
    st.subheader("🎰 Animation du Tirage au Sort")
    if data["participants_acceptes"]:
      st.write(
          f"Nombre de participants éligibles :"
          f" {len(data['participants_acceptes'])}"
      )

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
        st.success(f"🎉 Le gagnant désigné est : **{gagnant}** !")
        st.rerun()
    else:
      st.warning(
          "Il n'y a aucun participant validé pour l'instant pour lancer le"
          " tirage."
      )

  # ONGLET 4 : RÉINITIALISATION
  with tab4:
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
