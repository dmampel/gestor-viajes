from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import get_db, init_db

# Inicializar Base de Datos al arrancar (incluyendo migraciones)
init_db()
from datetime import datetime, date, timedelta, timezone
import os
import subprocess

# Configuración de zona horaria (Argentina GMT-3)
ARG_TZ = timezone(timedelta(hours=-3))

def get_ahora():
    """Devuelve la fecha y hora actual en la zona horaria de Argentina."""
    return datetime.now(ARG_TZ)

app = Flask(__name__)
app.secret_key = 'dixi_viajes_secret_key'

ADMIN_PASSWORD = os.environ.get('SECRET_PASS', 'dixi2026')

@app.before_request
def require_login():
    allow_list = ['login', 'static', 'deploy']
    if request.endpoint not in allow_list and request.endpoint is not None:
        if not session.get('role'):
            return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'demo':
            session['role'] = 'demo'
            return redirect(url_for('index'))
        elif action == 'admin':
            password = request.form.get('password')
            if password == ADMIN_PASSWORD:
                session['role'] = 'admin'
                return redirect(url_for('index'))
            else:
                flash('Contraseña incorrecta')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Helpers ---

def mes_actual():
    """Devuelve el mes actual en formato YYYY-MM."""
    return get_ahora().strftime('%Y-%m')


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


@app.template_filter('formato_hora_12h')
def formato_hora_12h(hora_str):
    """Convierte HH:MM (24h) a HH:MM am/pm (12h)."""
    if not hora_str:
        return ""
    try:
        dt = datetime.strptime(hora_str, '%H:%M')
        return dt.strftime('%I:%M %p').lower()
    except (ValueError, TypeError):
        return hora_str


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
            SELECT salida, destino, monto, hora 
            FROM viajes 
            WHERE cliente_id = ? 
            ORDER BY id DESC LIMIT 1
        ''', (c['id'],)).fetchone()
        if ultimo:
            ultimos_viajes[c['id']] = {
                'salida': ultimo['salida'],
                'destino': ultimo['destino'],
                'monto': ultimo['monto'],
                'hora': ultimo['hora']
            }

    ahora = get_ahora()
    hoy_str = ahora.strftime('%Y-%m-%d')
    manana_str = (ahora + timedelta(days=1)).strftime('%Y-%m-%d')

    db.close()
    return render_template('viajes.html', 
                           viajes=lista, 
                           clientes=clientes_activos,
                           ultimos_viajes=ultimos_viajes,
                           hoy=hoy_str,
                           manana=manana_str)


@app.route('/viajes/nuevo', methods=['POST'])
def crear_viaje():
    cliente_id = request.form.get('cliente_id', '').strip()
    salida = request.form.get('salida', '').strip()
    destino = request.form.get('destino', '').strip()
    monto = request.form.get('monto', '0').strip()
    hora = request.form.get('hora', '').strip()
    fecha_viaje = request.form.get('fecha', '').strip()

    if not fecha_viaje:
        fecha_viaje = get_ahora().strftime('%Y-%m-%d')

    if cliente_id and salida and destino:
        try:
            monto_num = float(monto)
        except ValueError:
            monto_num = 0

        db = get_db()
        cursor = db.cursor()
        
        # Insertar el viaje (evento único)
        cursor.execute(
            'INSERT INTO viajes (cliente_id, salida, destino, monto, hora, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?)',
            (int(cliente_id), salida, destino, monto_num, hora, fecha_viaje)
        )
        viaje_id = cursor.lastrowid
        
        # El mes del pago se deriva de la fecha del viaje
        mes_viaje = fecha_viaje[:7] # YYYY-MM
        
        # Crear el pago para el mes del viaje inmediatamente
        db.execute(
            'INSERT INTO pagos (viaje_id, mes, monto, pagado) VALUES (?, ?, ?, 0)',
            (viaje_id, mes_viaje, monto_num)
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
    hora = request.form.get('hora', '').strip()
    fecha_viaje = request.form.get('fecha', '').strip()

    if salida and destino:
        try:
            monto_num = float(monto)
        except ValueError:
            monto_num = 0

        db = get_db()
        
        # Actualizar viaje
        if fecha_viaje:
            db.execute(
                'UPDATE viajes SET salida = ?, destino = ?, monto = ?, hora = ?, fecha_creacion = ? WHERE id = ?',
                (salida, destino, monto_num, hora, fecha_viaje, id)
            )
            # También actualizar el mes en el pago si no está pagado
            mes_viaje = fecha_viaje[:7]
            db.execute(
                'UPDATE pagos SET mes = ? WHERE viaje_id = ? AND pagado = 0',
                (mes_viaje, id)
            )
        else:
            db.execute(
                'UPDATE viajes SET salida = ?, destino = ?, monto = ?, hora = ? WHERE id = ?',
                (salida, destino, monto_num, hora, id)
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
        SELECT p.*, v.salida, v.destino, v.monto as viaje_monto, v.fecha_creacion, v.hora, c.nombre as cliente_nombre
        FROM pagos p
        JOIN viajes v ON p.viaje_id = v.id
        JOIN clientes c ON v.cliente_id = c.id
        WHERE p.mes = ?
        ORDER BY v.fecha_creacion DESC, v.hora DESC, v.id DESC
    ''', (mes,)).fetchall()

    # Calcular resumen
    total = sum(p['monto'] for p in pagos_mes)
    cobrado = sum(p['monto'] for p in pagos_mes if p['pagado'])
    pendiente = total - cobrado

    db.close()

    # Fecha y hora actual formateada (ej: Jueves 19, 4:10 pm)
    ahora = get_ahora()
    dias = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    dia_nombre = dias.get(ahora.strftime('%A'), ahora.strftime('%A'))
    hora_str = ahora.strftime('%I:%M %p').lower()
    fecha_hoy = f"{dia_nombre} {ahora.day}, {hora_str}"

    return render_template('pagos.html',
                           pagos=pagos_mes,
                           mes=mes,
                           nombre_mes=nombre_mes(mes),
                           mes_ant=mes_anterior(mes),
                           mes_sig=mes_siguiente(mes),
                           total=total,
                           cobrado=cobrado,
                           pendiente=pendiente,
                           fecha_hoy=fecha_hoy)


