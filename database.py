import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos.db')


def get_db():
    """Obtiene una conexión a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crea las tablas si no existen."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS viajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            salida TEXT NOT NULL,
            destino TEXT NOT NULL,
            monto REAL NOT NULL DEFAULT 0,
            activo INTEGER NOT NULL DEFAULT 1,
            fecha_creacion TEXT NOT NULL DEFAULT (date('now')),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')

    # Migración: agregar fecha_creacion si no existe (para DBs existentes)
    try:
        cursor.execute("ALTER TABLE viajes ADD COLUMN fecha_creacion TEXT DEFAULT ''")
        # Actualizar registros existentes que no tengan fecha
        cursor.execute("UPDATE viajes SET fecha_creacion = date('now') WHERE fecha_creacion = '' OR fecha_creacion IS NULL")
    except sqlite3.OperationalError:
        pass  # La columna ya existe

    # Migración: agregar hora si no existe
    try:
        cursor.execute("ALTER TABLE viajes ADD COLUMN hora TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # La columna ya existe

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            viaje_id INTEGER NOT NULL,
            mes TEXT NOT NULL,
            monto REAL NOT NULL DEFAULT 0,
            pagado INTEGER NOT NULL DEFAULT 0,
            fecha_pago TEXT,
            nota TEXT DEFAULT '',
            turno TEXT DEFAULT 'sin_asignar',
            FOREIGN KEY (viaje_id) REFERENCES viajes(id),
            UNIQUE(viaje_id, mes)
        )
    ''')

    # Migración: agregar turno si no existe (para DBs existentes)
    try:
        cursor.execute("ALTER TABLE pagos ADD COLUMN turno TEXT DEFAULT 'sin_asignar'")
    except sqlite3.OperationalError:
        pass  # La columna ya existe

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print("Base de datos inicializada correctamente.")
