import streamlit as st
import re
from datetime import date, timedelta, time, datetime
from Restricciones import PERSONAL_AUTORIZADO, CO_REQUISITOS, DURACION_MIN
from Gestor import GestorCitas, GestorInventario

st.set_page_config(page_title="Opciones de Citas", page_icon="Fixed 1.png", layout="wide")
st.logo("Fixed 1.png", size="large")

gestor = GestorCitas()
inventario = GestorInventario()
gestor.archivar_citas_pasadas()
inventario.verificar_recarga()

st.title("🗂 Gestión de Citas")
st.caption(f"📄 Planillas disponibles: **{inventario.stock_actual()}**")

if "page" not in st.session_state:
    st.session_state.page = None

col1, col2, col3 = st.columns(3)
if col1.button("Agendar"):
    st.session_state.page = "Agendar"
    st.session_state.pop("cita_pendiente", None)
    st.session_state.pop("nueva_hora_sugerida", None)
if col2.button("Eliminar"):
    st.session_state.page = "Eliminar"
if col3.button("Modificar"):
    st.session_state.page = "Modificar"
    st.session_state.pop("mod_pendiente", None)
    st.session_state.pop("mod_hora_sugerida", None)


def fechas_laborables(dias=30):
    hoy = date.today()
    return [hoy + timedelta(days=i) for i in range(dias) if (hoy + timedelta(days=i)).weekday() < 5]


# ──────────────────────────────────────────────
# AGENDAR
# ──────────────────────────────────────────────
if st.session_state.page == "Agendar":
    st.subheader("📅 Agendar Cita")

    Pais = st.selectbox("País", list(PERSONAL_AUTORIZADO.keys()))
    fechas_validas = fechas_laborables(30)

    # Fuera del form para que reaccionen al cambio
    trabajadora = st.selectbox("Tramitadora", PERSONAL_AUTORIZADO[Pais])
    todos_recursos = CO_REQUISITOS[Pais]
    recursos_filtrados = [
        r for r in todos_recursos
        if not r.startswith("Laptop ") or r == f"Laptop {trabajadora}"
    ]
    recursos = st.multiselect("Recursos requeridos (seleccione al menos uno)", recursos_filtrados)

    with st.form("form_agendar"):
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        telefono = st.text_input("Teléfono (+53 ########)")

        tipo_tramite = st.selectbox("Tipo de trámite", list(DURACION_MIN[Pais].keys()))

        Fecha = st.selectbox("Fecha (solo días laborables)", fechas_validas)

        horas_manana = [time(h, m) for h in range(9, 12) for m in [0, 15, 30, 45]]
        horas_tarde  = [time(h, m) for h in range(13, 17) for m in [0, 15, 30, 45]] + [time(17, 30)]
        horario_disponible = horas_manana + horas_tarde

        if Fecha == date.today():
            ahora = datetime.now().time()
            horario_disponible = [h for h in horario_disponible if h > ahora]

        if horario_disponible:
            Hora = st.selectbox("Horario", horario_disponible)
        else:
            st.warning("⚠️ No hay horarios disponibles para hoy. Seleccione otro día.")
            Hora = None

        Guardar = st.form_submit_button("Guardar Cita")

    # Botón de aceptar hueco — siempre visible si hay conflicto pendiente
    if "cita_pendiente" in st.session_state:
        st.info(f"⚠️ Hueco sugerido: {st.session_state['nueva_hora_sugerida']}")
        col_a, col_b = st.columns([1, 4])
        if col_a.button("✅ Aceptar nuevo horario", key="btn_aceptar_agendar"):
            c = st.session_state.pop("cita_pendiente")
            c["hora"] = st.session_state.pop("nueva_hora_sugerida")
            citas = gestor.cargar()
            citas.append(c)
            gestor.guardar(citas)
            if "Planilla" in c.get("recursos_usados", []):
                inventario.descontar(c["pais"], c["Tipo_Tramite"])
            st.success(f"✅ Cita guardada en nuevo horario. Planillas restantes: {inventario.stock_actual()}")
            st.rerun()
        if col_b.button("❌ Cancelar", key="btn_cancelar_agendar"):
            st.session_state.pop("cita_pendiente", None)
            st.session_state.pop("nueva_hora_sugerida", None)
            st.rerun()

    if Guardar and Hora is None:
        st.error("❌ No hay horarios disponibles. Selecciona otro día.")

    if Guardar and Hora is not None:
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
            # Chequear planillas si el trámite las usa
            hay_suficientes, consumo = inventario.hay_planillas(Pais, tipo_tramite)
            if "Planilla" in recursos and not hay_suficientes:
                st.error(f"❌ No hay planillas suficientes. Se necesitan {consumo} y quedan {inventario.stock_actual()}.")
            else:
                cita_dict = {
                    "Tipo_Tramite": tipo_tramite,
                    "Nombre": nombre,
                    "Apellido": apellido,
                    "pais": Pais,
                    "fecha": str(Fecha),
                    "hora": Hora.strftime("%H:%M"),
                    "duracion": DURACION_MIN[Pais][tipo_tramite],
                    "trabajadora": trabajadora,
                    "recursos_usados": recursos,
                    "Telefono": telefono,
                }

                citas = gestor.cargar()

                if gestor.hay_conflicto(cita_dict, citas):
                    nueva_hora = gestor.buscar_hueco(cita_dict, citas)
                    if nueva_hora:
                        st.session_state["cita_pendiente"] = cita_dict
                        st.session_state["nueva_hora_sugerida"] = nueva_hora
                        st.warning(f"⚠️ Conflicto detectado. Hueco disponible: {nueva_hora}")
                        st.rerun()
                    else:
                        st.error("❌ No hay huecos disponibles ese día")
                else:
                    citas.append(cita_dict)
                    gestor.guardar(citas)
                    if "Planilla" in recursos:
                        inventario.descontar(Pais, tipo_tramite)
                    st.success(f"✅ Cita guardada. Planillas restantes: {inventario.stock_actual()}")


