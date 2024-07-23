from django.db import models

class Standart_Coin(models.Model):
    id = models.AutoField(primary_key=True)
    phase = models.DecimalField(max_digits=10, decimal_places=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    name_id = models.TextField()
    key_one = models.TextField()
    key_two = models.TextField(blank=True, null=True)
    encrypted_coin_str = models.TextField()
    encrypted_coin= models.TextField()


    def __str__(self):
        return f'Coin amount: {self.amount}'
    
class user_info(models.Model):
    email = models.TextField()
    encrypted_coin = models.TextField()
    delivered = models.BooleanField(default=False)

class withdraw(models.Model):
    wallet = models.TextField()
    encrypted_coin = models.TextField()
    status = models.BooleanField(default=False)

class CongregateForm(models.Model):
    num_inputs = models.IntegerField()
    coins_encrypted = models.TextField()
    keys_encrypted = models.TextField()