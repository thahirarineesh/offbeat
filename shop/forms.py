# forms.py
from django import forms

from offbeatapp.models import Customer
from shop.models import Address, Profile

class UserForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'username',
            'number',
            'email',
        ]
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profile_photo',
            'number',

        ]
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user',"is_deleted"]

    def _init_(self, *args, **kwargs):
        super(AddressForm, self)._init_(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] ="form-control"

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)
