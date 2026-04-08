# 🚐 Gestor de Viajes

Sistema de gestión para servicios de transporte y logística, diseñado para organizar viajes diarios, clientes y cobros de manera profesional y eficiente.

## 🚀 Características Principales

- **Tablero de Pagos Inteligente**: Gestión simplificada de cobros dividida en **No Pagados** y **Pagados**, con sistema de **arrastrar y soltar (Drag-and-Drop)** para actualizar estados en tiempo real.
- **Repetir Viaje**: Botón 🔁 en cada viaje reciente para pre-rellenar el formulario con los datos del viaje seleccionado (cliente, ruta, monto y hora), agilizando la carga de viajes frecuentes.
- **Deuda por Cliente**: Panel colapsable en la pestaña de Pagos que agrupa y muestra el total adeudado por cada cliente con sus viajes pendientes.
- **Orden de Pago en PDF**: Generación de una orden de cobro profesional por cliente directamente desde el panel de deuda. Incluye encabezado, tabla de recorridos, total a cobrar y pie de página. Se guarda como PDF desde el navegador (sin dependencias extra).
- **Seguimiento de Hora Exacta**: Registro de la hora específica para cada viaje con visualización automática en formato **12h (am/pm)**.
- **Gestión de Clientes**: Registro detallado de clientes con seguimiento de estado (Activos/Inactivos).
- **Log de Viajes**: Registro histórico de rutas y montos, con autocompletado inteligente basado en el último viaje realizado.
- **Intercambio Rápido de Rutas**: Botón ⇄ para invertir automáticamente la Salida y el Destino, ideal para cargas de viajes de ida y vuelta.
- **Selección de Fecha Flexible**: Registro de viajes para hoy, mañana o cualquier fecha futura, con botones de acceso rápido optimizados para uso desde el iPhone.
- **Historial de Cobros**: Resumen mensual de ingresos cobrados, pendientes y totales para un control financiero completo.
- **Accesibilidad Multi-Dispositivo**: Diseño adaptable tanto para celular (Mobile First) con barra de navegación inferior interactiva, inteligente como para monitor de Escritorio adaptándose usando distribuciones nativas con CSS Grid.
- **Modo Portfolio (Seguridad de Datos)**: Incluye un novedoso sistema de entrada bifurcada sin registro de usuario, donde los dueños inician sesión a una base de datos original resguardada, pero visitantes de GitHub y reclutadores entran como observadores con una base de datos ficticia clonada (`demo.db`).
- **Despliegue Automático**: Integración con GitHub y PythonAnywhere para actualizaciones en tiempo real.

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python + Flask
- **Base de Datos**: SQLite (con soporte para migraciones automáticas)
- **Frontend**: HTML5, Vanilla CSS3 (Modern UI)
- **Interactividad**: Sortable.js (tablero drag-and-drop)
- **PDF**: Generación via `window.print()` + CSS `@media print` (sin dependencias externas)
- **Despliegue**: GitHub Webhooks + PythonAnywhere

## 💻 Instalación Local

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/dmampel/gestor-viajes.git
   ```
2. Instalar dependencias:
   ```bash
   pip install flask
   ```
3. Ejecutar la aplicación:
   ```bash
   python flask_app.py
   ```
4. Acceder en el navegador a: `http://127.0.0.1:5001`

## ☁️ Despliegue (CI/CD)

El proyecto está configurado para actualizarse automáticamente en PythonAnywhere cada vez que se hace un `git push` a la rama `main`.

---
*Desarrollado para la optimización de servicios de transporte.*
