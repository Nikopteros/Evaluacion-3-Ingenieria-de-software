# Hotel Ríos del Sur · Sistema de Gestión Hotelera

Prototipo funcional de un sistema web para gestionar habitaciones, huéspedes y reservas del Hotel Ríos del Sur.
Desarrollado en **Python + Django**, con interfaz HTML + Bootstrap y sin JavaScript propio.

**Evaluación 3 · Ingeniería de Software**
**Integrantes:** Nicolás Román, David Rodríguez, Diego Vegas
**Docente:** Cristian Carrasco
**Repositorio:** [https://github.com/Nikopteros/Evaluacion-3-Ingenieria-de-software.git]

**Directorio de base de datos** hotel_rios_del_sur\database
**Directorio de Informe** hotel_rios_del_sur\docs
---

## 1. Problemas que resuelve

| Problema | Solución implementada |
|---|---|
| Reservas duplicadas | No se permiten dos reservas activas que se crucen en la misma habitación. Al guardar se bloquea la fila de la habitación (`select_for_update`) dentro de una transacción. Además se avisa si un mismo huésped ya tiene otra reserva en esas fechas. |
| No se sabe rápido qué habitaciones están disponibles | Consulta de disponibilidad por fechas, personas y tipo, y un panel de recepción con ocupación, estados y llegadas y salidas del día. |
| Datos de huéspedes dispersos | Ficha única por huésped (RUT validado o pasaporte, sin duplicados) con todo su historial de reservas. |

---

## 2. Tecnologías

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.10 o superior |
| Framework | Django (`>=5.1,<6.1`) |
| Interfaz | Plantillas HTML de Django + Bootstrap 5.3.3 (incluido en `static/css/`, funciona sin internet) |
| Base de datos | SQLite (por defecto) o MySQL / MariaDB (XAMPP) |
| Autenticación | Usuarios, grupos y sesiones de Django |
| Correo | SMTP (en desarrollo los correos se muestran en la consola) |

---

## 3. Instalación

### Requisitos
- Python 3.10 o superior
- Git
- (Opcional) XAMPP, solo si se quiere usar MySQL

### Opción A: instalación rápida con SQLite (recomendada)

No requiere instalar ninguna base de datos. Las tablas y los datos de ejemplo se crean automáticamente.

```bash
git clone [https://github.com/Nikopteros/Evaluacion-3-Ingenieria-de-software.git]
cd hotel-rios-del-sur
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py crear_datos_demo
python manage.py runserver
```

> En Linux o Mac el entorno virtual se activa con `source venv/bin/activate`.

Abrir en el navegador: **http://127.0.0.1:8000/**

### Opción B: usar MySQL con XAMPP y el archivo SQL

El archivo `database/hotel_rios_del_sur.sql` contiene la base de datos completa (estructura y datos de ejemplo).

1. Abrir **XAMPP** e iniciar **MySQL**.
2. Entrar a **http://localhost/phpmyadmin**.
3. Ir a la pestaña **Importar**, sin seleccionar ninguna base de datos.
4. Elegir el archivo `database/hotel_rios_del_sur.sql` y presionar **Importar**. Se crea la base `hotel_rios_del_sur` con todas sus tablas y datos.
5. Instalar el conector y configurar el proyecto (PowerShell):

```powershell
pip install mysqlclient
$env:DB_ENGINE="mysql"
$env:DB_NAME="hotel_rios_del_sur"
$env:DB_USER="root"
$env:DB_PASSWORD=""
python manage.py runserver
```

> En CMD las variables se definen con `set DB_ENGINE=mysql`, etc. La clave de `root` en XAMPP viene vacía por defecto.
> Como el SQL ya incluye los datos, no es necesario ejecutar `migrate` ni `crear_datos_demo`.
> Si `mysqlclient` da problemas de instalación en Windows, usar la Opción A.

### Usuarios de prueba

| Usuario | Contraseña | Rol |
|---|---|---|
| `recepcion` | `Recepcion2026!` | Recepción |
| `cliente` | `Cliente2026!` | Cliente |
| `admin` | `Admin2026!` | Administrador (también accede a `/admin/`) |

> Estas credenciales son solo para demostración y deben eliminarse o cambiarse en producción.

### Pruebas automáticas

```bash
python manage.py test hotel
```

19 pruebas: reservas superpuestas, capacidad, cancelación, disponibilidad, check-in y check-out, validación de RUT, teléfono y número de habitación, registro web, edición de habitaciones y permisos por rol.

---

## 4. Funcionalidades

| Funcionalidad | Quién | Dónde |
|---|---|---|
| Registro y administración de habitaciones | Recepción | `Recepción → Habitaciones` (registrar, editar, tipos y tarifas, cambiar estado) |
| Registro de huéspedes | Recepción / Cliente | `Recepción → Huéspedes` · el cliente usa `Registrarse` |
| Consulta de disponibilidad | Todos (incluso invitados) | `Disponibilidad` |
| Creación de reservas | Cliente (queda *pendiente*) / Recepción (queda *confirmada*) | Botón **Reservar** en Disponibilidad · `Recepción → Reservas → Nueva reserva` |
| Consulta de reservas | Cliente (las suyas) / Recepción (todas, con filtros) | `Mis reservas` · `Recepción → Reservas` |
| Cancelación de reservas | Cliente / Recepción | Botón **Cancelar** |
| Control de habitaciones ocupadas y disponibles | Recepción | `Recepción → Panel` |
| Check-in y check-out | Recepción | Panel o detalle de la reserva |

### Ciclo de vida

```
Reserva:     Pendiente ──confirmar──▶ Confirmada ──check-in──▶ En curso ──check-out──▶ Finalizada
                  └──────────cancelar──────┘

Habitación:  Disponible ──check-in──▶ Ocupada ──check-out──▶ En limpieza ──recepción──▶ Disponible
             (Recepción también puede marcarla "En mantención"; así no aparece en la disponibilidad)
```

### Reglas de negocio

- La fecha de salida debe ser posterior a la llegada, y la llegada no puede ser anterior a hoy.
- El día de salida queda libre: una reserva que termina el 10 no choca con otra que empieza el 10.
- Las reservas pendientes, confirmadas y en curso bloquean la habitación; las canceladas y finalizadas no.
- No se puede reservar para más personas que la capacidad del tipo de habitación.
- El check-in solo se permite con la reserva confirmada, dentro de sus fechas y con la habitación *Disponible*.
- Una habitación solo pasa a *Ocupada* mediante el check-in; no se puede marcar a mano.
- Mientras una habitación está ocupada no se puede cambiar su número, piso ni tipo.
- No se puede cambiar el tipo de una habitación si deja una reserva activa con más personas que la nueva capacidad.
- El número de habitación solo tiene dígitos y sus centenas indican el piso (203 → piso 2).
- El teléfono acepta números, espacios, guiones y un `+` al inicio, con 8 a 15 dígitos.
- El precio por noche se guarda en la reserva: un cambio de tarifa no altera reservas ya hechas.
- Al crear, confirmar o cancelar una reserva se envía un correo al huésped.

---

## 5. Seguridad

- **Autenticación y roles:** inicio de sesión de Django y grupos `Recepcion` y `Cliente`. Cada vista valida el rol; un cliente solo ve y cancela sus propias reservas.
- **Contraseñas:** almacenadas con hash PBKDF2 y validadas por los validadores de Django (largo mínimo, no comunes, no solo numéricas).
- **Inyección SQL:** todo el acceso a datos usa el ORM de Django (consultas parametrizadas).
- **XSS:** las plantillas escapan el HTML automáticamente.
- **CSRF:** token en todos los formularios; las acciones que modifican datos se hacen solo por POST, con pantalla de confirmación previa.
- **Validación de datos:** RUT chileno (módulo 11), documento único, correo, teléfono, fechas, capacidad y número de habitación, tanto en formularios como en los modelos.
- **Integridad:** transacciones atómicas y bloqueo de filas para evitar reservas simultáneas; `PROTECT` para impedir borrar huéspedes o habitaciones con historial.
- **Trazabilidad:** cada reserva registra quién la creó y las horas de check-in, check-out y cancelación.
- **Configuración por variables de entorno:** `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS` y las credenciales de base de datos y correo.

> **Para producción:** definir una `DJANGO_SECRET_KEY` propia, usar `DJANGO_DEBUG=0`, indicar el dominio en `DJANGO_ALLOWED_HOSTS` y activar HTTPS.

---

## 6. Estructura del proyecto

```
hotel-rios-del-sur/
├── config/                  Configuración (settings.py, urls.py)
├── hotel/
│   ├── models.py            TipoHabitacion, Habitacion, Huesped, Reserva
│   ├── servicios.py         DisponibilidadServicio, ReservaServicio, NotificacionServicio
│   ├── views.py             Vistas por rol (público, cliente, recepción)
│   ├── forms.py             Formularios y validaciones
│   ├── mixins.py            Control de acceso por rol
│   ├── validators.py        Validadores de RUT, teléfono y número de habitación
│   ├── tests.py             Pruebas automáticas
│   ├── migrations/          Migraciones de la base de datos
│   └── management/commands/crear_datos_demo.py
├── templates/               Plantillas HTML
├── static/css/              Bootstrap 5.3.3
├── database/
│   └── hotel_rios_del_sur.sql   Base de datos completa (MySQL / MariaDB)
├── docs/
│   └── Informe_Tecnico.docx     Informe técnico
├── manage.py
├── requirements.txt
└── README.md
```

---

## 7. Comandos útiles

| Comando | Para qué sirve |
|---|---|
| `python manage.py runserver` | Inicia el servidor de desarrollo |
| `python manage.py migrate` | Crea o actualiza las tablas |
| `python manage.py crear_datos_demo` | Carga datos de ejemplo (se puede ejecutar varias veces sin duplicar) |
| `python manage.py test hotel` | Ejecuta las pruebas automáticas |
| `python manage.py createsuperuser` | Crea un administrador nuevo |
