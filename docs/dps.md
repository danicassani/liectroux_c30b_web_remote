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
