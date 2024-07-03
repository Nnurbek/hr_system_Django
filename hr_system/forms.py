from django import forms
from django.utils.translation import gettext_lazy as _
from .models import EmployeeProfile, Notification
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': _('Пайдаланушы аты'),
            'first_name': _('Аты'),
            'last_name': _('Тегі'),
            'email': _('Электрондық пошта'),
        }

class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ['position', 'hourly_rate']
        labels = {
            'position': _('Лауазымы'),
            'hourly_rate': _('Сағаттық ставка'),
        }


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_('Құпия сөз'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Құпия сөзді растау'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': _('Пайдаланушы аты'),
            'first_name': _('Аты'),
            'last_name': _('Тегі'),
            'email': _('Электрондық пошта'),
        }
        help_texts = {
            'username': _('Міндетті. 150 таңбадан аспауы керек. Әріптер, сандар және @/./+/-/_ ғана.'),
        }
        error_messages = {
            'username': {
                'max_length': _("Бұл пайдаланушы аты тым ұзақ."),
            },
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Құпия сөздер сәйкес келмейді'))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user




class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['recipient', 'message']