@app.route('/pagos/toggle', methods=['POST'])
def toggle_pago():
    pago_id = request.form.get('pago_id')
    mes = request.form.get('mes', mes_actual())

    db = get_db()
    pago = db.execute('SELECT pagado FROM pagos WHERE id = ?', (pago_id,)).fetchone()
    if pago:
        nuevo_estado = 0 if pago['pagado'] else 1
        fecha = get_ahora().strftime('%Y-%m-%d %H:%M') if nuevo_estado else None
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


@app.route('/pagos/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    pago_id = data.get('pago_id')
    nuevo_estado = data.get('nuevo_estado')

    if pago_id is not None and nuevo_estado is not None:
        db = get_db()
        # Si se marca como pagado (1), guardamos la fecha actual. Si no, queda vacía.
        fecha = get_ahora().strftime('%Y-%m-%d %H:%M') if int(nuevo_estado) else None
        db.execute('UPDATE pagos SET pagado = ?, fecha_pago = ? WHERE id = ?',
                   (int(nuevo_estado), fecha, pago_id))
        db.commit()
        db.close()
        return {"status": "success"}, 200
    
    return {"status": "error"}, 400


@app.route('/pagos/orden', methods=['POST'])
def generar_orden():
    pago_ids = request.form.getlist('pago_ids')
    mes = request.form.get('mes', mes_actual())

    if not pago_ids:
        flash('⚠️ Seleccioná al menos un viaje')
        return redirect(url_for('pagos', mes=mes))

    db = get_db()
    placeholders = ','.join('?' * len(pago_ids))
    pagos_sel = db.execute(f'''
        SELECT p.id, p.monto, p.mes,
               v.salida, v.destino, v.hora, v.fecha_creacion,
               c.nombre as cliente_nombre
        FROM pagos p
        JOIN viajes v ON p.viaje_id = v.id
        JOIN clientes c ON v.cliente_id = c.id
        WHERE p.id IN ({placeholders})
        ORDER BY c.nombre ASC, v.fecha_creacion ASC, v.hora ASC
    ''', pago_ids).fetchall()
    db.close()

    # Agrupar por cliente
    clientes_orden = {}
    for p in pagos_sel:
        nombre = p['cliente_nombre']
        if nombre not in clientes_orden:
            clientes_orden[nombre] = {'viajes': [], 'total': 0}
        clientes_orden[nombre]['viajes'].append(p)
        clientes_orden[nombre]['total'] += p['monto']

    total_general = sum(p['monto'] for p in pagos_sel)
    ahora = get_ahora()
    fecha_emision = ahora.strftime('%d/%m/%Y')
    hora_emision = ahora.strftime('%H:%M')

    return render_template('orden.html',
                           clientes_orden=clientes_orden,
                           total_general=total_general,
                           fecha_emision=fecha_emision,
                           hora_emision=hora_emision,
                           mes=mes,
                           nombre_mes=nombre_mes(mes))




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
        
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        # 1. Verificar si es un repositorio Git, si no, inicializarlo
        if not os.path.exists(os.path.join(project_root, '.git')):
            subprocess.check_call(['git', 'init'], cwd=project_root)
            subprocess.check_call(['git', 'remote', 'add', 'origin', 'https://github.com/dmampel/gestor-viajes.git'], cwd=project_root)
        
        # 2. Traer cambios y forzar actualización (reset --hard es más limpio para deploy)
        subprocess.check_call(['git', 'fetch', '--all'], cwd=project_root)
        pull_output = subprocess.check_output(['git', 'reset', '--hard', 'origin/main'], cwd=project_root, stderr=subprocess.STDOUT).decode('utf-8')
        
        # 3. Reiniciar el servidor (específico de PythonAnywhere)
        # Ajustar el nombre de usuario si es diferente a 'gestorviajes'
        wsgi_path = '/var/www/gestorviajes_pythonanywhere_com_wsgi.py'
        if os.path.exists(wsgi_path):
            os.utime(wsgi_path, None)
            restart_msg = "Servidor reiniciado."
        else:
            restart_msg = "WSGI no encontrado (¿Estás en local?)."

        return {
            "status": "success",
            "message": f"Despliegue completado con éxito. {restart_msg}",
            "git_output": pull_output
        }, 200
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Error en comando Git: {e.output.decode('utf-8') if e.output else str(e)}"
        }, 500
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }, 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
