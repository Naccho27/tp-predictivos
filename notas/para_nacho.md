# Para Nacho · respuesta y estado al 24/10

Hola Nacho, te contesto lo que me preguntaste y te dejo dos cosas de los datos que encontré y que nos afectan a los dos.

## Lo que había que acordar

1. **Limpieza:** de acuerdo con arrancar en 2017 y dejar afuera los fines de semana. Las dos decisiones se ven claras en tu notebook.
2. **Fecha de corte 1/12/2024:** de acuerdo, es la que usé. Entrenamiento: 10.072 filas (9/01/2017 a 29/11/2024). Prueba: 2.336 filas (2/12/2024 a 28/09/2026), un 18,8 %.
3. **Alta demanda por mediana de estación y tipo:** de acuerdo.
4. **Con y sin `_sem_ant`:** ya está hecho. El resultado es interesante:
   - Random Forest: MAE de 25,2 t en las dos versiones. La semana anterior no le agrega nada, porque con estación, tipo, día, mes y feriado ya aprende el nivel de cada día.
   - Regresión lineal: baja de 45,8 t a 29,5 t con la semana anterior, porque sola no puede armar ese nivel.
5. **Feriados federales como limitación:** de acuerdo, pero mirá el punto 2 de abajo, porque hay algo más.

## Cómo voy

- **Investigación del Random Forest y la regresión lineal:** terminada y pegada en el Docs (funcionamiento, entradas y salida, aplicación, ventajas y limitaciones, regresión lineal y fuentes).
- **Gráficos exploratorios:** hechos en `notebooks/03_regresion_rf.ipynb`. Están la distribución de toneladas, el promedio por mes y el promedio por día de la semana, más una tabla del efecto de los feriados. No repetí el de evolución por año.
- **Modelos y evaluación:** también en el notebook 03. Están la regresión lineal y el Random Forest con y sin semana anterior, la elección de parámetros con el último año del entrenamiento como validación, ejemplos de valores reales contra predichos, la importancia de las variables y los errores por tipo, por día y en feriados.

| Modelo | MAE en prueba |
|---|---|
| Random Forest | 25,2 t (11,9 % de un día promedio) |
| Repetir el mismo día de la semana anterior | 27,1 t |
| Regresión lineal con semana anterior | 29,5 t |
| Regresión lineal sin semana anterior | 45,8 t |

## Dos cosas de los datos que hay que decidir juntos

**1. Septiembre de 2026 parece cargado a medias.**
Desde el lunes 7/09/2026, la estación Sur registra más o menos la mitad de lo normal en los tres tipos de residuo a la vez. El total diario de la ciudad pasa de unas 1.050 t (agosto) a unas 510 t. La Norte sigue igual, no hay feriado que lo explique y el 28/09 casi no tiene datos (3 filas con 1 a 8 t). Lo más probable es que Seattle todavía no haya terminado de cargar esos días.

- En mi modelo son 78 filas (3 % de la prueba), pero suben el MAE de 21,9 t a 25,2 t.
- En tu clasificador, esos días van a salir todos como "baja demanda" aunque probablemente no lo sean.

No toqué nada de la limpieza porque es tu notebook. Propongo cortar los datos el **4/09/2026** en el notebook 01 y explicarlo como decisión de limpieza (datos recientes incompletos). ¿Qué te parece?

**2. La variable `feriado` mezcla dos tipos de feriado.**
En Acción de Gracias, Navidad y Año Nuevo casi no se recibe nada (de 1 a 7 t). En los demás feriados federales (Día del Trabajo, Memorial Day, etc.) se trabaja casi normal. Mi modelo se equivoca unas 170 t en promedio en esos tres días, contra unas 46 t en los demás feriados.

Propongo agregar en el notebook 01 una columna `sin_recoleccion` (1 en esos tres feriados) y usarla en los dos modelos. No genera fuga, porque se sabe de antemano. Si no llegamos, lo dejamos como limitación y mejora futura.

## Lo de `anio` que me preocupaba

Pensaba que el Random Forest iba a subestimar 2025 y 2026 porque no extrapola años nuevos. Al final no pesa: el total anual se mantiene en unas 280.000 t y el año explica menos del 2,5 % de la importancia del modelo.

## Sobre el repo

Perdón: el primer commit del notebook 03 (la exploración) se subió directo a `main`. Solo agrega mi archivo y no toca nada tuyo. Todo lo demás está en mi rama **`lazaro`**: el notebook 03 completo y esta nota. Cuando revises, lo pasamos a `main` con un pull request.

Lázaro
