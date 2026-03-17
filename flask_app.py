from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db, init_db
from datetime import datetime, date, timedelta
import os
import subprocess

app = Flask(__name__)
app.secret_key = 'dixi_viajes_secret_key'

# --- Helpers ---

def mes_actual():
    """Devuelve el mes actual en formato YYYY-MM."""
    return date.today().strftime('%Y-%m')


def nombre_mes(mes_str):
    """Convierte '2026-03' a 'Marzo 2026'."""
    meses = {
        '01': 'Enero', '02': 'Febrero', '03': 'Marzo',
        '04': 'Abril', '05': 'Mayo', '06': 'Junio',
        '07': 'Julio', '08': 'Agosto', '09': 'Septiembre',
        '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
    }
    partes = mes_str.split('-')
    return f"{meses.get(partes[1], partes[1])} {partes[0]}"


def mes_anterior(mes_str):
    """Devuelve el mes anterior a mes_str."""
    partes = mes_str.split('-')
    anio, mes = int(partes[0]), int(partes[1])
    if mes == 1:
        return f"{anio - 1}-12"
    return f"{anio}-{mes - 1:02d}"


def mes_siguiente(mes_str):
    """Devuelve el mes siguiente a mes_str."""
    partes = mes_str.split('-')
    anio, mes = int(partes[0]), int(partes[1])
    if mes == 12:
        return f"{anio + 1}-01"
    return f"{anio}-{mes + 1:02d}"


@app.template_filter('formato_pesos')
def formato_pesos(valor):
    """Formatea un número con puntos como separadores de miles (ej: 25.000)."""
    try:
        return "{:,.0f}".format(valor).replace(',', '.')
    except (ValueError, TypeError):
        return valor


@app.template_filter('formato_fecha')
def formato_fecha(fecha_str):
    """Convierte YYYY-MM-DD a DD-MM-YYYY."""
    if not fecha_str:
        return ""
    try:
        # Intentar parsear formato YYYY-MM-DD que guarda SQLite
        dt = datetime.strptime(fecha_str, '%Y-%m-%d')
        return dt.strftime('%d-%m-%Y')
    except (ValueError, TypeError):
        return fecha_str


@app.template_filter('formato_dia_amigable')
def formato_dia_amigable(fecha_str):
    """Convierte YYYY-MM-DD a 'Lunes 16'."""
    if not fecha_str:
        return ""
    try:
        dt = datetime.strptime(fecha_str, '%Y-%m-%d')
        dias = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        dia_nombre = dias.get(dt.strftime('%A'), dt.strftime('%A'))
        return f"{dia_nombre} {dt.day}"
    except (ValueError, TypeError):
        return fecha_str


@app.template_filter('cap_palabras')
def cap_palabras(s):
    """Capitaliza cada palabra de un string (Title Case)."""
    if not s:
        return ""
    return ' '.join(word.capitalize() for word in s.split())


# --- Rutas ---

@app.route('/')
def index():
    return redirect(url_for('pagos', mes=mes_actual()))


# =====================
# CLIENTES
# =====================

@app.route('/clientes')
def clientes():
    db = get_db()
    lista = db.execute('SELECT * FROM clientes ORDER BY activo DESC, nombre ASC').fetchall()

    # Contar viajes activos por cliente
    clientes_info = []
    for c in lista:
        cant_viajes = db.execute(
            'SELECT COUNT(*) as total FROM viajes WHERE cliente_id = ? AND activo = 1',
            (c['id'],)
        ).fetchone()['total']
        clientes_info.append({
            'id': c['id'],
            'nombre': c['nombre'],
            'activo': c['activo'],
            'cant_viajes': cant_viajes
        })

    db.close()
    return render_template('clientes.html', clientes=clientes_info)


@app.route('/clientes/nuevo', methods=['POST'])
def crear_cliente():
    nombre = request.form.get('nombre', '').strip()

    if nombre:
        db = get_db()
        db.execute('INSERT INTO clientes (nombre) VALUES (?)', (nombre,))
        db.commit()
        db.close()

    return redirect(url_for('clientes'))


@app.route('/clientes/<int:id>/editar', methods=['POST'])
def editar_cliente(id):
    nombre = request.form.get('nombre', '').strip()

    if nombre:
        db = get_db()
        db.execute('UPDATE clientes SET nombre = ? WHERE id = ?', (nombre, id))
        db.commit()
        db.close()

    return redirect(url_for('clientes'))


@app.route('/clientes/<int:id>/toggle', methods=['POST'])
def toggle_cliente(id):
    db = get_db()
    cliente = db.execute('SELECT activo FROM clientes WHERE id = ?', (id,)).fetchone()
    if cliente:
        nuevo_estado = 0 if cliente['activo'] else 1
        db.execute('UPDATE clientes SET activo = ? WHERE id = ?', (nuevo_estado, id))
        db.commit()
    db.close()
    return redirect(url_for('clientes'))


