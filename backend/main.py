"""API de Alerta Temprana de Deserción Estudiantil (datos ficticios)."""
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from db import cursor

app = FastAPI(
    title="Alerta Temprana de Deserción · Universidad Israel",
    description="MVP demostrativo con datos ficticios. Desarrollado por Diego Vallejo.",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class TutoriaIn(BaseModel):
    tipo: str = Field(..., examples=["Tutoría académica"])
    observacion: str = Field("", max_length=300)


def calcular_riesgo(e: dict):
    """Regla ponderada (0-100). Reemplazable luego por un modelo de ML."""
    a = min(max((8 - e["promedio"]) / 4, 0), 1)
    s = min(max((90 - e["asistencia"]) / 40, 0), 1)
    r = min(e["materias_reprobadas"] / 3, 1)
    c = min(e["cuotas_atrasadas"] / 3, 1)
    score = round(100 * (0.35 * a + 0.30 * s + 0.20 * r + 0.15 * c))
    nivel = "Alto" if score >= 50 else "Medio" if score >= 25 else "Bajo"
    motivos = []
    if e["promedio"] < 7:
        motivos.append("Promedio bajo")
    if e["asistencia"] < 80:
        motivos.append("Asistencia baja")
    if e["materias_reprobadas"] > 0:
        motivos.append("Materias reprobadas")
    if e["cuotas_atrasadas"] > 0:
        motivos.append("Cuotas atrasadas")
    return score, nivel, motivos


def obtener_estudiantes(carrera: Optional[str] = None):
    sql = """SELECT e.*, (SELECT COUNT(*) FROM tutorias t WHERE t.estudiante_id = e.id) AS tutorias
             FROM estudiantes e"""
    params = ()
    if carrera:
        sql += " WHERE e.carrera = %s"
        params = (carrera,)
    with cursor() as cur:
        cur.execute(sql, params)
        filas = cur.fetchall()
    resultado = []
    for f in filas:
        e = dict(f)
        e["promedio"], e["asistencia"] = float(e["promedio"]), float(e["asistencia"])
        e["riesgo"], e["nivel"], e["motivos"] = calcular_riesgo(e)
        resultado.append(e)
    return sorted(resultado, key=lambda x: x["riesgo"], reverse=True)


@app.get("/", tags=["General"])
def inicio():
    return {"mensaje": "API activa. Documentación en /docs"}


@app.get("/api/carreras", tags=["Catálogos"])
def carreras():
    with cursor() as cur:
        cur.execute("SELECT DISTINCT carrera FROM estudiantes ORDER BY carrera")
        return [f["carrera"] for f in cur.fetchall()]


@app.get("/api/resumen", tags=["Indicadores"])
def resumen():
    est = obtener_estudiantes()
    with cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM tutorias")
        tutorias = cur.fetchone()["n"]
    return {
        "total": len(est),
        "alto": sum(e["nivel"] == "Alto" for e in est),
        "medio": sum(e["nivel"] == "Medio" for e in est),
        "bajo": sum(e["nivel"] == "Bajo" for e in est),
        "tutorias": tutorias,
    }


@app.get("/api/estudiantes", tags=["Estudiantes"])
def listar(carrera: Optional[str] = None,
           nivel: Optional[str] = Query(None, pattern="^(Alto|Medio|Bajo)$")):
    est = obtener_estudiantes(carrera)
    return [e for e in est if not nivel or e["nivel"] == nivel]


@app.post("/api/estudiantes/{estudiante_id}/tutorias", status_code=201, tags=["Tutorías"])
def registrar_tutoria(estudiante_id: int, datos: TutoriaIn):
    with cursor() as cur:
        cur.execute("SELECT id FROM estudiantes WHERE id = %s", (estudiante_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        cur.execute(
            "INSERT INTO tutorias (estudiante_id, tipo, observacion) VALUES (%s, %s, %s) RETURNING id, fecha",
            (estudiante_id, datos.tipo, datos.observacion),
        )
        return cur.fetchone()
