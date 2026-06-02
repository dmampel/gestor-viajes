# A ver cuánto gasto y cuánto gano

Sistema de gestión personal y de negocio para registrar viajes, cobros, gastos e ingresos — todo en un solo lugar, sin duplicar datos.

## Características

### Balance financiero
- **Pantalla de balance por mes**: resumen de ingresos totales, gastos totales y balance neto, con navegación mensual.
- **Ingresos automáticos desde viajes**: al marcar un viaje como pagado, aparece automáticamente en el balance del mes como ingreso.
- **Otros ingresos**: registro manual de ingresos fuera de la agencia (freelance, alquiler, etc.) con categorías.
- **Gastos**: registro de egresos por categoría (Servicios, Comida, Transporte, Alquiler, Salud, Otros) con desglose mensual.
- **Desglose por categoría**: pills visuales que muestran cuánto se gastó/ingresó por cada categoría en el mes.

### Gestión de viajes y cobros
- **Tablero de Pagos**: columnas de Pendientes y Pagados con **drag-and-drop** para cambiar el estado en tiempo real.
- **Deuda por cliente**: panel colapsable que agrupa el total adeudado por cada cliente.
- **Orden de pago en PDF**: generación de orden de cobro profesional por cliente, sin dependencias externas (`window.print()`).
- **Hora exacta por viaje**: registro con visualización en formato 12h (am/pm).
- **Repetir viaje**: botón 🔁 para pre-rellenar el formulario con los datos de un viaje anterior.
- **Intercambio de ruta**: botón ⇄ para invertir salida y destino al instante.
- **Fecha flexible**: registro para hoy, mañana o cualquier fecha, con botones de acceso rápido.

### Clientes e historial
- **Gestión de clientes**: registro de clientes activos/inactivos con conteo de viajes.
- **Log de viajes**: historial con autocompletado inteligente basado en el último viaje de cada cliente.
- **Historial de cobros**: resumen mensual de cobrado, pendiente y total.

### Acceso y seguridad
- **Modo demo**: visitantes acceden a una base de datos ficticia (`demo.db`) con datos de ejemplo; el admin usa la base real. Sin registro de usuario.
- **Diseño mobile-first**: barra de navegación inferior, optimizado para iPhone. Adapta a desktop con CSS Grid.

## Tecnologías

- **Backend**: Python + Flask
- **Base de datos**: SQLite con migraciones automáticas
- **Frontend**: HTML5 + Vanilla CSS3
- **Drag-and-drop**: Sortable.js
- **Despliegue**: GitHub Webhooks + PythonAnywhere

## Instalación local

```bash
git clone https://github.com/dmampel/gestor-viajes.git
pip install flask
python flask_app.py
```

Acceder en `http://127.0.0.1:5001`

Para regenerar los datos del demo:

```bash
python seed_demo.py
```

## Despliegue

Actualización automática en PythonAnywhere con cada `git push` a `main` vía webhook.