# =====================
# VIAJES
# =====================

@app.route('/viajes')
def viajes():
    db = get_db()

    # Mostrar viajes recientes (últimos 30 días)
    lista = db.execute('''
        SELECT v.*, c.nombre as cliente_nombre
        FROM viajes v
        JOIN clientes c ON v.cliente_id = c.id
        WHERE v.fecha_creacion >= date('now', '-30 days')
        ORDER BY v.fecha_creacion DESC, v.id DESC
    ''').fetchall()

    # Clientes activos para el formulario
    clientes_activos = db.execute(
        'SELECT id, nombre FROM clientes WHERE activo = 1 ORDER BY nombre ASC'
    ).fetchall()

    # Obtener el último viaje de cada cliente para autocompletar
    ultimos_viajes = {}
    for c in clientes_activos:
        ultimo = db.execute('''
            SELECT salida, destino, monto 
            FROM viajes 
            WHERE cliente_id = ? 
            ORDER BY id DESC LIMIT 1
        ''', (c['id'],)).fetchone()
        if ultimo:
            ultimos_viajes[c['id']] = {
                'salida': ultimo['salida'],
                'destino': ultimo['destino'],
                'monto': ultimo['monto']
            }

    db.close()
    return render_template('viajes.html', 
                           viajes=lista, 
                           clientes=clientes_activos,
                           ultimos_viajes=ultimos_viajes)


@app.route('/viajes/nuevo', methods=['POST'])
def crear_viaje():
    cliente_id = request.form.get('cliente_id', '').strip()
    salida = request.form.get('salida', '').strip()
    destino = request.form.get('destino', '').strip()
    monto = request.form.get('monto', '0').strip()

    if cliente_id and salida and destino:
        try:
            monto_num = float(monto)
        except ValueError:
            monto_num = 0

        db = get_db()
        cursor = db.cursor()
        
        # Insertar el viaje (evento único)
        cursor.execute(
            'INSERT INTO viajes (cliente_id, salida, destino, monto) VALUES (?, ?, ?, ?)',
            (int(cliente_id), salida, destino, monto_num)
        )
        viaje_id = cursor.lastrowid
        
        # Crear el pago para el mes actual inmediatamente
        db.execute(
            'INSERT INTO pagos (viaje_id, mes, monto, pagado) VALUES (?, ?, ?, 0)',
            (viaje_id, mes_actual(), monto_num)
        )
        
        db.commit()
        db.close()
        
        flash('✅ Viaje agregado correctamente')

    return redirect(url_for('viajes'))


@app.route('/viajes/<int:id>/editar', methods=['POST'])
def editar_viaje(id):
    salida = request.form.get('salida', '').strip()
    destino = request.form.get('destino', '').strip()
    monto = request.form.get('monto', '0').strip()

    if salida and destino:
        try:
            monto_num = float(monto)
        except ValueError:
            monto_num = 0

        db = get_db()
        db.execute(
            'UPDATE viajes SET salida = ?, destino = ?, monto = ? WHERE id = ?',
            (salida, destino, monto_num, id)
        )
        # Actualizar el monto en pagos NO pagados de este viaje
        db.execute(
            'UPDATE pagos SET monto = ? WHERE viaje_id = ? AND pagado = 0',
            (monto_num, id)
        )
        db.commit()
        db.close()

    return redirect(url_for('viajes'))


@app.route('/viajes/<int:id>/toggle', methods=['POST'])
def toggle_viaje(id):
    db = get_db()
    viaje = db.execute('SELECT activo FROM viajes WHERE id = ?', (id,)).fetchone()
    if viaje:
        nuevo_estado = 0 if viaje['activo'] else 1
        db.execute('UPDATE viajes SET activo = ? WHERE id = ?', (nuevo_estado, id))
        db.commit()
    db.close()
    return redirect(url_for('viajes'))


@app.route('/viajes/<int:id>/eliminar', methods=['POST'])
def eliminar_viaje(id):
    db = get_db()
    # Borrar el pago asociado (para que desaparezca de la lista de ese mes)
    db.execute('DELETE FROM pagos WHERE viaje_id = ?', (id,))
    # Borrar el viaje
    db.execute('DELETE FROM viajes WHERE id = ?', (id,))
    db.commit()
    db.close()
    return redirect(url_for('viajes'))


# =====================
# PAGOS
# =====================

