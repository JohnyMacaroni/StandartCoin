from django import forms
from .models import Standart_Coin

class CoinForm(forms.ModelForm):
    class Meta: 
        model = Standart_Coin
        fields = ['amount', 'encrypted_coin_str', 'encrypted_coin' ]