from unittest.mock import Mock, patch, call
from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase, override_settings, Client
from .robot import Robot, RobotError

@override_settings(ROBOT_DEMO=False, ROBOT_DEVICE_ID='test', ROBOT_IP='192.0.2.1', ROBOT_LOCAL_KEY='test-key')
class ProtocolTests(SimpleTestCase):
    def setUp(self):
        self.patcher = patch('remote.robot.tinytuya.Device')
        self.factory = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.device = self.factory.return_value
        self.device.set_value.return_value = {}

    @patch('remote.robot.time.sleep')
    def test_start_uses_confirmed_sequence(self, sleep):
        Robot().command('start')
        self.assertEqual(self.device.set_value.call_args_list, [call(27, 'auto'), call(25, True)])
        sleep.assert_called_once_with(1)
        self.device.set_version.assert_called_once_with(3.3)
        self.device.close.assert_called_once()

    def test_stop_and_dock(self):
        Robot().command('stop')
        Robot().command('dock')
        self.assertEqual(self.device.set_value.call_args_list, [call(25, False), call(27, 'chargego')])

    def test_error_stops_start_sequence_and_closes(self):
        self.device.set_value.return_value = {'Error': 'invalid', 'Err': '914'}
        with self.assertRaises(RobotError):
            Robot().command('start')
        self.device.set_value.assert_called_once_with(27, 'auto')
        self.device.close.assert_called_once()

    def test_network_error_does_not_leak_details(self):
        self.device.status.side_effect = OSError('test-key secret')
        with self.assertRaises(RobotError) as caught:
            Robot().status()
        self.assertNotIn('test-key', str(caught.exception))
        self.device.close.assert_called_once()

    def test_status_requires_dps(self):
        self.device.status.return_value = {}
        with self.assertRaises(RobotError):
            Robot().status()

@override_settings(ROBOT_DEMO=True)
class WebTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('owner', password='test-password')
        self.client.force_login(self.user)

    def test_anonymous_cannot_command(self):
        self.client.logout()
        with patch('remote.views.Robot') as robot:
            self.assertEqual(self.client.post('/command/start/').status_code, 302)
            robot.assert_not_called()

    def test_get_cannot_command(self):
        self.assertEqual(self.client.get('/command/start/').status_code, 405)

    def test_csrf_required(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post('/command/start/').status_code, 403)

    def test_unknown_command(self):
        self.assertEqual(self.client.post('/command/anything/').status_code, 400)

    def test_demo_buttons_update_state(self):
        for action, label in [('start', 'Limpiando'), ('stop', 'En pausa'), ('dock', 'Volviendo a la base')]:
            response = self.client.post(f'/command/{action}/', follow=True)
            self.assertContains(response, label)
            self.assertContains(response, 'Modo demostración')

    @patch('remote.views.Robot')
    def test_communication_error_is_visible(self, robot):
        robot.return_value.command.side_effect = RobotError('Sin conexión')
        robot.return_value.status.return_value = {}
        self.assertContains(self.client.post('/command/start/', follow=True), 'Sin conexión')

@override_settings(ROBOT_SUCTION_LEVELS=('gentle', 'normal', 'strong'))
@override_settings(ROBOT_DEMO=False, ROBOT_DEVICE_ID="test", ROBOT_IP="192.0.2.1", ROBOT_LOCAL_KEY="test-key")
class SuctionProtocolTests(SimpleTestCase):
    setUp = ProtocolTests.setUp
    def test_suction_writes_only_dps30(self):
        Robot().set_suction('strong')
        self.device.set_value.assert_called_once_with(30, 'strong')
        self.device.close.assert_called_once()

    def test_unknown_value_never_opens_connection(self):
        with self.assertRaises(ValueError):
            Robot().set_suction('arbitrary')
        self.factory.assert_not_called()

@override_settings(ROBOT_DEMO=True, ROBOT_SUCTION_LEVELS=('gentle', 'normal', 'strong'))
class SuctionWebTests(TestCase):
    setUp = WebTests.setUp
    def test_slider_applies_and_reflects_level(self):
        response = self.client.post('/suction/', {'level': '2'}, follow=True)
        self.assertContains(response, 'strong')
        self.assertContains(response, 'value="2"')
        self.assertEqual(Robot().status()['30'], 'strong')

    def test_invalid_index_does_not_send(self):
        with patch('remote.views.Robot') as robot:
            for value in ['-1', '3', '1.5', 'strong', '']:
                self.assertEqual(self.client.post('/suction/', {'level': value}).status_code, 400)
            robot.assert_not_called()

    def test_suction_requires_login_post_and_csrf(self):
        self.assertEqual(self.client.get('/suction/').status_code, 405)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post('/suction/', {'level': '1'}).status_code, 403)
        self.client.logout()
        self.assertEqual(self.client.post('/suction/', {'level': '1'}).status_code, 302)

    @override_settings(ROBOT_SUCTION_LEVELS=())
    def test_unconfigured_levels_cannot_be_sent(self):
        self.assertContains(self.client.get('/'), 'Configura los niveles admitidos')
        self.assertEqual(self.client.post('/suction/', {'level': '0'}).status_code, 400)

