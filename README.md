# 🎓 Alerta Temprana de Deserción Estudiantil

### Prototipo MVP para la Universidad Israel · Datos ficticios con fines demostrativos

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![OpenAPI](https://img.shields.io/badge/OpenAPI-6BA539?style=for-the-badge&logo=openapiinitiative&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

> Desarrollado por **Diego Vallejo**.

---

## 📑 Contenido

1. [¿Qué problema resuelve?](#-qué-problema-resuelve)
2. [La solución](#-la-solución)
3. [Tecnología de API utilizada](#-tecnología-de-api-utilizada)
4. [Arquitectura](#-arquitectura)
5. [Modelo de datos](#-modelo-de-datos)
6. [Cómo se calcula el riesgo hoy](#-cómo-se-calcula-el-riesgo-hoy)
7. [Estructura del proyecto](#-estructura-del-proyecto)
8. [Instalación y ejecución](#-instalación-y-ejecución)
9. [Endpoints](#-endpoints)
10. [Evolución a Machine Learning](#-evolución-a-machine-learning)
11. [Consideraciones éticas y de privacidad](#-consideraciones-éticas-y-de-privacidad)
12. [Limitaciones y hoja de ruta](#-limitaciones-y-hoja-de-ruta)

---

## 🎯 ¿Qué problema resuelve?

La **deserción estudiantil** es uno de los principales desafíos de la educación superior: cada estudiante
que abandona representa una trayectoria de vida interrumpida y una pérdida para la institución.

Casi siempre existen **señales previas** al abandono: baja de calificaciones, inasistencias, materias
reprobadas o dificultades económicas. El problema es que esas señales viven en sistemas distintos
(académico, asistencia, financiero) y, cuando alguien las junta, **suele ser demasiado tarde**.

| Situación actual | Consecuencia |
|---|---|
| Datos dispersos en varios sistemas | Nadie ve el panorama completo del estudiante |
| Detección reactiva (cuando el estudiante ya se fue) | Se pierde la ventana de intervención |
| Tutores sin criterio de priorización | Se atiende por intuición, no por urgencia |
| Sin registro de intervenciones | No se puede medir si la ayuda funcionó |

## 💡 La solución

Un **panel de alerta temprana** que consolida las señales de riesgo en un único puntaje por estudiante
y permite actuar desde la misma pantalla:

- 🔎 **Priorizar:** lista ordenada de mayor a menor riesgo, filtrable por carrera y nivel.
- 🧭 **Explicar:** cada alerta indica *por qué* el estudiante está en riesgo (promedio, asistencia, etc.).
- 🤝 **Intervenir:** el tutor registra una tutoría (académica, psicológica o financiera) con un clic.
- 📊 **Medir:** indicadores generales (estudiantes por nivel de riesgo y tutorías realizadas).

---

## 🔌 Tecnología de API utilizada

La API está construida con **[FastAPI](https://fastapi.tiangolo.com/)**, un framework web de Python
para crear APIs **REST** sobre HTTP con intercambio de datos en **JSON**.

| Componente | Rol en el proyecto |
|---|---|
| **FastAPI** | Define los endpoints REST (`GET`, `POST`) y sus rutas |
| **OpenAPI 3** | Estándar de especificación que FastAPI genera automáticamente a partir del código |
| **Swagger UI** (`/docs`) | Documentación interactiva: permite probar cada endpoint desde el navegador |
| **ReDoc** (`/redoc`) | Documentación alternativa de solo lectura, ideal para compartir |
| **Pydantic** | Valida los datos de entrada (por ejemplo, el cuerpo de una tutoría) y devuelve errores claros |
| **Uvicorn** | Servidor ASGI que ejecuta la aplicación |
| **psycopg2** | Conector a PostgreSQL |
| **CORS Middleware** | Permite que el frontend (otro puerto) consuma la API |

**¿Por qué FastAPI para este escenario?**

- ✅ **Documentación automática:** cada endpoint queda documentado y probable sin trabajo extra.
- ✅ **Validación incorporada:** menos errores y menos código de control manual.
- ✅ **Ligero y rápido:** ideal para un MVP que debe poder levantarse en minutos.
- ✅ **Mismo lenguaje que el ecosistema de datos:** el día que se incorpore un modelo de ML (scikit-learn),
  se integra directamente en la API sin cambiar de tecnología.

---

## 🏗️ Arquitectura

```
┌──────────────────────┐     HTTP / JSON      ┌──────────────────────┐      SQL      ┌──────────────────┐
│      FRONTEND        │ ───────────────────► │       BACKEND        │ ────────────► │    PostgreSQL    │
│  HTML + Tailwind CSS │                      │  FastAPI + Uvicorn   │               │  (localhost)     │
│  + JavaScript        │ ◄─────────────────── │  Regla de riesgo     │ ◄──────────── │  estudiantes     │
│  http://localhost:5500                      │  http://localhost:8000│              │  tutorias        │
└──────────────────────┘                      └──────────┬───────────┘               └──────────────────┘
                                                         │
                                                         ▼
                                            Swagger UI  →  /docs
                                            ReDoc       →  /redoc
```

## 🗄️ Modelo de datos

```
estudiantes                           tutorias
───────────────────────────           ───────────────────────────
id (PK)                               id (PK)
codigo (único)                        estudiante_id (FK → estudiantes.id)
nombre                                tipo
carrera                               observacion
semestre                              fecha
promedio  (sobre 10)
asistencia (%)
materias_reprobadas
cuotas_atrasadas
```

> Todos los datos son **ficticios** y se generan con `seed.py` (60 estudiantes, 6 carreras).

## 🧮 Cómo se calcula el riesgo hoy

El MVP usa una **regla ponderada transparente** (puntaje de 0 a 100):

| Factor | Peso | Se normaliza entre… |
|---|---|---|
| Promedio de notas | 35 % | 8.0 (sin riesgo) y 4.0 (riesgo máximo) |
| Asistencia | 30 % | 90 % (sin riesgo) y 50 % (riesgo máximo) |
| Materias reprobadas | 20 % | 0 y 3 |
| Cuotas atrasadas | 15 % | 0 y 3 |

**Niveles:** Bajo (0–24) · Medio (25–49) · Alto (50–100).

Es una regla **definida por criterio experto**, no aprendida de datos reales. Es útil para validar el
flujo de trabajo y para explicar el puntaje, pero **no es un modelo predictivo**. La siguiente sección
explica cómo evolucionar hacia uno.

---

## 📁 Estructura del proyecto

```
uisrael-alerta-temprana/
├── README.md
├── backend/
│   ├── requirements.txt     # Dependencias (entorno virtual, sin Docker)
│   ├── db.py                # Conexión a PostgreSQL
│   ├── seed.py              # Crea la BD, las tablas y datos ficticios
│   └── main.py              # API FastAPI + regla de riesgo
└── frontend/
    └── index.html           # Panel web (Tailwind CSS + JavaScript)
```

## 🚀 Instalación y ejecución

### Requisitos

- Python 3.10 o superior
- PostgreSQL en `localhost:5432` con usuario `postgres` y clave `172107` (credenciales de **ejemplo**)

### 1) Backend (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python seed.py
uvicorn main:app --reload --port 8000
```

`seed.py` crea la base `uisrael_alerta`, las tablas y los datos ficticios.
En Linux/Mac, activa el entorno con `source .venv/bin/activate`.

### 2) Frontend (otra terminal)

```powershell
cd frontend
python -m http.server 5500
```

### 3) Abrir

| Qué | URL |
|---|---|
| 🖥️ Aplicación | http://localhost:5500 |
| 📘 Swagger UI (documentación interactiva) | http://localhost:8000/docs |
| 📕 ReDoc | http://localhost:8000/redoc |

### Problemas comunes

| Problema | Solución |
|---|---|
| `password authentication failed` | Define tu clave: `$env:DB_PASSWORD="tu_clave"` antes de ejecutar `seed.py` y `uvicorn` |
| PowerShell bloquea el script de activación | `Set-ExecutionPolicy -Scope Process Bypass` |
| El panel muestra "No se pudo conectar con la API" | Verifica que `uvicorn` esté corriendo en el puerto 8000 |
| Puerto ocupado | Cambia `--port 8000` y actualiza la constante `API` en `frontend/index.html` |

---

## 🔗 Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/resumen` | Indicadores: total, riesgo alto/medio/bajo y tutorías |
| `GET` | `/api/carreras` | Catálogo de carreras |
| `GET` | `/api/estudiantes?carrera=&nivel=` | Estudiantes con puntaje, nivel y motivos de riesgo |
| `POST` | `/api/estudiantes/{id}/tutorias` | Registra una tutoría para el estudiante |

Ejemplo de respuesta de `GET /api/estudiantes`:

```json
{
  "id": 12,
  "codigo": "UI-0012",
  "nombre": "Kevin Vera Mena",
  "carrera": "Psicología",
  "promedio": 5.4,
  "asistencia": 61.0,
  "riesgo": 72,
  "nivel": "Alto",
  "motivos": ["Promedio bajo", "Asistencia baja", "Cuotas atrasadas"]
}
```

---

## 🤖 Evolución a Machine Learning

### ¿Por qué usar un modelo en este escenario?

La regla actual tiene límites que un modelo supervisado puede superar:

1. **Los pesos son opiniones, no evidencia.** Un modelo aprende de los datos históricos qué señales
   realmente anticiparon el abandono en *esta* institución.
2. **Captura interacciones.** Una asistencia del 75 % puede ser irrelevante para un estudiante con
   buenas notas, pero crítica si además tiene cuotas atrasadas. Una suma ponderada no lo ve.
3. **Entrega probabilidades calibradas.** "Este estudiante tiene 68 % de probabilidad de abandonar"
   es más accionable que un puntaje arbitrario de 0–100.
4. **Permite medir y mejorar.** Se puede evaluar objetivamente si el sistema acierta y compararlo
   contra la regla actual.
5. **Escala.** Con miles de estudiantes y más variables, la priorización manual deja de funcionar.

> ⚠️ **Importante:** con los datos ficticios de este MVP **no tiene sentido entrenar un modelo**: las
> etiquetas no corresponden a abandonos reales. El modelo requiere datos históricos reales y anonimizados.

### Problema de ML

**Clasificación binaria supervisada.** Para cada estudiante y período, predecir:

> ¿Abandonará (o no se matriculará) en el **siguiente período académico**? → `1 = abandona`, `0 = continúa`

**Variables candidatas:** promedio y su tendencia entre períodos, asistencia, materias reprobadas,
créditos aprobados vs. matriculados, mora en pagos, semestre, carrera, modalidad, becas, edad,
interacción con el campus virtual y número de tutorías previas.

### Modelos recomendados (en orden de adopción)

| # | Modelo | Por qué |
|---|---|---|
| 1 | **Regresión logística** | *Baseline* simple y explicable. Establece el piso que cualquier modelo más complejo debe superar |
| 2 | **Random Forest** | Captura relaciones no lineales con poco ajuste y es robusto |
| 3 | **Gradient Boosting** (XGBoost / LightGBM / `HistGradientBoostingClassifier`) | Suele dar el mejor rendimiento en datos tabulares como estos |

**Recomendación:** partir con regresión logística como línea base y avanzar a **Gradient Boosting** solo
si mejora de forma consistente. Para datos tabulares de este tamaño no se justifica *deep learning*.

### 📏 Métrica de evaluación recomendada

#### ❌ Por qué NO usar *accuracy*

La deserción es un evento **minoritario** (por ejemplo, 15–25 % de los estudiantes). Un modelo que
prediga "nadie abandona" tendría 75–85 % de *accuracy* y sería **completamente inútil**, porque no
detecta a ningún estudiante en riesgo.

#### ✅ Métricas principales

| Métrica | Qué mide | Por qué es adecuada aquí |
|---|---|---|
| **Recall (sensibilidad) de la clase "abandona"** | De todos los que realmente abandonan, ¿a cuántos detecté? | Un **falso negativo es el error más costoso**: un estudiante en riesgo que nadie atendió |
| **Precision** | De los que marqué en riesgo, ¿cuántos realmente abandonan? | Evita saturar a los tutores con falsas alarmas |
| **F2-score** | Media armónica que **pondera más el recall** que la precision | Refleja que perder a un estudiante cuesta más que una tutoría innecesaria |
| **PR-AUC** (Average Precision) | Calidad del ranking en datos desbalanceados | Más informativa que ROC-AUC cuando la clase positiva es rara |
| **Recall@k / Precision@k** | Desempeño dentro de los *k* estudiantes mejor rankeados | Los tutores tienen **capacidad limitada** (por ejemplo, atender a 50 estudiantes al mes) |

> **Métrica guía propuesta: Recall de la clase "abandona" sujeto a una precisión mínima aceptable
> (o F2-score), complementada con PR-AUC y Recall@k.**
>
> Razón de negocio: el costo de **no detectar** a un estudiante en riesgo (pérdida de matrícula y
> trayectoria interrumpida) es mayor que el costo de una **tutoría adicional**. Por eso se prioriza
> el recall, sin dejar que la precisión caiga tanto que el equipo de tutores se sature.

#### Buenas prácticas de validación

- **Partición temporal:** entrenar con cohortes pasadas y evaluar con la cohorte más reciente, igual
  que en producción. Una partición aleatoria infla los resultados.
- **Evitar fuga de datos (*data leakage*):** usar solo información disponible *antes* del momento de
  la predicción.
- **Ajustar el umbral de decisión:** no usar 0.5 por defecto; elegirlo según la capacidad de tutoría.
- **Calibración** (Brier score): que "70 %" signifique realmente ~70 %.
- **Explicabilidad** (coeficientes o SHAP): mostrar al tutor *por qué* el modelo marcó a un estudiante.
- **Equidad:** revisar que el recall no sea sistemáticamente menor para ciertos grupos (carrera,
  modalidad, beca, género).
- **Comparar contra la regla actual:** el modelo debe demostrar que mejora al *baseline*.

### Ejemplo de entrenamiento (referencial)

```python
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, fbeta_score, recall_score
import joblib

df = pd.read_csv("historico_anonimizado.csv")   # datos reales, anonimizados
X = df[["promedio", "asistencia", "materias_reprobadas", "cuotas_atrasadas", "semestre"]]
y = df["abandono_siguiente_periodo"]

# Partición TEMPORAL: pasado para entrenar, período más reciente para evaluar
entrenamiento = df["periodo"] < "2025-2"
modelo = HistGradientBoostingClassifier(class_weight="balanced", random_state=42)
modelo.fit(X[entrenamiento], y[entrenamiento])

prob = modelo.predict_proba(X[~entrenamiento])[:, 1]
pred = prob >= 0.35                                # umbral ajustado, no 0.5

print("PR-AUC :", average_precision_score(y[~entrenamiento], prob))
print("Recall :", recall_score(y[~entrenamiento], pred))
print("F2     :", fbeta_score(y[~entrenamiento], pred, beta=2))

joblib.dump(modelo, "modelo_desercion.joblib")
```

### Cómo se integraría a este proyecto

Solo cambia la función `calcular_riesgo` en `backend/main.py`: en lugar de la suma ponderada, carga
el modelo con `joblib` y usa `predict_proba`. **El frontend y los endpoints no cambian.**

```python
modelo = joblib.load("modelo_desercion.joblib")

def calcular_riesgo(e):
    prob = modelo.predict_proba([[e["promedio"], e["asistencia"],
                                  e["materias_reprobadas"], e["cuotas_atrasadas"],
                                  e["semestre"]]])[0][1]
    score = round(prob * 100)
    ...
```

---

## 🔒 Consideraciones éticas y de privacidad

- **Datos personales:** un sistema real trata datos personales y académicos de estudiantes; debe
  cumplir la normativa de protección de datos aplicable (en Ecuador, la Ley Orgánica de Protección de
  Datos Personales), con minimización de datos, control de accesos y finalidad clara.
- **Humano en el circuito:** el puntaje **apoya** la decisión del tutor, no la reemplaza.
- **Uso de apoyo, no sanción:** el objetivo es ofrecer ayuda oportuna, nunca estigmatizar ni limitar
  oportunidades al estudiante.
- **Transparencia:** cada alerta muestra sus motivos.
- **Seguridad de la demo:** las credenciales de ejemplo en `db.py` son solo para uso local; en un
  entorno real se gestionan con variables de entorno o un gestor de secretos.

## 🛣️ Limitaciones y hoja de ruta

**Limitaciones actuales del MVP**

- Datos ficticios y volumen pequeño (60 estudiantes).
- Riesgo calculado con regla ponderada, no con un modelo entrenado.
- Sin autenticación ni roles.
- Sin integración con sistemas académicos reales.

**Siguientes pasos**

- [ ] Autenticación y roles (tutor, coordinador, bienestar estudiantil)
- [ ] Integración con datos académicos y financieros reales (anonimizados)
- [ ] Modelo de ML con evaluación temporal y comparación contra la regla actual
- [ ] Explicabilidad por estudiante (SHAP) en el panel
- [ ] Seguimiento de resultados: ¿la tutoría redujo el riesgo?
- [ ] Notificaciones automáticas al tutor responsable
- [ ] Pruebas automatizadas y despliegue

---

<div align="center">

**Prototipo demostrativo con datos ficticios · Desarrollado por Diego Vallejo**

</div>
