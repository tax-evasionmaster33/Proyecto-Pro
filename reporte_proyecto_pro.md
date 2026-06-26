
## 1. Visión general del sistema

El Gestor de Citas de la Oficina de Trámites Proenza es una aplicación de escritorio web construida con **Streamlit** cuyo propósito es administrar el ciclo completo de las citas migratorias que gestiona la oficina. El sistema cubre cinco países de destino —España, EEUU, Canadá, Brasil y Turkia— y permite agendar, modificar, eliminar y consultar citas respetando un conjunto de reglas de negocio que reflejan la operación real de la oficina: disponibilidad de personal especializado, uso exclusivo de recursos materiales, franjas horarias válidas y consumo de inventario de planillas.

La arquitectura es deliberadamente simple: no hay base de datos relacional ni servidor externo. La persistencia se resuelve con tres archivos JSON (`PerCitas.json`, `CitasArchivadas.json`, `Inventario.json`) y toda la lógica de dominio vive en dos módulos Python (`Gestor.py` y `Restricciones.py`). La interfaz visual la provee Streamlit, que sirve la aplicación en el navegador mediante `streamlit run Main.py`.



## 2. Estructura de archivos

```
Proyecto-Pro/
│
├── Main.py              # Punto de entrada; página de inicio
├── Gestor.py            # Clases de dominio: GestorCitas, GestorInventario, Cita
├── Restricciones.py     # Diccionarios de reglas de negocio
│
├── PerCitas.json        # Citas activas (futuras)
├── CitasArchivadas.json # Citas pasadas, indexadas por fecha
├── Inventario.json      # Stock de planillas con control de recarga mensual
│
└── requerimientos.txt   # Dependencias pip
```

Cada módulo tiene una responsabilidad única y bien delimitada. `Restricciones.py` actúa como una capa de configuración pura —no tiene funciones, solo constantes—, lo cual facilita ajustar reglas de negocio sin tocar la lógica de la aplicación.

---

## 3. Módulo `Restricciones.py` — La capa de configuración

Este archivo centraliza todas las reglas de negocio del dominio en forma de diccionarios tipados con `typing`. Es el único lugar donde hay que hacer cambios cuando la oficina incorpora un nuevo país, una nueva tramitadora o modifica duraciones y consumos.

### 3.1 `PERSONAL_AUTORIZADO`

```python
PERSONAL_AUTORIZADO: Dict[str, List[str]] = {
    "España":  ["Zahili", "Yuli"],
    "EEUU":    ["Yanara"],
    "Canadá":  ["Betsy"],
    "Brasil":  ["Dania"],
    "Turkia":  ["Dania"],
}
```

Mapea cada país a la lista de tramitadoras autorizadas para atender ese destino. La validación en `GestorCitas.validar_restricciones` usa este diccionario para rechazar asignaciones inválidas antes de guardar cualquier cita.

### 3.2 `CO_REQUISITOS`

```python
CO_REQUISITOS: Dict[str, List[str]] = {
    "España":  ["Planilla", "Laptop Yuli", "Laptop Zahili", "Escaner", "Impresora"],
    "EEUU":    ["Planilla", "Laptop Yanara"],
    ...
}
```

Define el conjunto de recursos materiales disponibles (y obligatorios como pool) por país. La lógica de validación comprueba que los recursos seleccionados en el formulario no dejen vacío el conjunto requerido para ese destino. Nótese que las laptops están nominadas por tramitadora (`Laptop Yuli`, `Laptop Zahili`), lo que las convierte en recursos con identidad propia y evita que dos tramitadoras compartan la misma laptop simultáneamente sin conflicto explícito.

### 3.3 `DURACION_MIN`

```python
DURACION_MIN: Dict[str, Dict[str, int]] = {
    "España": {
        "Lmd": 50,
        "Visado": 30,
        ...
    },
    ...
}
```

Establece la duración en minutos para cada tipo de trámite por país. Esto garantiza que los tiempos agendados sean realistas y que no se produzcan solapamientos invisibles por citas demasiado cortas.

### 3.4 `CONSUMO_PLANILLAS` y `RECARGA_MENSUAL_PLANILLAS`

