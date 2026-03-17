from app import app
from database import get_db

with app.test_request_context('/pagos?mes=2026-03'):
    try:
        from flask import g
        # Trigger the route
        with app.test_client() as client:
            response = client.get('/pagos?mes=2026-03')
            print(f"Status: {response.status_code}")
            if response.status_code == 500:
                # We can't easily get the stack trace here, but let's try to see if it crashes when we run the query manually
                db = get_db()
                pagos = db.execute('''
                    SELECT p.*, v.salida, v.destino, v.monto as viaje_monto, v.fecha_creacion, c.nombre as cliente_nombre
                    FROM pagos p
                    JOIN viajes v ON p.viaje_id = v.id
                    JOIN clientes c ON v.cliente_id = c.id
                    WHERE p.mes = '2026-03'
                ''').fetchall()
                print(f"Query returned {len(pagos)} rows")
    except Exception as e:
        import traceback
        print(traceback.format_exc())
