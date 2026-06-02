import sqlite3
import random
from datetime import datetime, timedelta
import os

def init_demo_db():
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, activo INTEGER NOT NULL DEFAULT 1)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS viajes (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER NOT NULL, salida TEXT NOT NULL, destino TEXT NOT NULL, monto REAL NOT NULL DEFAULT 0, activo INTEGER NOT NULL DEFAULT 1, fecha_creacion TEXT NOT NULL DEFAULT (date('now')), hora TEXT DEFAULT '', FOREIGN KEY (cliente_id) REFERENCES clientes(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pagos (id INTEGER PRIMARY KEY AUTOINCREMENT, viaje_id INTEGER NOT NULL, mes TEXT NOT NULL, monto REAL NOT NULL DEFAULT 0, pagado INTEGER NOT NULL DEFAULT 0, fecha_pago TEXT, nota TEXT DEFAULT '', turno TEXT DEFAULT 'sin_asignar', FOREIGN KEY (viaje_id) REFERENCES viajes(id), UNIQUE(viaje_id, mes))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, monto REAL NOT NULL, categoria TEXT NOT NULL DEFAULT 'Otros', descripcion TEXT DEFAULT '')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ingresos_manuales (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, monto REAL NOT NULL, categoria TEXT NOT NULL DEFAULT 'Otros', descripcion TEXT DEFAULT '')''')
    conn.commit()
    conn.close()

def seed_database():
    init_demo_db()
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM pagos')
    cursor.execute('DELETE FROM viajes')
    cursor.execute('DELETE FROM clientes')
    cursor.execute('DELETE FROM gastos')
    cursor.execute('DELETE FROM ingresos_manuales')

    nombres_ficticios = [
        "Juan Pérez", "María Gómez", "Lucas Torres", "Sofía Martínez",
        "Diego Silva", "Valentina Rojas", "Empresa Tech S.A.", "Colegio San José"
    ]
    lugares = ["Casa", "Colegio", "Oficina", "Aeropuerto", "Terminal de Ómnibus", "Shopping", "Centro", "Hospital", "Club", "Gimnasio"]

    print("Generando clientes...")
    cliente_ids = []
    for nombre in nombres_ficticios:
        cursor.execute("INSERT INTO clientes (nombre, activo) VALUES (?, 1)", (nombre,))
        cliente_ids.append(cursor.lastrowid)

    print("Generando viajes y pagos...")
    fecha_actual = datetime.now()

    for i in range(45):
        c_id = random.choice(cliente_ids)
        salida = random.choice(lugares)
        destino = random.choice([l for l in lugares if l != salida])
        dias_restar = random.randint(0, 60)
        fecha_viaje = fecha_actual - timedelta(days=dias_restar)
        fecha_str = fecha_viaje.strftime("%Y-%m-%d")
        hora_str = f"{random.randint(6, 22):02d}:{random.choice(['00', '15', '30', '45'])}"
        monto = random.randint(1500, 8500)
        pagado = 1 if random.random() > 0.35 else 0
        mes_viaje = fecha_viaje.strftime("%Y-%m")

        fecha_pago = None
        if pagado:
            dias_despues = random.randint(0, 3)
            fp = fecha_viaje + timedelta(days=dias_despues)
            fecha_pago = fp.strftime("%Y-%m-%d %H:%M")

        cursor.execute("""
            INSERT INTO viajes (cliente_id, fecha_creacion, hora, salida, destino, monto, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (c_id, fecha_str, hora_str, salida, destino, monto))
        vid = cursor.lastrowid
        cursor.execute(
            "INSERT INTO pagos (viaje_id, mes, monto, pagado, fecha_pago) VALUES (?, ?, ?, ?, ?)",
            (vid, mes_viaje, monto, pagado, fecha_pago)
        )

    print("Generando gastos...")
    gastos_por_mes = [
        # (categoria, descripcion, monto_min, monto_max, veces_por_mes)
        ('Alquiler',    'Alquiler departamento',  60000, 70000, 1),
        ('Servicios',   'Internet y celular',       4000,  6000, 1),
        ('Servicios',   'Luz y gas',                3000,  7000, 1),
        ('Comida',      'Supermercado',             8000, 18000, 2),
        ('Comida',      'Delivery',                 1500,  4000, 3),
        ('Transporte',  'Nafta',                    5000,  9000, 2),
        ('Salud',       'Prepaga',                  8000, 12000, 1),
        ('Otros',       '',                         1000,  5000, 1),
    ]

    for mes_offset in range(3):
        fecha_ref = fecha_actual.replace(day=1) - timedelta(days=30 * mes_offset)
        for categoria, descripcion, monto_min, monto_max, veces in gastos_por_mes:
            for _ in range(veces):
                dia = random.randint(1, 28)
                fecha_gasto = fecha_ref.replace(day=dia)
                if fecha_gasto > fecha_actual:
                    fecha_gasto = fecha_actual
                cursor.execute(
                    "INSERT INTO gastos (fecha, monto, categoria, descripcion) VALUES (?, ?, ?, ?)",
                    (fecha_gasto.strftime("%Y-%m-%d"), random.randint(monto_min, monto_max), categoria, descripcion)
                )

    print("Generando ingresos manuales...")
    ingresos_extra = [
        ('Freelance', 'Diseño web cliente externo', 25000, 50000),
        ('Alquiler',  'Alquiler cochera',            8000, 10000),
        ('Otros',     'Venta artículos',             3000,  8000),
    ]

    for mes_offset in range(3):
        fecha_ref = fecha_actual.replace(day=1) - timedelta(days=30 * mes_offset)
        for categoria, descripcion, monto_min, monto_max in ingresos_extra:
            if random.random() > 0.3:
                dia = random.randint(1, 28)
                fecha_ing = fecha_ref.replace(day=dia)
                if fecha_ing > fecha_actual:
                    fecha_ing = fecha_actual
                cursor.execute(
                    "INSERT INTO ingresos_manuales (fecha, monto, categoria, descripcion) VALUES (?, ?, ?, ?)",
                    (fecha_ing.strftime("%Y-%m-%d"), random.randint(monto_min, monto_max), categoria, descripcion)
                )

    conn.commit()
    conn.close()
    print("¡Base demo.db llenada con éxito!")

if __name__ == "__main__":
    seed_database()