```python
CONSUMO_PLANILLAS: Dict[str, Dict[str, int]] = {
    "España": { "Lmd": 5, "Visado": 3, ... },
    ...
}
RECARGA_MENSUAL_PLANILLAS = 500
```

Cada tipo de trámite consume un número específico de planillas físicas. El sistema descuenta del inventario al crear una cita y lo devuelve al eliminarla, modelando el consumo real de material de oficina. La recarga mensual de 500 unidades se aplica automáticamente al inicio de cada mes calendario.

---

## 4. Módulo `Gestor.py` — La lógica de dominio

### 4.1 Clase `Cita`

Es un Data Transfer Object (DTO) simple que encapsula los atributos de una cita:

| Atributo | Tipo | Descripción |
|---|---|---|
| `pais` | str | País de destino del trámite |
| `fecha` | str | Fecha en formato `YYYY-MM-DD` |
| `hora` | str | Hora en formato `HH:MM` |
| `duracion` | int | Duración en minutos |
| `trabajadora` | str | Tramitadora asignada |
| `recursos_usados` | list | Recursos materiales seleccionados |
| `telefono` | str | Teléfono de contacto del cliente |
| `tc` | str | Tipo de trámite |
| `name` / `last_name` | str | Nombre y apellido del cliente |

El método `to_dict()` serializa la instancia a un diccionario compatible con `json.dump`, que es el único mecanismo de persistencia del sistema. La simplicidad de esta clase es intencional: no tiene lógica propia, delegando toda la validación y operación a `GestorCitas`.

### 4.2 Clase `GestorCitas`

Es el núcleo operativo del sistema. Contiene seis métodos que cubren el ciclo completo de vida de una cita.

#### `cargar()` y `guardar(citas)`

```python
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
```

`cargar` lee `PerCitas.json` y devuelve la lista de citas activas. La implementación es defensiva: si el archivo no existe o está corrompido, lo recrea vacío y continúa sin lanzar una excepción. `guardar` escribe la lista completa de vuelta al archivo con indentación y soporte UTF-8, lo cual preserva los caracteres especiales del español.

#### `cargar_archivo()` — Historial de citas pasadas

Carga `CitasArchivadas.json`, que tiene una estructura diferente a `PerCitas.json`: es un diccionario donde cada clave es una fecha (`"2026-06-15"`) y el valor es una lista de citas que ocurrieron ese día. Esto permite consultar el historial agrupado por día sin tener que recorrer toda la colección.

#### `archivar_citas_pasadas()` — Depuración automática del estado activo

```python
def archivar_citas_pasadas(self):
    citas = self.cargar()
    archivo = self.cargar_archivo()
    ahora = datetime.now()
    citas_activas = []

    for c in citas:
        fecha_hora = datetime.strptime(f"{c['fecha']} {c['hora']}", "%Y-%m-%d %H:%M")
        if fecha_hora < ahora:
            dia = c["fecha"]
            if dia not in archivo:
                archivo[dia] = []
            archivo[dia].append(c)
        else:
            citas_activas.append(c)

    self.guardar(citas_activas)
    with open(ARCHIVO_ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(archivo, f, indent=4, ensure_ascii=False)
    return citas_activas
```

Este método es el mecanismo de mantenimiento automático. Cada vez que se invoca —típicamente al cargar la vista del itinerario o al iniciar la app—, compara la fecha y hora de cada cita activa con el momento actual. Las citas cuya `fecha + hora` ya pasaron se mueven al archivo histórico; el resto permanece en `PerCitas.json`. Es una operación de clasificación en tiempo lineal O(n) que mantiene pequeño el archivo de citas activas con el paso del tiempo.

#### `validar_restricciones(pais, trabajadora, recursos, tipo_tramite, duracion)`

```python
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
```

Ejecuta tres validaciones secuenciales contra las constantes de `Restricciones.py` y acumula todos los errores encontrados en una lista, en lugar de fallar al primer error. Esto permite mostrarle al usuario todos los problemas de una vez, mejorando la experiencia de uso. La función retorna la lista vacía si todo es válido, lo que hace que la comprobación en el código llamador sea trivial: `if errores: ...`.

#### `hay_conflicto(nueva, citas)` — Detección de solapamiento

```python
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
```

