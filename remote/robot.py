"""Local Tuya commands confirmed by the supplied controller script."""
import threading
import time
import tinytuya
from django.conf import settings

class RobotError(Exception):
    pass

_lock = threading.Lock()
_demo = {'14': 86, '25': False, '27': 'standby', '28': 'paused', '30': 'normal', '32': 0, '33': 0}

def _validate(response):
    if not isinstance(response, dict) or response.get('Error') or response.get('Err'):
        raise RobotError('El robot no confirmó la comunicación. Comprueba la conexión y la configuración.')
    return response

class Robot:
    def _device(self):
        if not all((settings.ROBOT_DEVICE_ID, settings.ROBOT_IP, settings.ROBOT_LOCAL_KEY)):
            raise RobotError('Falta configurar ROBOT_DEVICE_ID, ROBOT_IP o ROBOT_LOCAL_KEY en el servidor.')
        device = tinytuya.Device(dev_id=settings.ROBOT_DEVICE_ID, address=settings.ROBOT_IP, local_key=settings.ROBOT_LOCAL_KEY, dev_type='device22')
        device.set_version(3.3)
        device.set_socketTimeout(5)
        device.set_socketRetryLimit(1)
        device.set_dpsUsed({str(i): None for i in range(1, 35)})
        return device

    def _run(self, operation):
        with _lock:
            device = None
            try:
                device = self._device()
                return operation(device)
            except RobotError:
                raise
            except Exception:
                raise RobotError('No se pudo comunicar con el robot. Comprueba que el servidor tenga acceso a su red local.') from None
            finally:
                if device is not None:
                    device.close()

    def status(self):
        if settings.ROBOT_DEMO:
            with _lock:
                return dict(_demo)
        def read(device):
            response = _validate(device.status())
            if not isinstance(response.get('dps'), dict):
                raise RobotError('El robot respondió sin datos de estado.')
            return response['dps']
        return self._run(read)

    def command(self, action):
        if action not in ('start', 'stop', 'dock'):
            raise ValueError('Unknown command')
        if settings.ROBOT_DEMO:
            with _lock:
                _demo.update({'25': action == 'start', '27': {'start': 'auto', 'stop': 'standby', 'dock': 'chargego'}[action], '28': {'start': 'cleaning', 'stop': 'paused', 'dock': 'docking'}[action]})
            return
        def send(device):
            if action == 'start':
                _validate(device.set_value(27, 'auto'))
            elif action == 'stop':
                _validate(device.set_value(25, False))
            else:
                _validate(device.set_value(27, 'chargego'))
        self._run(send)

    def set_suction(self, value):
        if value not in settings.ROBOT_SUCTION_LEVELS:
            raise ValueError('Unsupported suction level')
        if settings.ROBOT_DEMO:
            with _lock:
                _demo['30'] = value
            return
        self._run(lambda device: _validate(device.set_value(30, value)))
