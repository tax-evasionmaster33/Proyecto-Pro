from datetime import datetime, timedelta
import json
import os

from Restricciones import PERSONAL_AUTORIZADO, CO_REQUISITOS, DURACION_MIN, CONSUMO_PLANILLAS, RECARGA_MENSUAL_PLANILLAS

ARCHIVO = os.path.join(os.path.dirname(__file__), "PerCitas.json")
ARCHIVO_ARCHIVO = os.path.join(os.path.dirname(__file__), "CitasArchivadas.json")
ARCHIVO_INVENTARIO = os.path.join(os.path.dirname(__file__), "Inventario.json")


class Cita:
    def __init__(self, pais, fecha, hora, duracion, trabajadora, recursos_usados, telefono, tc, name, last_name):
        self.pais = pais
        self.fecha = fecha
        self.hora = hora
        self.duracion = duracion
        self.trabajadora = trabajadora
        self.recursos_usados = recursos_usados
        self.telefono = telefono
        self.tc = tc
        self.name = name
        self.last_name = last_name

    def to_dict(self):
        return {
            "Pais": self.pais,
            "Fecha": self.fecha,
            "Hora": self.hora,
            "Duracion": self.duracion,
            "Trabajadora": self.trabajadora,
            "Recursos_usados": self.recursos_usados,
            "Telefono": self.telefono,
            "Tc": self.tc,
            "Name": self.name,
            "LastName": self.last_name,
        }


class GestorCitas:
    def cargar(self):
        try:
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            with open(ARCHIVO, "w", encoding="utf-8") as f:
                json.dump([], f)
            return []

    def cargar_archivo(self):
        try:
            with open(ARCHIVO_ARCHIVO, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                return {}
        except (FileNotFoundError, json.JSONDecodeError):
            with open(ARCHIVO_ARCHIVO, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4, ensure_ascii=False)
            return {}

    def archivar_citas_pasadas(self):
        citas = self.cargar()
        archivo = self.cargar_archivo()
        ahora = datetime.now()

        citas_activas = []

        for c in citas:
            fecha_hora = datetime.strptime(
                f"{c['fecha']} {c['hora']}", "%Y-%m-%d %H:%M"
            )

            if fecha_hora < ahora:
                dia = c["fecha"]
                if dia not in archivo:
                    archivo[dia] = []
                archivo[dia].append(c)  # CORRECCIÓN: fuera del if
            else:
                citas_activas.append(c)

        self.guardar(citas_activas)

        with open(ARCHIVO_ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(archivo, f, indent=4, ensure_ascii=False)

        return citas_activas

    def guardar(self, citas):
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(citas, f, indent=4, ensure_ascii=False)

    def validar_restricciones(self, pais, trabajadora, recursos, tipo_tramite, duracion):
        errores = []

        autorizadas = PERSONAL_AUTORIZADO.get(pais, [])
        if trabajadora not in autorizadas:
            errores.append(f"❌ {trabajadora} no está autorizada para trámites de {pais}.")

        requeridos = set(CO_REQUISITOS.get(pais, []))
        provistos = set(recursos)
        faltantes = requeridos - provistos
        if faltantes:
            errores.append(f"❌ Faltan recursos: {', '.join(faltantes)}")

        dur_min = DURACION_MIN.get(pais, {}).get(tipo_tramite)
        if dur_min and duracion < dur_min:
            errores.append(f"❌ Duración mínima para {tipo_tramite} es {dur_min} min.")

        return errores

    def hay_conflicto(self, nueva, citas):
        ini_n = datetime.strptime(f"{nueva['fecha']} {nueva['hora']}", "%Y-%m-%d %H:%M")
        fin_n = ini_n + timedelta(minutes=nueva["duracion"])

        for c in citas:
            ini_c = datetime.strptime(f"{c['fecha']} {c['hora']}", "%Y-%m-%d %H:%M")
            fin_c = ini_c + timedelta(minutes=c["duracion"])

            solapa = ini_n < fin_c and fin_n > ini_c

            if solapa and (
                c["trabajadora"] == nueva["trabajadora"] or
                set(c["recursos_usados"]) & set(nueva["recursos_usados"])
            ):
                return True
        return False

    def buscar_hueco(self, base, citas, paso=15):
        hora = datetime.strptime(
            f"{base['fecha']} {base['hora']}", "%Y-%m-%d %H:%M"
        )
        cierre = hora.replace(hour=17, minute=30)

        while hora <= cierre:
            base["hora"] = hora.strftime("%H:%M")
            if not self.hay_conflicto(base, citas):
                return base["hora"]
            hora += timedelta(minutes=paso)

        return None


class GestorInventario:
    def cargar(self):
        try:
            with open(ARCHIVO_INVENTARIO, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Inventario inicial
            data = {
                "planillas": {
                    "stock": RECARGA_MENSUAL_PLANILLAS,
                    "recarga_mensual": RECARGA_MENSUAL_PLANILLAS,
                    "ultimo_reset": datetime.now().strftime("%Y-%m-01")
                }
            }
            self.guardar(data)
            return data

    def guardar(self, data):
        with open(ARCHIVO_INVENTARIO, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def verificar_recarga(self):
        """Si es el primer dia del mes y no se ha recargado, suma el stock."""
        data = self.cargar()
        hoy = datetime.now()
        ultimo_reset = datetime.strptime(data["planillas"]["ultimo_reset"], "%Y-%m-%d")

        # Es un mes nuevo
        if hoy.year > ultimo_reset.year or hoy.month > ultimo_reset.month:
            data["planillas"]["stock"] += data["planillas"]["recarga_mensual"]
            data["planillas"]["ultimo_reset"] = hoy.strftime("%Y-%m-01")
            self.guardar(data)

        return data

    def stock_actual(self):
        data = self.verificar_recarga()
        return data["planillas"]["stock"]

    def hay_planillas(self, pais, tipo_tramite):
        """Devuelve True si hay suficientes planillas para el trámite."""
        consumo = CONSUMO_PLANILLAS.get(pais, {}).get(tipo_tramite, 0)
        return self.stock_actual() >= consumo, consumo

    def descontar(self, pais, tipo_tramite):
        """Descuenta planillas al crear una cita."""
        consumo = CONSUMO_PLANILLAS.get(pais, {}).get(tipo_tramite, 0)
        if consumo == 0:
            return
        data = self.cargar()
        data["planillas"]["stock"] = max(0, data["planillas"]["stock"] - consumo)
        self.guardar(data)

    def devolver(self, pais, tipo_tramite):
        """Devuelve planillas al eliminar una cita."""
        consumo = CONSUMO_PLANILLAS.get(pais, {}).get(tipo_tramite, 0)
        if consumo == 0:
            return
        data = self.cargar()
        data["planillas"]["stock"] += consumo
        self.guardar(data)
