# Liectroux YW509 · Web remote

Web Django en español con inicio de limpieza, parada/pausa y vuelta a la base. Control local con TinyTuya 3.3 y comandos del script original. Incluye autenticación, protección CSRF, estado y modo demostración. Los mapas quedan pendientes: [evidencia de DPS](docs/dps.md).

## Instalación

Python 3.12 recomendado. Desde la raíz del repositorio:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.lock
export DJANGO_DEBUG=1
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
```

## Demostración

```sh
export DJANGO_DEBUG=1 ROBOT_DEMO=1
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

Inicia sesión con el usuario creado. Los botones cambian el estado simulado; no hay comunicación con el robot. El estado demo es temporal y se reinicia con el proceso. No hay usuario ni contraseña predeterminados.

## Robot real

Ejecuta el servidor en un ordenador de la misma LAN del robot. Este entorno cloud no garantiza acceso a dispositivos domésticos. TinyTuya usa una conexión TCP local al puerto 6668; no es una API HTTPS de Tuya Cloud.

Configura en el proceso, sin guardar ni publicar los valores:

- `ROBOT_DEVICE_ID`: identificador de Tuya.
- `ROBOT_IP`: IP local del robot (reserva DHCP recomendada).
- `ROBOT_LOCAL_KEY`: clave local.
- `ROBOT_DEMO=0`: control real; es el valor predeterminado.

La aplicación no carga archivos `.env` automáticamente. Define variables en la shell o en el gestor del servicio. Nunca incluyas claves en Git. Los detalles de errores del dispositivo no se muestran para evitar filtrar credenciales.

Inicio escribe 27=`auto` y después 25=`true`; parada escribe 25=`false`; base escribe 27=`chargego`. Un mensaje de orden enviada indica respuesta de comunicación, no que el movimiento físico haya finalizado. Actualiza el estado para consultar el robot. Si falla la segunda escritura de inicio, la primera puede haber sido aplicada: consulta el estado antes de reintentar.

Las operaciones se serializan dentro de un proceso. Usa un único proceso de servidor para evitar órdenes simultáneas sobre el mismo robot. Cada operación abre y cierra su conexión. No mantengas otra conexión persistente de TinyTuya al mismo tiempo.

Para acceder desde la LAN durante desarrollo, añade el hostname/IP del servidor a `DJANGO_ALLOWED_HOSTS` y usa `runserver 0.0.0.0:8000`. Para despliegue, usa un servidor WSGI con `config.wsgi:application`, un solo worker y HTTPS; configura `DJANGO_DEBUG=0`, una `DJANGO_SECRET_KEY` privada y `DJANGO_ALLOWED_HOSTS`. El servidor de desarrollo no es un despliegue de producción.

## Validación

```sh
DJANGO_DEBUG=1 ROBOT_DEMO=1 .venv/bin/python manage.py test
DJANGO_DEBUG=1 .venv/bin/python manage.py check
```

Las pruebas verifican la secuencia exacta de comandos, errores de red, cierre de conexiones, login, CSRF, comandos por POST y los tres botones en demo. No validan firmware ni movimiento físico. Solo consulta de estado al abrir la página: no hay órdenes automáticas ni sondeo en segundo plano.

## Flujo de trabajo

Cada tarea se desarrolla en una rama nueva y termina con un pull request. No subir credenciales ni capturas privadas del robot.
