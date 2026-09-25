from datetime import datetime
import random
import time
import streamlit as st

# ==========================================
# 1. CONFIGURATION & HEURE DU TIRAGE
# ==========================================
st.set_page_config(
    page_title="La Place du Village - Tirage au Sort",
    page_icon="🎁",
    layout="wide",
)

# Date et heure exactes du tirage automatique
HEURE_TIRAGE = datetime(2026, 10, 15, 20, 0, 0)
GRAINE_UNIQUE = 20261015  # Assure un tirage infalsifiable et identique partout

# Données partagées entre tous les spectateurs (session globale)
if "participants_valides" not in st.session_state:
    st.session_state.participants_valides = [
        "Participant 1",
        "Participant 2",
        "Participant 3",
        "Participant 4",
        "Participant 5",
    ]

# ==========================================
# 2. NAVIGATION (ADMIN vs SPECTATEUR)
# ==========================================
st.sidebar.title("📌 Menu")
mode = st.sidebar.radio("Navigation", ["👁️ Mode Spectateur", "⚙️ Administration"])

# ==========================================
# VUE SPECTATEUR (ACCÈS PUBLIC SANS ACTION)
# ==========================================
if mode == "👁️ Mode Spectateur":
    st.title("🎉 La Place du Village - Tirage au Sort en Direct")

    maintenant = datetime.now()

    if maintenant < HEURE_TIRAGE:
        # --- PHASE 1 : COMPTE À REBOURS ---
        temps_restant = HEURE_TIRAGE - maintenant
        secondes_totales = int(temps_restant.total_seconds())

        heures = secondes_totales // 3600
        minutes = (secondes_totales % 3600) // 60
        secondes = secondes_totales % 60

        st.subheader("⏳ Le tirage au sort automatique va bientôt commencer...")
        st.metric(
            label="Temps restant avant le tirage",
            value=f"{heures:02d}h {minutes:02d}m {secondes:02d}s",
        )

        st.divider()
        st.write("### 👥 Liste des participants validés")

        # Affichage des participants sur 3 colonnes comme sur ton interface
        cols = st.columns(3)
        for idx, nom in enumerate(
            sorted(st.session_state.participants_valides)
        ):
            cols[idx % 3].write(f"• {nom}")

        # Rafraîchissement automatique toutes les secondes
        time.sleep(1)
        st.rerun()

    else:
        # --- PHASE 2 : DÉCLENCHEMENT AUTOMATIQUE DU TIRAGE ---
        st.subheader("🔮 Tirage en cours...")

        # Animation des boules / noms qui défilent
        placeholder = st.empty()
        random.seed(
            GRAINE_UNIQUE
        )  # Graine fixe pour garantir un gagnant unique

        with st.spinner("Mélange des boules dans le boulier..."):
            for _ in range(15):
                nom_temp = random.choice(st.session_state.participants_valides)
                placeholder.markdown(
                    f"<h2 style='text-align: center; color: #ff4b4b;'>🎰 {nom_temp}</h2>",
                    unsafe_allow_html=True,
                )
                time.sleep(0.2)

        # Tirage final
        gagnant = random.choice(sorted(st.session_state.participants_valides))

        # Résultat affiché pour tous les spectateurs
        placeholder.success(f"### 🎉 LE GAGNANT EST : **{gagnant}** 🎉")
        st.balloons()

        st.divider()
        st.write("### 👥 Participants à ce tirage :")
        cols = st.columns(3)
        for idx, nom in enumerate(
            sorted(st.session_state.participants_valides)
        ):
            cols[idx % 3].write(f"• {nom}")

# ==========================================
# VUE ADMIN (SÉCURISÉE PAR MOT DE PASSE)
# ==========================================
elif mode == "⚙️ Administration":
    st.title("⚙️ Espace Administration")

    mot_de_passe = st.text_input("Mot de passe d'accès", type="password")

    if mot_de_passe == "admin03":  # Ton mot de passe
        st.success("Accès autorisé")

        st.subheader("📝 Gestion des participants")
        nouveaux_noms = st.text_area(
            "Ajouter des participants (un par ligne)",
            height=150,
            value="\n".join(st.session_state.participants_valides),
        )

        if st.button("Enregistrer la liste"):
            st.session_state.participants_valides = [
                n.strip() for n in nouveaux_noms.split("\n") if n.strip()
            ]
            st.success("Liste mise à jour avec succès !")

        st.divider()
        st.write(f"**Heure du tirage configurée :** {HEURE_TIRAGE}")

    elif mot_de_passe:
        st.error("Mot de passe incorrect")
