import RPi.GPIO as GPIO
from django.shortcuts import render

from control_lampara.utils import print_timestamp
from ledblink.forms import UserLedBlinkForm
from ledblink.models import ControlLamp

pin_number = 16
# GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pin_number, GPIO.OUT)


def get_pin_state():
    state = ControlLamp.objects.all()[0].state

    if int(state):
        return "On"
    else:
        return "Off"


def blinker(request):
    current_pin_state = get_pin_state()
    print_timestamp(message="Current pin {0} state: {1}".format(current_pin_state, pin_number))

    if request.method == 'POST':
        form = UserLedBlinkForm(request.POST or None)
        if form.is_valid():
            if int(request.POST['state']):
                print_timestamp(message="Turning On pin #" + str(pin_number))
                GPIO.output(pin_number, GPIO.LOW)
            else:
                print_timestamp(message="Turning Off pin #" + str(pin_number))
                GPIO.output(pin_number, GPIO.HIGH)

            if len(ControlLamp.objects.all()) > 1:
                # delete all registers
                ControlLamp.objects.all().delete()

            if len(ControlLamp.objects.all()) == 1:
                # update the register
                ControlLamp.objects.filter(pk=ControlLamp.objects.all()[0].pk).update(state=form.data['state'])

            if len(ControlLamp.objects.all()) == 0:
                # create a new register
                form.save()

            current_pin_state = get_pin_state()
    else:
        form = UserLedBlinkForm()

    context = {
        'status': current_pin_state,
        'form': form,
    }
    return render(request, 'control_page.html', context)
