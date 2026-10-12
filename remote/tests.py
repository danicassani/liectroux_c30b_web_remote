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
