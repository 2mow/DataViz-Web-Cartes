import streamlit as st
import pandas as pd
import folium
from folium.plugins import FastMarkerCluster
from streamlit_folium import st_folium
import json
import matplotlib.pyplot as plt
import seaborn as sns

# Titre principal de l'application
st.title("Application AirBnB - Paris")

# Chargement des fichiers nécessaires
data_file = "listings.csv"  # Fichier des logements
geojson_file = "neighbourhoods.geojson"  # Contours des arrondissements

# Lecture des données de base
df = pd.read_csv(data_file)
with open(geojson_file, "r") as f:
    geojson_data = json.load(f)

# Onglets de navigation
onglet1, onglet2, onglet3 = st.tabs(["Onglet1", "Onglet2", "Onglet3"])

################################## Onglet 1 : Statistiques générales ##################################
with onglet1:
    st.header("Statistiques générales")

    # Création de deux colonnes pour les graphiques côte à côte
    col1, col2 = st.columns(2)

    # Graphique sur les types de logements
    with col1:
        st.subheader("Répartition des types de logements")
        room_type_counts = df["room_type"].value_counts()
        
        # Graphique amélioré avec palette de couleurs
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        room_type_counts.plot(kind="bar", color=sns.color_palette("Set2", len(room_type_counts)), ax=ax1)
        ax1.set_title("Nombre de logements par type", fontsize=16, fontweight='bold')
        ax1.set_ylabel("Nombre de logements", fontsize=14)
        ax1.set_xlabel("Type de logement", fontsize=14)
        ax1.tick_params(axis="x", rotation=45)  # Rotation des labels sur l'axe des X
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig1)

    # Graphique sur les prix
    with col2:
        st.subheader("Distribution des prix")
        
        # Graphique amélioré avec palette de couleurs
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        df["price"].plot(kind="hist", bins=50, color=sns.color_palette("Blues", 1)[0], ax=ax2)
        ax2.set_title("Distribution des prix", fontsize=16, fontweight='bold')
        ax2.set_xlabel("Prix (€)", fontsize=14)
        ax2.set_ylabel("Fréquence", fontsize=14)
        ax2.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig2)


    # Carte avec tous les logements
    st.subheader("Carte globale des logements à Paris")
    centre = [48.8566, 2.3522]  # Coordonnées de Paris
    m = folium.Map(location=centre, zoom_start=12, tiles="cartodbpositron")

    # Limiter à un échantillon de logements (par exemple, 1000 logements)
    sample_df = df.sample(n=1000, random_state=42)  # Échantillon de 1000 logements

    # Création d'une liste de coordonnées pour les logements échantillonnés
    locations = sample_df[["latitude", "longitude"]].values.tolist()

    # Utilisation de FastMarkerCluster pour améliorer les performances
    FastMarkerCluster(locations).add_to(m)

    st_folium(m)

################################## Onglet 2 : Carte choroplèthe ##################################
with onglet2:
    st.header("Carte choroplèthe interactive")

    # Choix de la statistique à afficher
    stat_option = st.selectbox(
        "Choisissez la statistique à afficher :",
        ["Nombre de logements", "Prix moyen", "Part de logement entier"]
    )

    # Calcul des statistiques nécessaires
    df["is_entire_home"] = df["room_type"] == "Entire home/apt"

    stats = df.groupby("neighbourhood").agg(
        nb_logements=("id", "count"),
        prix_moyen=("price", "mean"),
        part_logement_entier=("is_entire_home", "mean")
    ).reset_index()

    stats["part_logement_entier"] *= 100  # Conversion en pourcentage

    # Carte de base
    m = folium.Map(location=centre, zoom_start=12, tiles="cartodbpositron")

    # Ajout de la couche choroplèthe selon la statistique
    if stat_option == "Nombre de logements":
        data_col = "nb_logements"
        legend_name = "Nombre de logements"
    elif stat_option == "Prix moyen":
        data_col = "prix_moyen"
        legend_name = "Prix moyen (€)"
    else:
        data_col = "part_logement_entier"
        legend_name = "Part de logements entiers (%)"

    folium.Choropleth(
        geo_data=geojson_data,
        name="choropleth",
        data=stats,
        columns=["neighbourhood", data_col],
        key_on="feature.properties.neighbourhood",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=legend_name
    ).add_to(m)

    st_folium(m)

################################## Onglet 3 : Small multiples ##################################
with onglet3:
    st.header("Répartition des types de logements par arrondissement")

    # Préparation des données pour les graphiques
    arrondissement_stats = df.groupby(["neighbourhood", "room_type"]).size().unstack(fill_value=0)

    # Création des small multiples
    fig, axes = plt.subplots(nrows=5, ncols=4, figsize=(20, 15), sharey=True)
    axes = axes.flatten()

    for i, (arrondissement, data) in enumerate(arrondissement_stats.iterrows()):
        ax = axes[i]
        data.plot(kind="bar", ax=ax, color=sns.color_palette("Set3", len(data.index)))
        ax.set_title(arrondissement)
        ax.set_xticklabels(data.index, rotation=45, ha="right")
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Suppression des axes inutilisés
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    st.pyplot(fig)

    st.caption("Chaque graphique représente la répartition des types de logements pour un arrondissement spécifique.")