Implementa la lógica clásica de detección de intervalos solapados: dos intervalos `[A, B)` y `[C, D)` se superponen si y solo si `A < D` y `B > C`. El método aplica esta condición y luego verifica si el solapamiento implica un conflicto real, es decir, si la nueva cita comparte tramitadora o al menos un recurso material con la cita existente. Esto permite que dos citas se solapen en el tiempo siempre que usen recursos completamente distintos —un escenario válido si, por ejemplo, hay dos citas de diferentes países atendidas por diferentes tramitadoras en el mismo bloque horario.

#### `buscar_hueco(base, citas, paso=15)` — Resolución automática de conflictos

```python
def buscar_hueco(self, base, citas, paso=15):
    hora = datetime.strptime(f"{base['fecha']} {base['hora']}", "%Y-%m-%d %H:%M")
    cierre = hora.replace(hour=17, minute=30)

    while hora <= cierre:
        base["hora"] = hora.strftime("%H:%M")
        if not self.hay_conflicto(base, citas):
            return base["hora"]
        hora += timedelta(minutes=paso)

    return None
```

Cuando el horario solicitado presenta conflicto, este método intenta encontrar el primer slot libre avanzando en incrementos de 15 minutos hasta las 17:30. Retorna la hora libre encontrada o `None` si no hay hueco disponible en el día. El paso de 15 minutos refleja la granularidad de la agenda y proporciona un margen de preparación entre citas consecutivas.

### 4.3 Clase `GestorInventario`

Maneja el stock de planillas físicas. Su estado persiste en `Inventario.json` con tres campos: `stock` (unidades disponibles), `recarga_mensual` (constante: 500) y `ultimo_reset` (fecha del último reinicio mensual).

#### `verificar_recarga()` — Auto-recarga mensual

```python
def verificar_recarga(self):
    data = self.cargar()
    hoy = datetime.now()
    ultimo_reset = datetime.strptime(data["planillas"]["ultimo_reset"], "%Y-%m-%d")

    if hoy.year > ultimo_reset.year or hoy.month > ultimo_reset.month:
        data["planillas"]["stock"] += data["planillas"]["recarga_mensual"]
        data["planillas"]["ultimo_reset"] = hoy.strftime("%Y-%m-01")
        self.guardar(data)

    return data
```

Este método se llama cada vez que se consulta el stock. Si ha cambiado el mes (o el año), suma la recarga mensual al stock existente y actualiza la fecha de reset. La condición `hoy.year > ultimo_reset.year or hoy.month > ultimo_reset.month` cubre correctamente el cruce de año. Importante: la recarga es **acumulativa** —si quedaban planillas del mes anterior, se conservan— lo cual es el comportamiento correcto para una oficina real.

#### `hay_planillas(pais, tipo_tramite)`, `descontar(pais, tipo_tramite)`, `devolver(pais, tipo_tramite)`

```python
def hay_planillas(self, pais, tipo_tramite):
    consumo = CONSUMO_PLANILLAS.get(pais, {}).get(tipo_tramite, 0)
    return self.stock_actual() >= consumo, consumo

def descontar(self, pais, tipo_tramite):
    consumo = CONSUMO_PLANILLAS.get(pais, {}).get(tipo_tramite, 0)
    if consumo == 0:
        return
    data = self.cargar()
    data["planillas"]["stock"] = max(0, data["planillas"]["stock"] - consumo)
    self.guardar(data)

def devolver(self, pais, tipo_tramite):
    consumo = CONSUMO_PLANILLAS.get(pais, {}).get(tipo_tramite, 0)
    if consumo == 0:
        return
    data = self.cargar()
    data["planillas"]["stock"] += consumo
    self.guardar(data)
```

Estos tres métodos forman el ciclo completo de inventario. `hay_planillas` verifica disponibilidad antes de confirmar una cita. `descontar` descuenta al crear. `devolver` reintegra al eliminar. El uso de `max(0, stock - consumo)` en `descontar` previene stocks negativos. Nótese que `devolver` no tiene límite superior: si se elimina una cita y se devuelven planillas, el stock puede superar la recarga mensual, lo cual es intencionado (planillas acumuladas de meses anteriores).

---

## 5. Módulo `Main.py` — Punto de entrada y página de inicio

```python
st.set_page_config(
    page_title="Home",
    page_icon="Fixed 1.png",
    layout="wide",
)
```

