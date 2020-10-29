from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from manager.models import Account

class RegistrationForm(UserCreationForm):
    """RegistrationForm definition."""
    email = forms.EmailField(max_length=60,help_text="Add a valid email address")
    
    class Meta:
        model = Account
        fields = ["email","username","password1","password2"]

class AccountAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label="password",widget=forms.PasswordInput)
    
    class Meta:
        model = Account
        fields = ["email","password"]

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        if not authenticate(email=email,password=password):
            return forms.ValidationError('Invalid Login')

class NewTransactionForm(forms.Form):
    """NewTransactionForm definition."""

    # TODO: Define form fields here
    receiver = forms.CharField()
    amount = forms.FloatField()

    class Meta:
        fields = ['receiver','amount']


class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['username']

    def clean_username(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            try:
                _ = Account.objects.exclude(pk=self.instance.pk).get(username='username')
            except Account.DoesNotExist:
                return username
            raise forms.ValidationError(f'username {username} is already use.')
