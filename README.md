# 🚐 Gestor de Viajes Dixi

Sistema de gestión para servicios de transporte y logística, diseñado para organizar viajes diarios, clientes y cobros de manera profesional y eficiente.

## 🚀 Características Principales

- **Tablero de Pagos Inteligente**: Organiza los viajes del día en franjas horarias (Mañana, Tarde, Noche) mediante un sistema de **arrastrar y soltar (Drag-and-Drop)**.
- **Gestión de Clientes**: Registro de clientes con seguimiento de estado (Activos/Inactivos).
- **Log de Viajes**: Registro histórico de rutas y montos, con autocompletado inteligente basado en el último viaje realizado.
- **Historial de Cobros**: Visualización mensual del progreso de cobros y estados de pago.
- **Despliegue Automático**: Integración total con GitHub y PythonAnywhere para actualizaciones en tiempo real.

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python + Flask
- **Base de Datos**: SQLite (con soporte para migraciones automáticas)
- **Frontend**: HTML5, Vanilla CSS3 (Modern UI)
- **Iconografía**: Lucide Icons
- **Interactividad**: Sortable.js (para el tablero de arrastrar y soltar)
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
4. Acceder en el navegador a: `http://127.0.0.1:5000`

## ☁️ Despliegue (CI/CD)

El proyecto está configurado para actualizarse automáticamente en PythonAnywhere cada vez que se hace un `git push` a la rama `main`.

---
*Desarrollado para la optimización de servicios de transporte.*
