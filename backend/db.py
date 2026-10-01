"""Conexión a PostgreSQL (localhost). Valores de DEMO; se pueden sobrescribir con variables de entorno."""
import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "172107"),
    "dbname": os.getenv("DB_NAME", "uisrael_alerta"),
}


@contextmanager
def cursor():
    """Entrega un cursor, confirma los cambios y cierra la conexión al terminar."""
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    try:
        with conn:
            with conn.cursor() as cur:
                yield cur
    finally:
        conn.close()
