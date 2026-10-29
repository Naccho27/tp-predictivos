# Prototipo de integración con UrbanRec: API de predicción de alta demanda
#
# Qué hace: carga el árbol de decisión entrenado en el notebook 02 y responde,
# para una estación, un tipo de residuo y una fecha, si se espera un día de alta demanda.
#
# Por qué una API: en UrbanRec, el backend de Node consultaría este servicio de Python
# y mostraría la alerta en el panel del operador. Así el modelo queda separado del sistema
# y se puede reentrenar sin tocar el resto del código.
#
# Cómo ejecutarlo (desde la raíz del repositorio, con el .venv activado):
#   uvicorn api.main:app --reload
# y abrir http://127.0.0.1:8000/docs

from datetime import date
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pandas.tseries.holiday import USFederalHolidayCalendar
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# 1 · Cargar el modelo (una sola vez, al arrancar)
# ---------------------------------------------------------------------------

# Ruta armada a partir de la ubicación de este archivo, para que funcione
# sin importar desde qué carpeta se ejecute uvicorn
RUTA_MODELO = Path(__file__).resolve().parent.parent / "modelos" / "arbol_alta_demanda.joblib"

paquete = joblib.load(RUTA_MODELO)
modelo = paquete["modelo"]       # el árbol entrenado
COLUMNAS = paquete["columnas"]   # las 16 columnas, en el orden en que el árbol las espera
UMBRAL = paquete["umbral"]       # 0,4: elegido con validación en el notebook 02

DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]  # igual que en el notebook 01

app = FastAPI(
    title="UrbanRec · Predicción de alta demanda",
    description="Prototipo del TP de algoritmos predictivos. Modelo: árbol de decisión "
                "entrenado con datos de Seattle (2017 a 2024).",
)

# ---------------------------------------------------------------------------
# 2 · Qué recibe y qué devuelve
# ---------------------------------------------------------------------------

# Pydantic valida los datos antes de que lleguen al modelo: si falta un campo,
# viene una estación que no existe o un número negativo, responde con error solo.
class Consulta(BaseModel):
    estacion: Literal["Norte", "Sur"]
    tipo: Literal["Basura", "Organicos", "Reciclables"]
    fecha: date = Field(description="Día a predecir (AAAA-MM-DD). Solo días hábiles.")
    viajes_sem_ant: int = Field(ge=0, description="Viajes del mismo día de la semana anterior")
    toneladas_sem_ant: float = Field(ge=0, description="Toneladas del mismo día de la semana anterior")


class Prediccion(BaseModel):
    probabilidad_alta: float
    alerta: bool
    umbral: float
    mensaje: str


# ---------------------------------------------------------------------------
# 3 · Preparar los datos igual que en los notebooks
# ---------------------------------------------------------------------------

def preparar(c: Consulta) -> pd.DataFrame:
    # Variables de calendario, calculadas igual que en el notebook 01 (Paso 11)
    feriados = USFederalHolidayCalendar().holidays(c.fecha, c.fecha)
    accion_de_gracias = c.fecha.month == 11 and c.fecha.weekday() == 3 and 22 <= c.fecha.day <= 28
    navidad = c.fecha.month == 12 and c.fecha.day == 25
    anio_nuevo = c.fecha.month == 1 and c.fecha.day == 1

    # Arrancamos con las 16 columnas en 0 y completamos las que corresponden.
    # Así el one-hot queda igual que en el entrenamiento: una sola columna en 1
    # por estación, tipo y día.
    fila = dict.fromkeys(COLUMNAS, 0)
    fila["anio"] = c.fecha.year
    fila["mes"] = c.fecha.month
    fila["feriado"] = int(len(feriados) > 0)
    fila["sin_recoleccion"] = int(accion_de_gracias or navidad or anio_nuevo)
    fila["viajes_sem_ant"] = c.viajes_sem_ant
    fila["toneladas_sem_ant"] = c.toneladas_sem_ant
    fila[f"estacion_{c.estacion}"] = 1
    fila[f"tipo_{c.tipo}"] = 1
    fila[f"dia_semana_{DIAS[c.fecha.weekday()]}"] = 1

    # DataFrame de una fila, con las columnas en el orden exacto del entrenamiento
    return pd.DataFrame([fila])[COLUMNAS]


# ---------------------------------------------------------------------------
# 4 · El endpoint
# ---------------------------------------------------------------------------

@app.post("/prediccion/alta-demanda", response_model=Prediccion)
def predecir(c: Consulta):
    # Casos que el modelo no conoce: se rechazan en lugar de devolver una predicción inventada
    if c.fecha.weekday() >= 5:
        raise HTTPException(422, "El modelo solo predice días hábiles (lunes a viernes).")
    if c.estacion == "Norte" and c.tipo == "Reciclables":
        raise HTTPException(422, "La estación Norte no recibe reciclables en los datos de entrenamiento.")

    # predict_proba devuelve [P(normal), P(alta)]; nos quedamos con la segunda
    prob = float(modelo.predict_proba(preparar(c))[0, 1])

    # Misma regla de decisión que en el notebook 02 (Paso 15)
    alerta = prob > UMBRAL
    if alerta:
        mensaje = f"Alta demanda prevista en {c.estacion} ({c.tipo}): reforzar camiones y personal."
    else:
        mensaje = f"Demanda normal prevista en {c.estacion} ({c.tipo})."

    return Prediccion(probabilidad_alta=round(prob, 3), alerta=alerta, umbral=UMBRAL, mensaje=mensaje)