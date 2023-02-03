from django import forms
from models import *


class RoomForm(forms.Form):
    number = forms.CharField(max_length=10)
    capacity = forms.IntegerField()
    appointment = forms.ChoiceField(choices=[("Seminars", "Семинар"), ("Lectures", "Лекция"),
                                                           ("Laboratory", "Лаборатория"), ("Terminal", "Терминал")])