@app.route('/pagos')
def pagos():
    mes = request.args.get('mes', mes_actual())

    db = get_db()

    # Ya no generamos pagos automáticamente. 
    # El usuario los anota uno por uno en la pestaña Viajes.

    # Obtener pagos del mes (mostramos todos los existentes, incluso si el viaje se desactivó después)
    pagos_mes = db.execute('''
        SELECT p.*, v.salida, v.destino, v.monto as viaje_monto, v.fecha_creacion, c.nombre as cliente_nombre
        FROM pagos p
        JOIN viajes v ON p.viaje_id = v.id
        JOIN clientes c ON v.cliente_id = c.id
        WHERE p.mes = ?
        ORDER BY v.fecha_creacion DESC, v.id DESC
    ''', (mes,)).fetchall()

    # Calcular resumen
    total = sum(p['monto'] for p in pagos_mes)
    cobrado = sum(p['monto'] for p in pagos_mes if p['pagado'])
    pendiente = total - cobrado

    db.close()

    return render_template('pagos.html',
                           pagos=pagos_mes,
                           mes=mes,
                           nombre_mes=nombre_mes(mes),
                           mes_ant=mes_anterior(mes),
                           mes_sig=mes_siguiente(mes),
                           total=total,
                           cobrado=cobrado,
                           pendiente=pendiente)


@app.route('/pagos/toggle', methods=['POST'])
def toggle_pago():
    pago_id = request.form.get('pago_id')
    mes = request.form.get('mes', mes_actual())

    db = get_db()
    pago = db.execute('SELECT pagado FROM pagos WHERE id = ?', (pago_id,)).fetchone()
    if pago:
        nuevo_estado = 0 if pago['pagado'] else 1
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M') if nuevo_estado else None
        db.execute('UPDATE pagos SET pagado = ?, fecha_pago = ? WHERE id = ?',
                   (nuevo_estado, fecha, pago_id))
        db.commit()
        
        if nuevo_estado:
            flash('💰 Pago registrado')
        else:
            flash('↩️ Pago desmarcado')
    db.close()

    return redirect(url_for('pagos', mes=mes))


@app.route('/pagos/update_turno', methods=['POST'])
def update_turno():
    data = request.get_json()
    pago_id = data.get('pago_id')
    nuevo_turno = data.get('nuevo_turno')

    if pago_id and nuevo_turno:
        db = get_db()
        db.execute('UPDATE pagos SET turno = ? WHERE id = ?', (nuevo_turno, pago_id))
        db.commit()
        db.close()
        return {"status": "success"}, 200
    
    return {"status": "error"}, 400


# =====================
# HISTORIAL
# =====================

@app.route('/historial')
def historial():
    db = get_db()

    meses = db.execute('''
        SELECT DISTINCT mes FROM pagos ORDER BY mes DESC
    ''').fetchall()

    resumen_meses = []
    for m in meses:
        mes_val = m['mes']
        datos = db.execute('''
            SELECT p.monto, p.pagado
            FROM pagos p
            JOIN viajes v ON p.viaje_id = v.id
            WHERE p.mes = ?
        ''', (mes_val,)).fetchall()

        total = sum(d['monto'] for d in datos)
        cobrado = sum(d['monto'] for d in datos if d['pagado'])
        cantidad = len(datos)
        pagados = sum(1 for d in datos if d['pagado'])

        resumen_meses.append({
            'mes': mes_val,
            'nombre': nombre_mes(mes_val),
            'total': total,
            'cobrado': cobrado,
            'pendiente': total - cobrado,
            'cantidad': cantidad,
            'pagados': pagados
        })

    db.close()

    return render_template('historial.html', meses=resumen_meses)


# --- Ruta de Despliegue Automático ---

@app.route('/deploy', methods=['POST'])
def deploy():
    """Ruta para recibir webhooks de GitHub y actualizar la app."""
    try:
        # 0. Asegurar que la base de datos esté al día
        init_db()
        
        # 1. Pull de los cambios desde GitHub
        pull_output = subprocess.check_output(['git', 'pull', 'origin', 'main'], stderr=subprocess.STDOUT).decode('utf-8')
        
        # 2. Reiniciar el servidor (específico de PythonAnywhere)
        # Esto funciona 'tocando' el archivo WSGI
        # Ajustar el nombre de usuario si es diferente a 'gestorviajes'
        wsgi_path = '/var/www/gestorviajes_pythonanywhere_com_wsgi.py'
        if os.path.exists(wsgi_path):
            os.utime(wsgi_path, None)
            restart_msg = "Servidor reiniciado."
        else:
            restart_msg = "WSGI no encontrado (¿Estás en local?)."

        return {
            "status": "success",
            "message": f"Despliegue completado. {restart_msg}",
            "git_output": pull_output
        }, 200
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": str(e.output.decode('utf-8'))
        }, 500
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }, 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
