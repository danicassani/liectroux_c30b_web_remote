# DPS del Liectroux YW509

## Evidencia disponible

No se ha encontrado un esquema público específico del YW509 en las fuentes consultadas. La búsqueda de issues de GitHub por `YW509` no devolvió resultados el 12 de octubre de 2026. Esto no demuestra que no exista documentación. Las búsquedas por API de GitHub, Google y el portal de documentación de Tuya quedaron bloqueadas por el proxy de este entorno.

La implementación utiliza el script aportado por el propietario, que declara estos comandos como funcionales:

| Acción | Escrituras, en orden |
| --- | --- |
| Inicio | DPS 27 = `auto`; esperar 1 segundo; DPS 25 = `true` |
| Parada / pausa | DPS 25 = `false` |
| Base | DPS 27 = `chargego` |

No se han enviado comandos a un robot real desde este entorno. El título C30B en el menú del script no permite identificar el firmware del YW509.

## Fuentes externas consultadas

- [LocalTuya: implementación de aspiradoras](https://github.com/rospogrigio/localtuya/blob/master/custom_components/localtuya/vacuum.py): configura los IDs por dispositivo; `chargego` es el valor predeterminado para regresar a la base. Inicio y pausa escriben booleanos al DP de activación. Es corroboración general, no un esquema del YW509.
- [Tuya Local: Liectroux XR500 T3](https://github.com/make-all/tuya-local/blob/main/custom_components/tuya_local/devices/liectroux_xr500_t3_vacuum.yaml): activación en 2, modo en 4, batería en 8, silencio en 25. Su DPS 102 figura como `rooms_msg_unseen`, no como mapa confirmado.
- [Reporte original del XR500 T3, con DPS observados](https://github.com/make-all/tuya-local/issues/1056).
- [Tuya Local: Liectroux G7](https://github.com/make-all/tuya-local/blob/main/custom_components/tuya_local/devices/liectroux_g7_vacuum.yaml): limpieza en 101, pausa en 102, modo en 104, batería en 106; usa `backcharge` para la base.

Por tanto, no deben copiarse los IDs de otro Liectroux. Tampoco se consideran verificados los enums de succión, dirección, ni la interpretación de mapas de la tabla inicial. Los sensores 14, 28, 30, 32 y 33 se muestran siguiendo el script y la tabla, sin escribir en ellos.

## Cómo obtener una fuente específica del dispositivo

La fuente más fiable es el esquema Tuya del producto/firmware del robot: IDs, códigos, tipos, permisos de lectura/escritura y enums. Desde un proyecto Tuya IoT autorizado al dispositivo, consulta sus funciones, estado y especificación. TinyTuya permite recuperar metadatos con su wizard y API Cloud; consulta su [documentación](https://github.com/jasonacox/tinytuya#tuya-cloud-access).

No publiques la clave local, identificador del dispositivo, credenciales de Tuya ni archivos `devices.json` o `tinytuya.json`. Comparte únicamente el esquema sanitizado. Para corroborar comportamiento, captura el estado local antes y después de iniciar, pausar y enviar a la base desde la app oficial. Leer estado no prueba todos los enums admitidos. No se deben probar valores de escritura a ciegas.

DPS 102 queda pendiente de capturas y de identificación de su formato. No hay decodificador de mapas en esta versión.

## Control de succión

El slider escribe DPS 30 usando únicamente los enums configurados en `ROBOT_SUCTION_LEVELS`. La asignación de escritura a 30 procede de la tabla aportada, y todavía requiere confirmación en el YW509. Por ello el control real no tiene niveles habilitados por defecto. Los niveles `gentle,normal,strong` de demo son ejemplos; no constituyen validación del firmware. El usuario debe verificar ID y enums del esquema antes de habilitar el control real.

## Mapas: resultado de la investigación

El propietario confirmó que la lectura local de DPS 102 de su script **no proporciona datos útiles** en su YW509. Se descarta ese método como solución para obtener su mapa. Tampoco hay evidencia de un valor que se pueda escribir en 102 para solicitarlo.

Fuentes consultadas el 12 de octubre de 2026:

- [TinyTuya: consulta local](https://github.com/jasonacox/tinytuya/blob/master/tinytuya/core/XenonDevice.py): `set_dpsUsed` selecciona DPS y `status()` envía `DP_QUERY`; no implica generar un mapa.
- [Tuya Cloud Map Extractor](https://github.com/oven-lab/tuya_cloud_map_extractor): utiliza Sweeping Robot Open API para aspiradoras láser, incluye XR500, no YW509; está sin mantenimiento.
- [Discusión de captura local](https://github.com/oven-lab/tuya_cloud_map_extractor/issues/21): el autor describe un DPS de solicitud y otro de comunicaciones en su dispositivo, sin IDs universales.
- [Tuya Vacuum Maps](https://github.com/jaidenlabelle/tuya-vacuum-maps) y su dependencia `tuya-vacuum==0.1.8`, `tuya_vacuum/vacuum.py`: la solicitud es `GET /v1.0/users/sweepers/file/{device_id}/realtime-map`. El resultado contiene `map_url` y `map_type`; 0 corresponde a mapa y 1 a trayectoria. Los bytes se descargan de las URLs proporcionadas.
- [Ejemplo de descarga del proyecto](https://github.com/jaidenlabelle/tuya-vacuum-maps/blob/main/scripts/download_maps.py): muestra la misma ruta, aunque su importación apunta a un módulo que ya no está en el checkout; la dependencia actual confirma el endpoint.
- [TinyTuya issue 551](https://github.com/jasonacox/tinytuya/issues/551): distintos reportes sobre Lefant y Cecotec; algunas respuestas son análisis automatizados, no un esquema validado. No se usan sus IDs ni `get_both` para el YW509.

El comando `download_map` implementa la ruta cloud encontrada, no una lectura DPS 102. Guarda bytes sin interpretar. **Su compatibilidad con YW509 y su acceso real no han sido comprobados**: no hay credenciales/proyecto Tuya disponibles. No escribe DPS ni inicia limpieza. Si se requiere una solución exclusivamente local, falta identificar en el esquema del firmware el trigger y transporte de mapas; no se enviarán comandos de otro modelo a ciegas.