# ──────────────────────────────────────────────
# ELIMINAR
# ──────────────────────────────────────────────
if st.session_state.page == "Eliminar":
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
            cita_eliminada = citas[idx]
            citas.pop(idx)
            gestor.guardar(citas)
            if "Planilla" in cita_eliminada.get("recursos_usados", []):
                inventario.devolver(cita_eliminada["pais"], cita_eliminada["Tipo_Tramite"])
            st.success(f"✅ Cita eliminada. Planillas restantes: {inventario.stock_actual()}")
            st.rerun()


# ──────────────────────────────────────────────
# MODIFICAR
# ──────────────────────────────────────────────
if st.session_state.page == "Modificar":
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
            nueva_fecha = st.selectbox(
                "Nueva fecha",
                fechas_validas,
                index=fechas_validas.index(date.fromisoformat(cita["fecha"])) if date.fromisoformat(cita["fecha"]) in fechas_validas else 0
            )
            horas_manana = [time(h, m) for h in range(9, 12) for m in [0, 15, 30, 45]]
            horas_tarde  = [time(h, m) for h in range(13, 17) for m in [0, 15, 30, 45]] + [time(17, 30)]
            horario_disponible = horas_manana + horas_tarde

            hora_actual = time(int(cita["hora"].split(":")[0]), int(cita["hora"].split(":")[1]))
            hora_idx = horario_disponible.index(hora_actual) if hora_actual in horario_disponible else 0

            nueva_hora = st.selectbox("Nuevo horario", horario_disponible, index=hora_idx)
            GuardarCambios = st.form_submit_button("Guardar cambios")

        # Botón de aceptar hueco modificar
        if "mod_pendiente" in st.session_state:
            st.info(f"⚠️ Hueco sugerido: {st.session_state['mod_hora_sugerida']}")
            col_a, col_b = st.columns([1, 4])
            if col_a.button("✅ Aceptar nuevo horario", key="btn_aceptar_modificar"):
                idx_mod, cita_mod = st.session_state.pop("mod_pendiente")
                cita_mod["hora"] = st.session_state.pop("mod_hora_sugerida")
                citas = gestor.cargar()
                citas[idx_mod] = cita_mod
                gestor.guardar(citas)
                st.success("✅ Cita modificada correctamente")
                st.rerun()
            if col_b.button("❌ Cancelar", key="btn_cancelar_modificar"):
                st.session_state.pop("mod_pendiente", None)
                st.session_state.pop("mod_hora_sugerida", None)
                st.rerun()

        if GuardarCambios:
            cita_modificada = cita.copy()
            cita_modificada["fecha"] = str(nueva_fecha)
            cita_modificada["hora"] = nueva_hora.strftime("%H:%M")

            otras_citas = citas[:idx] + citas[idx + 1:]

            if gestor.hay_conflicto(cita_modificada, otras_citas):
                hora_disponible = gestor.buscar_hueco(cita_modificada, otras_citas)
                if hora_disponible:
                    st.session_state["mod_pendiente"] = (idx, cita_modificada)
                    st.session_state["mod_hora_sugerida"] = hora_disponible
                    st.warning(f"⚠️ Conflicto detectado. Hueco disponible: {hora_disponible}")
                    st.rerun()
                else:
                    st.error("❌ No hay huecos disponibles ese día")
            else:
                citas[idx] = cita_modificada
                gestor.guardar(citas)
                st.success("✅ Cita modificada correctamente")
                st.rerun()
