import folium
from folium.map import Icon
from streamlit_folium import st_folium

from planrehidro_flu.app.data import inventario_estacoes

map = folium.Map(location=[-14.0, -48.0], zoom_start=5)

icon_estacao = folium.DivIcon(
    icon_size=(150, 30),
    icon_anchor=(75, 15), # Center the anchor for a 150x30 icon
    html="<div>🔻</div>"
)


for estacao in inventario_estacoes:
    folium.Marker(
        location=[estacao.latitude, estacao.longitude],
        icon=icon_estacao,
        popup=f"{estacao.nome} ({estacao.codigo})",
        tooltip=f"{estacao.nome} ({estacao.codigo})",
    ).add_to(map)


# call to render Folium map in Streamlit
st_data = st_folium(map, width=725)
