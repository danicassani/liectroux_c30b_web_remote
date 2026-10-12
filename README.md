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

## Slider de succión

El slider selecciona niveles discretos y envía DPS 30 únicamente al pulsar **Aplicar succión**. En demo incluye Suave (`gentle`), Normal (`normal`) y Fuerte (`strong`). Para control real configura `ROBOT_SUCTION_LEVELS` con los enums admitidos por tu firmware, ordenados de menor a mayor, por ejemplo `gentle,normal,strong` **solo si has confirmado esos valores**. Sin esta variable, el control real permanece desactivado. No se presupone que `eco` o `max` existan. El nivel actual se selecciona cuando coincide con uno de los configurados; si no coincide, la web avisa de que no se conoce.

## Descargar archivos del mapa (Tuya Cloud)

La lectura local de DPS 102 ya fue probada por el propietario y no proporciona el mapa. La alternativa investigada es la API cloud de aspiradoras. **YW509 aún no está confirmado como compatible**; consulta [fuentes y limitaciones](docs/dps.md).

Necesita un proyecto Tuya IoT vinculado al robot, permiso **Sweeping Robot Open API**, y estas variables del proceso: `TUYA_CLIENT_ID`, `TUYA_CLIENT_SECRET`, `TUYA_REGION` y `ROBOT_DEVICE_ID`. Configura los valores de forma privada, nunca en Git ni en chat. La región debe ser la del proyecto: `cn`, `us`, `us-e`, `eu`, `eu-w` o `in`.

Desde la raíz del repositorio:

```sh
DJANGO_DEBUG=1 .venv/bin/python manage.py download_map
```

Se consulta `/v1.0/users/sweepers/file/{device_id}/realtime-map` y se descargan los archivos en `captures/map-<id>/`: `*-layout.bin` (mapa) y `*-path.bin` (trayectoria). No se decodifican. Cada ejecución usa un directorio único y archivos privados 0600, ignorados por Git. Las URLs firmadas no se guardan ni muestran. `--output-dir` permite otro directorio; mantenlo fuera de Git. Si falla una descarga, se elimina su archivo parcial y se conservan los archivos completos anteriores.

Requiere HTTPS al host regional de Tuya y a los destinos de almacenamiento devueltos por la API. Si el entorno restringe red, habilita esos destinos concretos. No hay modo demo para esta descarga: las pruebas usan respuestas simuladas, no archivos del robot.

La app configurada no basta para acceder a esta API. Para preparar el acceso, sigue la [configuración Tuya IoT de la integración](https://github.com/oven-lab/tuya_cloud_map_extractor#prerequisites): crea un proyecto cloud en el centro de datos correcto, vincula tu cuenta de Smart Life/Tuya mediante QR desde el proyecto y autoriza Sweeping Robot Open API si está disponible para tu cuenta. Verifica condiciones y disponibilidad del servicio en Tuya antes de activarlo. El robot debe aparecer en los dispositivos del proyecto. Guarda Client ID y Client Secret de forma privada. No hace falta cambiar la lógica de los botones ni conectar el robot directamente a este entorno cloud.
