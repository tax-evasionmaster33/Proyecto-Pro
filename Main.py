import streamlit as st

# CORRECCIÓN: set_page_config debe ser la primera llamada de Streamlit
st.set_page_config(
    page_title="Home",
    page_icon="Fixed 1.png",
    layout="wide",
)

st.logo("Fixed 1.png", size="large")

st.header("Oficina de Tramites Proenza")
st.subheader("Gestor de Eventos")

main_container = st.container(border=True, horizontal_alignment="left")

contenido = """
### 📋 TRÁMITES MIGRATORIOS  
#### *asesoría y llenado de documentos*  

📍 **Dirección**  
Calle L No. 53 apto A entre Calzada y 11, Vedado, La Habana, Cuba

📞 **Teléfono**  
(+53) 7836 64 85

📷 **Instagram**  
https://www.instagram.com/oficina_tramites_proenza

📧 **Email**  
proenza2022@gmail.com
"""

info = """
## Detalles de los Recursos

**Fuerza de Trabajo:**
- Yuli — España
- Zahili — España
- Yanara — EEUU
- Dania — Turkia, Brasil
- Betsy — Canadá

**Recursos Materiales:**
- Planilla
- Impresora
- Escaner
- Laptop
"""

with main_container:
    colx, coly = st.columns([0.3, 0.7], border=False)
    with colx:
        st.image("1.jpg", "", width="stretch")
    with coly:
        st.markdown(contenido)

if st.checkbox("Presione para obtener más info sobre los recursos"):
    st.markdown(info)
