"""Download raw map files via the sweeper API; not a local DPS 102 query."""
import os
import re
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlsplit, quote
import requests
import tinytuya
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Download raw map/path files via Tuya Sweeping Robot Open API (not DPS 102).'

    def add_arguments(self, parser):
        parser.add_argument('--output-dir', default='captures')

    def handle(self, *args, **options):
        names = ('TUYA_CLIENT_ID', 'TUYA_CLIENT_SECRET', 'TUYA_REGION', 'ROBOT_DEVICE_ID')
        missing = [name for name in names if not os.environ.get(name)]
        if missing:
            raise CommandError('Configura las variables: ' + ', '.join(missing))
        region = os.environ['TUYA_REGION']
        if region not in ('cn', 'us', 'us-e', 'eu', 'eu-w', 'in'):
            raise CommandError('TUYA_REGION no válida: usa cn, us, us-e, eu, eu-w o in.')
        folder = None
        try:
            cloud = tinytuya.Cloud(apiRegion=region, apiKey=os.environ['TUYA_CLIENT_ID'], apiSecret=os.environ['TUYA_CLIENT_SECRET'], apiDeviceID=os.environ['ROBOT_DEVICE_ID'])
            response = cloud.cloudrequest('/v1.0/users/sweepers/file/' + quote(os.environ['ROBOT_DEVICE_ID'], safe='') + '/realtime-map', action='GET')
            if not isinstance(response, dict) or response.get('success') is not True:
                code = response.get('code', '') if isinstance(response, dict) else ''
                safe_code = str(code) if re.fullmatch(r'[0-9]{1,10}', str(code)) else 'desconocido'
                raise CommandError(f'Tuya rechazó la consulta (código {safe_code}). Revisa región, permisos Sweeping Robot Open API y dispositivo vinculado.')
            files = response.get('result')
            if not isinstance(files, list) or not files:
                raise CommandError('Tuya no devolvió archivos de mapa. La compatibilidad del YW509 no está confirmada.')
            for item in files:
                if not isinstance(item, dict) or item.get('map_type') not in (0, 1):
                    raise CommandError('Tuya devolvió un tipo de archivo no reconocido.')
                parts = urlsplit(item.get('map_url', ''))
                if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password:
                    raise CommandError('Tuya devolvió una URL de descarga no válida.')
            folder = Path(options['output_dir']) / ('map-' + uuid4().hex)
            folder.mkdir(parents=True, mode=0o700)
            for index, item in enumerate(files):
                kind = 'layout' if item['map_type'] == 0 else 'path'
                target = folder / f'{index:02d}-{kind}.bin'
                # Signed URLs are secrets: never log or save them. Preserve TLS checks.
                with requests.get(item['map_url'], stream=True, timeout=(10, 30), allow_redirects=False) as downloaded:
                    if downloaded.status_code != 200:
                        raise CommandError('La descarga fue rechazada. Las URLs pueden haber caducado o faltar acceso al almacenamiento.')
                    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    try:
                        size = 0
                        with os.fdopen(fd, 'wb') as output:
                            for chunk in downloaded.iter_content(65536):
                                size += len(chunk)
                                if size > 50 * 1024 * 1024:
                                    raise CommandError('El archivo supera el límite de 50 MiB.')
                                output.write(chunk)
                        if not size:
                            raise CommandError('Se recibió un archivo vacío.')
                    except Exception:
                        target.unlink(missing_ok=True)
                        raise
                self.stdout.write(f'Guardado: {target} ({size} bytes)')
        except CommandError:
            raise
        except Exception:
            raise CommandError('No se pudo descargar el mapa. Revisa conexión, credenciales y permisos; no se muestran detalles que puedan revelar URLs o claves.') from None
        finally:
            if folder is not None and not any(folder.iterdir()):
                folder.rmdir()