class CloudMapTests(SimpleTestCase):
    def test_cloud_map_saves_exact_bytes_and_private_files(self):
        import os, tempfile, stat
        from pathlib import Path
        from io import StringIO
        from django.core.management import call_command
        env = {'TUYA_CLIENT_ID': 'test-id', 'TUYA_CLIENT_SECRET': 'test-secret', 'TUYA_REGION': 'eu', 'ROBOT_DEVICE_ID': 'robot-test'}
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, env), patch('remote.management.commands.download_map.tinytuya.Cloud') as cloud, patch('remote.management.commands.download_map.requests.get') as get:
            cloud.return_value.cloudrequest.return_value = {'success': True, 'result': [{'map_type': 0, 'map_url': 'https://storage.example/map?signed=secret'}, {'map_type': 1, 'map_url': 'https://storage.example/path'}]}
            response = get.return_value.__enter__.return_value
            response.status_code = 200
            response.iter_content.side_effect = [[b'\x00\xffraw'], [b'path']]
            log = StringIO()
            call_command('download_map', output_dir=directory, stdout=log)
            cloud.return_value.cloudrequest.assert_called_once_with('/v1.0/users/sweepers/file/robot-test/realtime-map', action='GET')
            files = sorted(Path(directory).glob('*/*.bin'))
            self.assertEqual([p.read_bytes() for p in files], [b'\x00\xffraw', b'path'])
            self.assertTrue(all(stat.S_IMODE(p.stat().st_mode) == 0o600 for p in files))
            self.assertNotIn('signed', log.getvalue())
            self.assertFalse(get.call_args.kwargs['allow_redirects'])

    def test_missing_credentials_prevents_network(self):
        import os
        from django.core.management import call_command, CommandError
        with patch.dict(os.environ, {}, clear=True), patch('remote.management.commands.download_map.tinytuya.Cloud') as cloud:
            with self.assertRaises(CommandError):
                call_command('download_map')
            cloud.assert_not_called()

    def test_api_reject_and_unsafe_urls_do_not_download(self):
        import os
        from django.core.management import call_command, CommandError
        env = {'TUYA_CLIENT_ID': 'test', 'TUYA_CLIENT_SECRET': 'test', 'TUYA_REGION': 'eu', 'ROBOT_DEVICE_ID': 'test'}
        with patch.dict(os.environ, env), patch('remote.management.commands.download_map.tinytuya.Cloud') as cloud, patch('remote.management.commands.download_map.requests.get') as get:
            for response in [{'success': False, 'msg': 'private-secret'}, {'success': True, 'result': []}, {'success': True, 'result': [{'map_type': 0, 'map_url': 'http://storage.example/map'}]}]:
                cloud.return_value.cloudrequest.return_value = response
                with self.assertRaises(CommandError) as caught:
                    call_command('download_map')
                self.assertNotIn('private-secret', str(caught.exception))
            get.assert_not_called()

    def test_partial_download_removed(self):
        import os, tempfile
        from pathlib import Path
        from django.core.management import call_command, CommandError
        env = {'TUYA_CLIENT_ID': 'test', 'TUYA_CLIENT_SECRET': 'test', 'TUYA_REGION': 'eu', 'ROBOT_DEVICE_ID': 'test'}
        def chunks(*args):
            yield b'partial'
            raise OSError('signed-private-url')
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, env), patch('remote.management.commands.download_map.tinytuya.Cloud') as cloud, patch('remote.management.commands.download_map.requests.get') as get:
            cloud.return_value.cloudrequest.return_value = {'success': True, 'result': [{'map_type': 0, 'map_url': 'https://storage.example/map'}]}
            response = get.return_value.__enter__.return_value
            response.status_code = 200
            response.iter_content.side_effect = chunks
            with self.assertRaises(CommandError) as caught:
                call_command('download_map', output_dir=directory)
            self.assertNotIn('signed-private-url', str(caught.exception))
            self.assertEqual(list(Path(directory).iterdir()), [])
