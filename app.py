import pandas
import json
import folium
from streamlit_folium import st_folium

centre = [40.7,-73.95]
m = folium.Map(location = centre, zoom_start = 10, tiles = "cartodbpositron")

geojson_data = json.load(open("new-york-city-boroughs.geojson"))
df = pandas.read_csv("restaurants_ok.csv")

resume = df.filter(["borough", "restaurant_id"]).groupby("borough").count().reset_index()
resume.columns = ["name", "nb_restaurants"]

choro = folium.Choropleth(
    geo_data = geojson_data,
    name = "choropleth",
    data = resume,
    columns = ["name", "nb_restaurants"],
    key_on = "feature.properties.name",
    fill_color = "YlGn",
    fill_opacity = 0.7,
    line_opacity = 0.2,
    legend_name = "Nombre de restaurants par quartier"
).add_to(m)

for row in choro.geojson.data['features']:
    q = row['properties']['name']
    nb = resume.query("name == @q")["nb_restaurants"].iloc[0]
    row['properties']['nb'] = int(nb)

folium.GeoJsonTooltip(['name','nb'], aliases = ['Quartier : ','Nombre de restaurants : ']).add_to(choro.geojson)

st_folium(m)