from datetime import datetime, timedelta
import json
import os


ARCHIVO = os.path.join(os.path.dirname(__file__), "PerCitas.json")
ARCHIVO_ARCHIVO =   os.path.join(os.path.dirname(__file__),"CitasArchivadas.json")
class Cita:
    def __init__(self, pais, fecha, hora, duracion, trabajadora, recursos_usados,Telefono,TC,Name,LastNAme):
        self.pais = pais
        self.fecha = fecha
        self.hora = hora
        self.duracion = duracion
        self.trabajadora = trabajadora
        self.recursos_usados = recursos_usados
        self.Telefono = Telefono
        self.Tc = TC
        self.Name = Name 
        self.LastNAme = LastNAme

    def to_dict(self):
        return {
            "Pais": self.pais,
            "Fecha": self.fecha,
            "Hora": self.hora,
            "Duracion": self.duracion,
            "Trabajadora": self.trabajadora,
            "Recursos_usados": self.recursos_usados,
            "Telefono":self.Telefono,
            "Tc":self.Tc,
            "Name":self.Name,
            "LastName":self.LastNAme
        }


class GestorCitas:
    def cargar(self):
        try:
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                data = json.load(f)
                # si no es lista, inicializamos lista vacía
                if not isinstance(data, list):
                    return []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            # Crear archivo vacío si no existe o está corrupto
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

# ESto se encarga de Cuando se abra el sistema las citas q tengan fechas menores a la actual en el sistema se pasan a otro json para evitar eror en la modficacion y eliminacion de estas
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
                dia = c["fecha"]  # yyyy-mm-dd

                if dia not in archivo:
                  archivo[dia] = []

                  archivo[dia].append(c)
            else:
                citas_activas.append(c)

    # Guardar cambios
        self.guardar(citas_activas)

        with open(ARCHIVO_ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(archivo, f, indent=4, ensure_ascii=False)

        return citas_activas



    def guardar(self, citas):
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(citas, f, indent=4, ensure_ascii=False)
            











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
