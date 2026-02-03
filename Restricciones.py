#Restricciones
from typing import Dict, List
# ESTAS SON LAS RESTRICCIONES 
#    *LEER EN EL README*

PERSONAL_AUTORIZADO:Dict[str, List[str]] = {
    "España": ["Zahili", "Yuli"],
    "EEUU"  : ["Yanara"],
    "Canadá": ["Betsy"],
    "Brasil": ["Dania"],
    "Turkia": ["Dania"],
}

CO_REQUISITOS:Dict[str, List[str]] = {
    "España": ["Planilla", "Laptop Yuli","Laptop Zahili", "Escaner", "Impresora"],
    "EEUU"  : ["Planilla", "Laptop Yanara"],
    "Canadá": ["Planilla", "Laptop Betsy", "Escaner"],
    "Brasil": ["Laptop Dania", "Escaner"],
    "Turkia": ["Planilla", "Escaner","Laptop Dania"]
}


DURACION_MIN:Dict[str, Dict[str, int]] = {
    "España": {
        "Lmd": 50,
        "Visado": 30,
        "Legalización": 30,
        "Transcripción de Matrimonio": 40,
        "Asesoría": 20,
        "Cita de Pasaporte": 20
    },
    "EEUU": {
        "Visa turismo": 50,
        "Visa trabajo": 50,
        "Asesoría": 20
    },
    "Canadá": {
        "Visa turismo": 80,
        "Asesoría": 30
    },
    "Brasil": {
        "Visa Turismo": 80,
        "Asesoría": 30
    },
    "Turkia": {
        "Visa Turismo": 45,
        "Asesoría": 20
    }
}






