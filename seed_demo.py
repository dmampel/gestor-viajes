import sqlite3
import random
from datetime import datetime, timedelta
import os

def init_demo_db():
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()
    # Crear tablas como en app
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, activo INTEGER NOT NULL DEFAULT 1)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS viajes (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER NOT NULL, salida TEXT NOT NULL, destino TEXT NOT NULL, monto REAL NOT NULL DEFAULT 0, activo INTEGER NOT NULL DEFAULT 1, fecha_creacion TEXT NOT NULL DEFAULT (date('now')), hora TEXT DEFAULT '', FOREIGN KEY (cliente_id) REFERENCES clientes(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pagos (id INTEGER PRIMARY KEY AUTOINCREMENT, viaje_id INTEGER NOT NULL, mes TEXT NOT NULL, monto REAL NOT NULL DEFAULT 0, pagado INTEGER NOT NULL DEFAULT 0, fecha_pago TEXT, nota TEXT DEFAULT '', turno TEXT DEFAULT 'sin_asignar', FOREIGN KEY (viaje_id) REFERENCES viajes(id), UNIQUE(viaje_id, mes))''')
    conn.commit()
    conn.close()

def seed_database():
    init_demo_db()
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM pagos')
    cursor.execute('DELETE FROM viajes')
    cursor.execute('DELETE FROM clientes')
    
    nombres_ficticios = ["Juan Pérez", "María Gómez", "Lucas Torres", "Sofía Martínez", "Diego Silva", "Valentina Rojas", "Empresa Tech S.A.", "Colegio San José"]
    lugares = ["Casa", "Colegio", "Oficina", "Aeropuerto", "Terminal de Ómnibus", "Shopping", "Centro", "Hospital", "Club", "Gimnasio"]

    print("Generando clientes...")
    cliente_ids = []
    for nombre in nombres_ficticios:
        cursor.execute("INSERT INTO clientes (nombre, activo) VALUES (?, 1)", (nombre,))
        cliente_ids.append(cursor.lastrowid)

    print("Generando historial de viajes (Demo)...")
    fecha_actual = datetime.now()
    
    for i in range(35):
        c_id = random.choice(cliente_ids)
        salida = random.choice(lugares)
        destino = random.choice([l for l in lugares if l != salida])
        dias_restar = random.randint(0, 30)
        fecha_viaje = (fecha_actual - timedelta(days=dias_restar))
        fecha_str = fecha_viaje.strftime("%Y-%m-%d")
        hora_str = f"{random.randint(6, 22):02d}:{random.choice(['00', '15', '30', '45'])}"
        monto = random.randint(1500, 8500)
        pagado = 1 if random.random() > 0.4 else 0
        mes_viaje = fecha_viaje.strftime("%Y-%m")

        cursor.execute("""
            INSERT INTO viajes (cliente_id, fecha_creacion, hora, salida, destino, monto, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (c_id, fecha_str, hora_str, salida, destino, monto))
        vid = cursor.lastrowid

        cursor.execute("INSERT INTO pagos (viaje_id, mes, monto, pagado) VALUES (?, ?, ?, ?)", (vid, mes_viaje, monto, pagado))

    conn.commit()
    conn.close()
    print("¡Base demo.db llenada con éxito!")

if __name__ == "__main__":
    seed_database()
