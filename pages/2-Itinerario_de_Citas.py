import streamlit as st
import json
import os
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(__file__))  # sube de pages/ a la raíz
ARCHIVO = os.path.join(RAIZ, "PerCitas.json")
ARCHIVO_ARCHIVO = os.path.join(RAIZ, "CitasArchivadas.json")

st.set_page_config(page_title="Itinerario de Citas")

st.title("📋 Itinerario de Citas")


def cargar_citas_activas():
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def cargar_citas_archivadas():
    try:
        with open(ARCHIVO_ARCHIVO, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        return {}


dia = st.date_input("📅 Seleccione un día", value=date.today())

tab_activas, tab_archivadas = st.tabs(["🟢 Citas activas", "🕒 Citas archivadas"])

with tab_activas:
    citas = cargar_citas_activas()
    citas_dia = [c for c in citas if c["fecha"] == str(dia)]

    if not citas_dia:
        st.info("No hay citas activas para este día")
    else:
        st.dataframe(citas_dia, use_container_width=True, hide_index=True)

with tab_archivadas:
    archivadas = cargar_citas_archivadas()
    dia_str = str(dia)

    if dia_str not in archivadas:
        st.warning("No hay citas archivadas para este día")
    else:
        st.dataframe(archivadas[dia_str], use_container_width=True, hide_index=True)


if st.checkbox("Haga click si desea ver todas las citas activas"):
    todas = cargar_citas_activas()
    st.dataframe(todas, use_container_width=True, hide_index=True)

# CORRECCIÓN: usar nombre distinto al de la función
if st.checkbox("Haga click si desea ver todas las citas archivadas"):
    todas_archivadas = cargar_citas_archivadas()
    # Aplanar el dict {fecha: [lista]} en una sola lista
    aplanadas = []
    for lista in todas_archivadas.values():
        aplanadas.extend(lista)
    if aplanadas:
        st.dataframe(aplanadas, use_container_width=True, hide_index=True)
    else:
        st.info("No hay citas archivadas")
