from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from .robot import Robot, RobotError

@login_required
def dashboard(request):
    status, error = {}, ''
    try:
        status = Robot().status()
    except RobotError as exc:
        error = str(exc)
    labels = {'cleaning': 'Limpiando', 'docking': 'Volviendo a la base', 'charging': 'Cargando', 'paused': 'En pausa'}
    return render(request, 'remote/dashboard.html', {'demo': settings.ROBOT_DEMO, 'error': error, 'battery': status.get('14', '—'), 'state': labels.get(status.get('28'), status.get('28', 'Sin datos')), 'mode': status.get('27', '—'), 'suction': status.get('30', '—'), 'area': status.get('32', '—'), 'duration': status.get('33', '—'), 'alarm': status.get('11')})

@login_required
@require_POST
def command(request, action):
    if action not in ('start', 'stop', 'dock'):
        return HttpResponseBadRequest('Comando desconocido')
    try:
        Robot().command(action)
        messages.success(request, {'start': 'Orden de inicio enviada.', 'stop': 'Orden de parada enviada.', 'dock': 'Orden de regreso a la base enviada.'}[action])
    except RobotError as exc:
        messages.error(request, str(exc))
    return redirect('dashboard')