`Main.py` es la pantalla de bienvenida del sistema. El llamado a `st.set_page_config` debe ser la primera instrucción de Streamlit en toda la aplicación —error común que el código comenta explícitamente. La página muestra información de contacto de la oficina, una fotografía y un panel opcional con el detalle de los recursos humanos y materiales disponibles. La navegación hacia las otras secciones (agenda, itinerario) se realiza a través de la barra lateral de Streamlit, que Streamlit genera automáticamente a partir de la estructura de páginas del proyecto.

---

## 6. Esquema de persistencia JSON

### `PerCitas.json` — Citas activas

Array de objetos. Cada objeto representa una cita futura con campos planos de tipos primitivos, lo que facilita la serialización/deserialización sin librerías adicionales. El estado actual tiene ~70 citas activas distribuidas entre junio y julio de 2026.

### `CitasArchivadas.json` — Historial

Diccionario indexado por fecha. Esta decisión de diseño permite recuperar todas las citas de un día concreto con una búsqueda O(1) por clave, sin iterar el historial completo.

### `Inventario.json`

```json
{
    "planillas": {
        "stock": 495,
        "recarga_mensual": 500,
        "ultimo_reset": "2026-06-01"
    }
}
```

Objeto único con tres campos. El diseño es extensible: si en el futuro se incorporan otros consumibles (sobres, sellos, etc.), se agregan como nuevas claves en el mismo archivo sin romper la estructura existente.

---

## 7. Flujos de operación principales

### Agendar una cita

1. El usuario selecciona país, tipo de trámite, tramitadora, recursos, fecha, hora, duración y datos del cliente.
2. Se llama a `GestorCitas.validar_restricciones` → si hay errores, se muestran todos y se detiene.
3. Se llama a `GestorInventario.hay_planillas` → si no hay stock suficiente, se rechaza la cita.
4. Se llama a `GestorCitas.hay_conflicto` → si hay solapamiento, se invoca `buscar_hueco` para proponer un horario alternativo.
5. Si todo es válido, se llama a `GestorInventario.descontar` y luego se agrega la cita a la lista y se guarda.

### Eliminar una cita

1. El usuario selecciona la cita de una lista desplegable.
2. Se llama a `GestorInventario.devolver` para reintegrar las planillas.
3. Se elimina la cita de la lista y se guarda.

### Modificar una cita

1. El usuario selecciona la cita y especifica nueva fecha u hora.
2. Se valida el nuevo horario con `hay_conflicto`; si hay conflicto, se ofrece un hueco alternativo.
3. Se actualiza el campo modificado y se guarda.

### Consultar el itinerario

1. Se llama a `archivar_citas_pasadas` para depurar el estado activo.
2. Se filtran las citas activas por la fecha seleccionada y se muestran en tabla.
3. Opcionalmente se muestra la tabla del historial (`CitasArchivadas.json`) con las citas pasadas.

---

## 8. Otros detalles a tener en cuenta

**Separación de configuración y lógica.** `Restricciones.py` no importa nada de `Gestor.py` ni de Streamlit. Es puro dato. Esto hace que cambiar una regla de negocio (añadir un país, cambiar una duración mínima) sea trivial y sin riesgo de romper otra cosa.

**Validación acumulativa.** `validar_restricciones` retorna una lista de errores, no lanza una excepción al primer problema. El usuario ve todos los errores de una vez en lugar de tener que corregirlos uno por uno en sucesivos intentos.

**Doble archivo JSON.** Separar citas activas de citas pasadas mantiene pequeño el archivo que se lee y escribe con frecuencia, y da estructura natural al historial sin necesidad de consultas complejas.

**Granularidad de 15 minutos.** El paso fijo en `buscar_hueco` alinea todos los horarios a múltiplos de 15 minutos, lo que produce una agenda ordenada y deja márgenes de preparación entre citas consecutivas que usan los mismos recursos.

**Recursos con identidad nominal.** Nombrar las laptops como `Laptop Yuli` o `Laptop Zahili` en lugar de simplemente `Laptop` resuelve elegantemente el problema de asignación: el sistema puede distinguir qué laptop está ocupada sin necesidad de una tabla de relaciones adicional.
