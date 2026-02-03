import streamlit as st
from datetime import datetime,timedelta,time

#ESTO ES EL MENU PRINCIPAL O MAS BIEN DONDE SE MUESTRA LA INFO DE LA OFICINA Y ESO





st.header("Oficina de Tramites Proenza")
st.subheader("Gestor de Eventos")
st.set_page_config(
page_title="Home",
page_icon="Fixed 1.png",
layout="wide",
)
logo = st.logo("Fixed 1.png",size="large")

main_container = st.container(border=True,horizontal_alignment="left")

contenido = """
### 📋 TRÁMITES MIGRATORIOS  
#### *asesoría y llenado de documentos*  

📍 **Dirección**  
- [ ] Calle L No. 53 apto A entre Calzada y 11, Vedado  
  La Habana, Cuba  

📞 **Teléfono**  
- [ ] (+53) 7836 64 85  

📷 **Instagram**
- [ ]  https://www.instagram.com/oficina_tramites_proenza?igsh=dXE4aThoYTkybWdj


📧 **Email**  
- [ ] proenza2022@gmail.com
"""
info = """
## Detalles de los Recursos:
    Fuerza de Trabajo:      Pais del Tramite:                 
    - Yuli                  (España)                            
    - Zahili                (España)                   
    - Yanara                (EEUU)                     
    - Dania                 (Turkia,Brazil)                           
    - Betsy                 (Canada)                          
    Recursos Materiales:
    - Planilla
    - Impresora
    - Escaner
    - Laptop

"""
with main_container:
    colx,coly =st.columns([0.3,0.7],border=False)
    with colx:
        st.image("1.jpg","",width="stretch")
    with coly:
        st.markdown(contenido)


x = st.checkbox("Presione para obtener mas info sobre los recursos!")
if x:
    st.markdown(info)