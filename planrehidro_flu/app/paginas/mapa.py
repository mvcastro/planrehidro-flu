import folium
from streamlit_folium import st_folium

from planrehidro_flu.app.data import df_criterios_rh

map = folium.Map(location=[-14.0, -48.0], zoom_start=5)

icon_estacao = folium.DivIcon(
    # icon_size=(150, 30),
    # icon_anchor=(75, 15), # Center the anchor for a 150x30 icon
    html="<div>🔻</div>"
)


for _, estacao in df_criterios_rh.iterrows():
    folium.Marker(
        location=[estacao["latitude"], estacao["longitude"]],
        icon=icon_estacao,
        popup=folium.Popup(estacao.to_frame().to_html()),
        tooltip=f"{estacao['nome']} ({estacao['codigo_estacao']})",
    ).add_to(map)


# call to render Folium map in Streamlit
st_data = st_folium(map, width=800, returned_objects=[])
