# forms.py

from django import forms
from .models import Customer, Meeting


class CustomerForms(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"


class MeetingForms(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = "__all__"