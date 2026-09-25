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
        "etat_tirage": "En attente",
    }
    save_data(default_data)
    return default_data

  with open(DATA_FILE, "r", encoding="utf-8") as f:
    return json.load(f)


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8f") as f:
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
      "📥 Trier les Commentaires FB",
      "👥 Gérer les Listes",
      "🎁 Lancer le Tirage",
      "🔄 Réinitialiser",
  ])

  # ONGLET 1 : ANALYSE ET TRI INTELLIGENT DES COMMENTAIRES FACEBOOK
  with tab1:
    st.subheader("📥 Analyse automatique des commentaires Facebook")
    st.write(
        "Copiez-collez tout le fil de discussion de votre publication Facebook"
        " ci-dessous. L'application va extraire les noms et trier les"
        " participants toute seule !"
    )

    texte_fb = st.text_area(
        "Collez les commentaires Facebook ici :",
        height=250,
        placeholder="Collez tout le texte brut copié depuis Facebook...",
    )

    if st.button("🤖 Lancer le tri automatique"):
      if texte_fb.strip():
        lignes = texte_fb.split("\n")
        commentaires_bruts = []
        buffer_nom = None

        # Étape 1 : Nettoyage et regroupement par auteur typique de Facebook
        # Sur Facebook, le nom est souvent seul sur une ligne, suivi de "·" ou de texte.
        i = 0
        while i < len(lignes):
          ligne = lignes[i].strip()
          # Ignorer les lignes de bruit typiques de l'interface FB
          mots_a_ignorer = [
              "Répondre",
              "Partager",
              "Voir la traduction",
              "Modifié",
              "·",
              "",
          ]
          if ligne in mots_a_ignorer or "COMMENT JOUER" in ligne:
            i += 1
            continue

          # Détection d'un nom probable (ligne courte sans caractères bizarres, ou suivie de '·')
          if (
              i + 1 < len(lignes)
              and ("·" in lignes[i + 1] or lignes[i + 1].strip() == "")
              and len(ligne) < 40
          ):
            nom_auteur = ligne
            # Récupérer le contenu du commentaire un peu plus bas
            contenu = ""
            i += 2
            while i < len(lignes):
              sub_lign = lignes[i].strip()
              if sub_lign in ["Répondre", "Partager", "Voir la traduction"]:
                break
              if (
                  sub_lign
                  and len(sub_lign) < 40
                  and i + 1 < len(lignes)
                  and lignes[i + 1].strip() == "·"
              ):
                break  # On tombe sur le nom suivant
              contenu += " " + sub_lign
              i += 1

            if nom_auteur:
              commentaires_bruts.append(
                  {"nom": nom_auteur, "texte": contenu.lower()}
              )
          else:
            i += 1

        # Étape 2 : Validation ou Refus automatique selon les critères du jeu
        ajoutes = 0
        refuses = 0

        # Liste des administrateurs à exclure du tirage
        exclus = ["seb capturis", "sébastien", "chriss tallerie"]

        for c in commentaires_bruts:
          nom = c["nom"]
          texte = c["texte"]

          # Vérifier si c'est l'admin
          if any(ex in nom.lower() for ex in exclus):
            continue  # On ignore l'admin

          # Critère 1 : La personne participe-t-elle ou donne-t-elle une réponse valide ?
          # On cherche des indices de participation ou un parfum
          mots_cles_parfums = [
              "caramel",
              "beurre salé",
              "yuzu",
              "café",
              "chocolat",
              "cacahuète",
              "expresso",
              "gourmand",
          ]
          mots_participation = ["participe", "invite", "préféré", "préfère"]

          a_participe = any(m in texte for m in mots_participation) or any(
              p in texte for p in mots_cles_parfums
          )

          # S'assurer qu'elle n'est pas déjà dans les listes
          if nom not in data["participants_acceptes"] and not any(
              r["nom"] == nom for r in data["participants_refuses"]
          ):
            if a_participe:
              data["participants_acceptes"].append(nom)
              ajoutes += 1
            else:
              # Si le commentaire est juste une discussion sans participation claire
              pass

        save_data(data)
        st.success(
            f"✨ Analyse terminée ! **{ajoutes} nouveaux participants** ont été"
            " validés automatiquement."
        )
        st.rerun()
      else:
        st.warning("Veuillez coller les commentaires Facebook avant de trier.")

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
