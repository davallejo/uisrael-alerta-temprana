"""Crea la base de datos, las tablas y carga datos FICTICIOS de demostración."""
import random

import psycopg2
from psycopg2.extras import execute_values

from db import DB_CONFIG

random.seed(2026)

NOMBRES = ["Camila", "Mateo", "Valentina", "Sebastián", "Daniela", "Andrés", "Paola", "Kevin",
           "Gabriela", "Joel", "Samantha", "Diego", "Karen", "Bryan", "Lucía", "Erick",
           "Nicole", "David", "Mishell", "Anthony"]
APELLIDOS = ["Andrade", "Cevallos", "Guerrero", "Mena", "Paredes", "Salazar", "Toapanta", "Vera",
             "Yánez", "Zambrano", "Chiliquinga", "Ortiz", "Montalvo", "Revelo", "Játiva", "Naranjo"]
CARRERAS = ["Sistemas de Información", "Electrónica y Automatización", "Administración de Empresas",
            "Psicología", "Diseño Gráfico", "Turismo"]

# Rangos por perfil: promedio (sobre 10), asistencia (%), materias reprobadas, cuotas atrasadas
PERFILES = {
    "bajo":  dict(prom=(7.8, 9.7), asis=(88, 100), rep=(0, 0), cuo=(0, 0)),
    "medio": dict(prom=(6.5, 7.7), asis=(70, 86),  rep=(0, 2), cuo=(0, 2)),
    "alto":  dict(prom=(4.5, 6.5), asis=(50, 72),  rep=(1, 3), cuo=(1, 3)),
}

DDL = """
DROP TABLE IF EXISTS tutorias;
DROP TABLE IF EXISTS estudiantes;

CREATE TABLE estudiantes (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(12) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    carrera VARCHAR(60) NOT NULL,
    semestre INT NOT NULL,
    promedio NUMERIC(4,2) NOT NULL,
    asistencia NUMERIC(5,1) NOT NULL,
    materias_reprobadas INT NOT NULL DEFAULT 0,
    cuotas_atrasadas INT NOT NULL DEFAULT 0
);

CREATE TABLE tutorias (
    id SERIAL PRIMARY KEY,
    estudiante_id INT NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    tipo VARCHAR(40) NOT NULL,
    observacion VARCHAR(300) DEFAULT '',
    fecha TIMESTAMP DEFAULT NOW()
);
"""


def crear_base_si_no_existe():
    cfg = {**DB_CONFIG, "dbname": "postgres"}
    conn = psycopg2.connect(**cfg)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG["dbname"],))
        if not cur.fetchone():
            cur.execute(f'CREATE DATABASE "{DB_CONFIG["dbname"]}"')
            print(f"Base de datos '{DB_CONFIG['dbname']}' creada.")
    conn.close()


def main():
    crear_base_si_no_existe()
    filas = []
    for i in range(1, 61):
        p = PERFILES[random.choices(list(PERFILES), weights=[60, 25, 15])[0]]
        nombre = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
        filas.append((
            f"UI-{i:04d}", nombre, random.choice(CARRERAS), random.randint(1, 8),
            round(random.uniform(*p["prom"]), 2), round(random.uniform(*p["asis"]), 1),
            random.randint(*p["rep"]), random.randint(*p["cuo"]),
        ))

    conn = psycopg2.connect(**DB_CONFIG)
    with conn, conn.cursor() as cur:
        cur.execute(DDL)
        execute_values(cur, """
            INSERT INTO estudiantes
            (codigo, nombre, carrera, semestre, promedio, asistencia, materias_reprobadas, cuotas_atrasadas)
            VALUES %s""", filas)
        cur.execute("""
            INSERT INTO tutorias (estudiante_id, tipo, observacion)
            SELECT id, 'Tutoría académica', 'Seguimiento inicial (dato ficticio)'
            FROM estudiantes WHERE promedio < 6 LIMIT 3""")
    conn.close()
    print(f"Listo: {len(filas)} estudiantes ficticios cargados.")


if __name__ == "__main__":
    main()
