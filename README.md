# TP Algoritmos predictivos

**Integrantes:** Ignacio Nicolás González y Lázaro Ruidavets

Clasificación (árbol de decisión) y regresión (Random Forest, con regresión lineal como base) sobre la recolección residencial de residuos de Seattle, vinculadas con UrbanRec.

## Datos

- **Fuente:** *SPU Solid Waste Tons and Trips Data*, City of Seattle: https://cos-data.seattle.gov/d/293h-ej5h
- `data/raw/seattle_tons_trips.csv`: archivo original, descargado el 15/10/2026. No volver a descargarlo: el dataset se sigue actualizando y cambiarían los resultados.
- `data/processed/datos_limpios.csv`: salida del notebook 01, con 12.330 registros (días hábiles del 9/01/2017 al 4/09/2026).

| Variable | Descripción |
| --- | --- |
| `fecha` | Día del registro |
| `estacion` | Estación de transferencia: Norte o Sur |
| `tipo` | Tipo de residuo: Basura, Reciclables u Organicos |
| `toneladas` | Toneladas recibidas en el día (objetivo de la regresión) |
| `viajes` | Viajes de camión del día (de acá sale la categoría de alta demanda; no se usa como entrada) |
| `anio`, `mes`, `dia_semana` | Obtenidos de la fecha |
| `feriado` | 1 si es feriado federal de EE. UU. |
| `sin_recoleccion` | 1 en Acción de Gracias, el 25 de diciembre y el 1 de enero |
| `toneladas_sem_ant`, `viajes_sem_ant` | Valores del mismo día de la semana anterior, misma estación y tipo |

## Contenido

| Archivo | Qué hace |
| --- | --- |
| `notebooks/01_preparacion.ipynb` | Limpieza y creación de variables; genera el CSV limpio |
| `notebooks/02_clasificacion_arbol.ipynb` | Árbol de decisión: entrenamiento, evaluación y guardado del modelo |
| `notebooks/03_regresion_rf.ipynb` | Exploración, regresión lineal y Random Forest |
| `modelos/arbol_alta_demanda.joblib` | Árbol entrenado, orden de columnas y umbral de decisión (0,4) |
| `api/main.py` | Prototipo de API con FastAPI para la alerta de alta demanda |

## Cómo reproducirlo

Probado con Python 3.13.

1. `python -m venv .venv`
2. Activar el entorno (Windows: `.venv\Scripts\activate`)
3. `pip install -r requirements.txt`
4. Ejecutar los notebooks de `notebooks/` en orden: 01, 02 y 03, desde esa carpeta.

Todos los modelos usan `random_state=42`, así que cada ejecución da los mismos resultados.

## Prototipo de API (vinculación con UrbanRec)

Desde la raíz del repositorio, con el entorno activado:

```
uvicorn api.main:app --reload
```

Abrir http://127.0.0.1:8000/docs y probar `POST /prediccion/alta-demanda`.