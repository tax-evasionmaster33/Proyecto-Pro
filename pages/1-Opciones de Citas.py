import streamlit as st
import re # Esto es para hallar patrones en un input
from datetime import date, timedelta, time, datetime
from Restricciones import *
from Gestor import *

st.set_page_config(page_title="MP", page_icon="Fixed 1.png")
st.logo("Fixed 1.png", size="large")
#ESTE FRAGMENTO DE CODIGO SE encarga de Cargar esas funciones siempre q se ejecute la aplicacion
gestor = GestorCitas()
gestor.archivar_citas_pasadas()


st.title("🗂 Gestión de Citas")

col1, col2, col3 = st.columns(3)
if col1.button("Agendar"):
    st.session_state.page = "Agendar"
if col2.button("Eliminar"):
    st.session_state.page = "Eliminar"
if col3.button("Modificar"):
    st.session_state.page = "Modificar"

if "page" not in st.session_state:
    st.session_state.page = None

#Esto es lo de las fechas para el menu mas adelante
def fechas_laborables(dias=30):
    hoy = date.today()
    return [hoy + timedelta(days=i) for i in range(dias) if (hoy + timedelta(days=i)).weekday() < 5]

# TOdo ese es el menu Agenfar y validaciONEs
if st.session_state.page == "Agendar":
    st.subheader("📅 Agendar Cita")

    Pais = st.selectbox("País", list(PERSONAL_AUTORIZADO.keys()))

    if Pais:
        fechas_validas = fechas_laborables(30)

        with st.form("form_agendar"):
            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            telefono = st.text_input("Teléfono (+53 ########)")

            tipo_tramite = st.selectbox("Tipo de trámite", list(DURACION_MIN[Pais].keys()))
            trabajadora = st.selectbox("Tramitadora", PERSONAL_AUTORIZADO[Pais])
            recursos = st.multiselect("Recursos requeridos(Seleccione al menos uno!)",CO_REQUISITOS[Pais])

            Fecha = st.selectbox("Fecha (solo días laborables)", fechas_validas)

            # Horarios permitidos
            horas_manana = [time(h, m) for h in range(9, 12) for m in [0, 15, 30, 45]]
            horas_tarde = [time(h, m) for h in range(13, 17) for m in [0, 15, 30, 45]] + [time(17, 30)]
            horario_disponible = horas_manana + horas_tarde

            Hora = st.selectbox("Horario", horario_disponible)

            Guardar = st.form_submit_button("Guardar Cita")

        if Guardar:
            errores = []
            if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,}", nombre):
                errores.append("❌ Nombre inválido")
            if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,}", apellido):
                errores.append("❌ Apellido inválido")
            if not re.fullmatch(r"\+53 \d{8}", telefono):
                errores.append("❌ Teléfono inválido")
            if not recursos:
                errores.append("❌ Seleccione al menos un recurso")

            if errores:
                for e in errores:
                    st.error(e)
            else:
                # Crear diccionario de la cita
                cita_dict = {
                    "Tipo_Tramite":tipo_tramite,
                    "Nombre":nombre,
                    "Apellido":apellido,
                    "pais": Pais,
                    "fecha": str(Fecha),
                    "hora": Hora.strftime("%H:%M"),
                    "duracion": DURACION_MIN[Pais][tipo_tramite],
                    "trabajadora": trabajadora,
                    "recursos_usados": recursos,
                    "Telefono":telefono
                }

                # Carga las citas existentes
                citas = gestor.cargar()

                # Revisa si hay algun conflicto
                if gestor.hay_conflicto(cita_dict, citas):
                    nueva_hora = gestor.buscar_hueco(cita_dict, citas)
                    if nueva_hora:
                        st.warning(f"⚠️ Conflicto detectado. Hueco más cercano disponible: {nueva_hora}")
                        if st.button("Aceptar nuevo horario"):
                            cita_dict["hora"] = nueva_hora
                            citas.append(cita_dict)
                            gestor.guardar(citas)
                            st.success("✅ Cita guardada en nuevo horario")
                    else:
                        st.error("❌ No hay huecos disponibles hoy")
                else:
                    citas.append(cita_dict)
                    gestor.guardar(citas)
                    st.success("✅ Cita guardada correctamente")

# ESta es la parte q se encarga de el bton Eliminar  eso
elif st.session_state.page == "Eliminar":
    st.subheader("🗑 Eliminar Cita")
    citas = gestor.cargar()

    if not citas:
        st.info("No hay citas guardadas")
    else:
        opciones = [
            f"{c['pais']} | {c['fecha']} | {c['hora']} | {c['trabajadora']}"
            for c in citas
        ]
        seleccion = st.selectbox("Seleccione la cita a eliminar", opciones)
        if st.button("Eliminar cita"):
            idx = opciones.index(seleccion)
            citas.pop(idx)
            gestor.guardar(citas)
            st.success("✅ Cita eliminada correctamente")
            st.rerun()

# Esta es la parte q se encarga de lo del boton de Modificar y eso
elif st.session_state.page == "Modificar":
    st.subheader("✏️ Modificar Cita")
    citas = gestor.cargar()

    if not citas:
        st.info("No hay citas guardadas")
    else:
        opciones = [
            f"{c['pais']} | {c['fecha']} | {c['hora']} | {c['trabajadora']}"
            for c in citas
        ]
        seleccion = st.selectbox("Seleccione la cita a modificar", opciones)
        idx = opciones.index(seleccion)
        cita = citas[idx]

        fechas_validas = fechas_laborables(30)

        with st.form("form_modificar"):
#Esto se encarga de cambiar la fecha de una cita ya creada
            nueva_fecha = st.selectbox("Nueva fecha", fechas_validas, index=fechas_validas.index(date.fromisoformat(cita["fecha"])))
            #Este es el horario permitido entre las nueve am a las 12 y despues de 1 pm hasta las 5:30
            horas_manana = [time(h, m) for h in range(9, 12) for m in [0, 15, 30, 45]]
            horas_tarde = [time(h, m) for h in range(13, 17) for m in [0, 15, 30, 45]] + [time(17, 30)]
            horario_disponible = horas_manana + horas_tarde

#Esto se encarga de cambiar la hora de una cita seleccionado 
            nueva_hora = st.selectbox("Nuevo horario", horario_disponible, index=horario_disponible.index(time(int(cita["hora"].split(":")[0]), int(cita["hora"].split(":")[1]))))
            
            GuardarCambios = st.form_submit_button("Guardar cambios")

        if GuardarCambios:
            cita_modificada = cita.copy()
            cita_modificada["fecha"] = str(nueva_fecha)
            cita_modificada["hora"] = nueva_hora.strftime("%H:%M")
            # Revisar conflicto
            otras_citas = citas[:idx] + citas[idx+1:]
            if gestor.hay_conflicto(cita_modificada, otras_citas):
                nueva_hora_disponible = gestor.buscar_hueco(cita_modificada, otras_citas)
                if nueva_hora_disponible:
                    st.warning(f"⚠️ Conflicto detectado. Hueco más cercano disponible: {nueva_hora_disponible}")
                    if st.button("Aceptar nuevo horario"):
                        cita_modificada["hora"] = nueva_hora_disponible
                        citas[idx] = cita_modificada
                        gestor.guardar(citas)
                        st.success("✅ Cita modificada correctamente")
                        st.rerun()
                else:
                    st.error("❌ No hay huecos disponibles hoy")
            else:
                citas[idx] = cita_modificada
                gestor.guardar(citas)
                st.success("✅ Cita modificada correctamente")
                st.rerun()

