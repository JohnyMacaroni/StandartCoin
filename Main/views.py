from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
import sys
import os
from Main.models import Standart_Coin,user_info,withdraw
import json
import utils
from StandartCoin import settings
from cryptography.fernet import Fernet

import requests
from django.views.decorators.csrf import csrf_exempt
import hmac
import hashlib



#90016878-c107-46dd-9c39-48916882bfcb

#wallet btc :bc1qdnv5lta0f6gpd9hfm2kv3exv23962zujh53lcw
# wallet BNB :0xecfadd21cf0db805b06f0cb1667efd76135b233d
#wallet ethereum :0xecfadd21cf0db805b06f0cb1667efd76135b233d
#wallet usdt:TCmqfkuzeo1981xnJHu8zvjVqxKuS8nMBB
#wallet sol:93KNzWMZdUBZ4o5s782GWz7L9oRj6gvQYu6LMbPy5hcL

def main(request):
    return render(request, 'Main/main.html')

#verify_coin
def create_verify_page(request):  
    return render(request, 'Main/verify_coin.html')

def get_verify(request):
    if request.method == 'GET' :
            coin_text = request.GET.get('coin_text', '')
            key_two = request.GET.get('key', '')

            try:
                permission, coin_obj_con, coin_obj_al = verification(request, coin_text, key_two)

                if permission == True:

                    if coin_obj_con[0]:

                        id_coin = coin_obj_al.id
                        amount = utils.has_at_most_x_decimals(coin_obj_al.amount,2)
                        coin_obj_al.delete()

                        coin, coin_db, key_two = utils.create_coin(amount)

                        new_coin = Standart_Coin(id = id_coin, **coin_db)

                        new_coin.save()

                        # Exemplo de resposta JSON com as informações da moeda

                        response_data = {
                            'success': True,
                            'coin_info': coin,
                            'key':key_two
                        }

                        return render(request, 'Main/verify_coin.html', response_data)

            except Standart_Coin.DoesNotExist:
                # Caso a moeda não seja encontrada no banco de dados
                
                data = {
                    'success': False,
                    'error': f"Crypto Not Found.",
                    'coin_info': f"Crypto Not Found",
                }
                return JsonResponse(data)

            except Exception as e:
                # Captura qualquer outra exceção não prevista
                
                data = {
                    'success': False,
                    'error': f"Unable to verify",
                    'coin_info': f"Unable to verify",
                }
                return JsonResponse(data)

    else:
        # Se a requisição não for GET ou não for AJAX, retorne uma resposta de erro
        data = {
            'success': False,
            'error': "Requisição inválida para verificar moeda.",
        }
        return JsonResponse(data)

def verification(request,encrypted_coin,key):
    coin_obj_al = Standart_Coin.objects.get(encrypted_coin=encrypted_coin)
    key_one = coin_obj_al.key_one
    coin_obj_con = utils.verify_coin(coin_obj_al.encrypted_coin, key_one, key)

    if coin_obj_con[2]["phase"] == coin_obj_al.phase and float(coin_obj_con[2]["amount"]) == float(coin_obj_al.amount) and coin_obj_con[2]["name_id"] == coin_obj_al.name_id and coin_obj_con[2]["key_one"] == coin_obj_al.key_one :
        print("teste2")
        return (True, coin_obj_con, coin_obj_al)
    
    return False

#create_coin
def create_coin_page(request):  
    return render(request, 'Main/create_coin.html',{'policy':utils.get_policy(),'rate':utils.get_rate()})

def get_coin(request):
    try:
        if request.method == 'GET':
            amount = request.GET.get('amount')
            crypto =  request.GET.get('crypto')
            email = request.GET.get('email')
            
            if amount and float(amount)>0:
                amount = utils.has_at_most_x_decimals(amount,2)
                crypto = utils.crypto(crypto)
                
                if amount and crypto and email:
                    
                    try:

                        # Example: Creating a coin and saving it to the database
                        coin, coin_db, key_two = utils.create_coin(amount)

                        new_coin = Standart_Coin(**coin_db)
                        
                        new_email = user_info(email=str(email),encrypted_coin=coin)

                        new_email.save()
                        new_coin.save()

                        
                        # Construct the JSON response

                        response_data = {
                            'payment_info': crypto,
                            'wallet_adress': "html",
                            'policy': utils.get_policy(),
                            'rate':utils.get_rate()
                        }
                        
                        return render(request, 'Main/create_coin.html', response_data)
                    except Exception as e:
                        return JsonResponse({'error': 'error'}, status=400)
                else:
                    return JsonResponse({'error': 'Amount not provided','coin_info':'No coin information available'}, status=401)
            else:
                return JsonResponse({'error': 'Amount not provided','coin_info':'No coin information available'}, status=401)
        else:
            return JsonResponse({'error': 'Invalid request method','coin_info':'No coin information available'}, status=405)
    except Exception as e:
        return JsonResponse({'error': "Exception",'coin_info':"error"}, status=410)

#sell_coin
def create_sell_page(request):
    return render(request,'Main/sell_coin.html',{'policy':utils.get_policy(),'rate':utils.get_rate()})

def get_sell(request):
    try:
        if request.method == 'GET':
            wallet = request.GET.get('wallet_info')
            crypto =  request.GET.get('encrypted_coin')
            key_two =  request.GET.get('key')
            

            try:
                permission, coin_obj_con, coin_obj_al = verification(request, crypto, key_two)
                
                if permission == True:
                    
                    id_coin = coin_obj_al.id
                    withdraw_object = withdraw(wallet=wallet,encrypted_coin=coin_obj_al.encrypted_coin)
                    coin_obj_al.delete()

                    withdraw_object.save()
                    response_data = {
                        'process':'Sucess',
                        'policy': utils.get_policy(),
                        'rate':utils.get_rate()
                    }
                    
                    return render(request, 'Main/sell_coin.html', response_data)
            except Exception as e:
                return JsonResponse({'error': 'Invalid request method','coin_info':'No coin information available'}, status=400)
                
        else:
            return JsonResponse({'error': 'Invalid request method','coin_info':'No coin information available'}, status=405)
    except Exception as e:
        return JsonResponse({'error': "Exception",'coin_info':'error'}, status=410)

def coin_list(request):
    coins = Standart_Coin.objects.all()
    return render(request, 'Main/coins.html', {'coins': coins})


COINBASE_API_URL = 'https://api.commerce.coinbase.com/checkouts'
COINBASE_API_KEY = '90016878-c107-46dd-9c39-48916882bfcb'

def create_payment(request):
    if request.method == 'GET':
        amount = request.GET.get('amount')
        crypto_type = request.GET.get('crypto')

        headers = {
            'Content-Type': 'application/json',
            'X-CC-Api-Key': COINBASE_API_KEY
        }

        data = {
            "name": "Coin Purchase",
            "description": "Buying our custom coins",
            "pricing_type": "fixed_price",
            "local_price": {
                "amount": amount,
                "currency": "USD"
            },
            "requested_info": ["email"]
        }

        response = requests.post(COINBASE_API_URL, headers=headers, json=data)

        if response.status_code == 201:
            checkout = response.json()
            checkout_id = checkout['data']['id']
            checkout_url = f"https://commerce.coinbase.com/checkout/{checkout_id}"
            context = {
                'checkout_url': checkout_url,
                'crypto_type': crypto_type,
                'amount': amount,
                #'order_id': checkout_id
            }
            return render(request, 'Main/create_coin.html', context)
        else:
            return HttpResponse('Error creating checkout', status=500)
    return render(request, 'Main/create_coin.html')


@csrf_exempt
def payment_webhook(request):
    if request.method == 'POST':
        event = json.loads(request.body)

        if event['event']['type'] == 'charge:confirmed':
            order_id = event['event']['data']['metadata']['order_id']
            amount = event['event']['data']['metadata']['amount']
            email = event['event']['data']['metadata']['email']
            print(order_id)
            # Handle confirmed payment and send the coin
            print("done")
            get_coin(amount,order_id,email)
            
            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failure'})


#congregate_coin
def create_congregate_page(request):
    return render(request, 'Main/congregate.html')

def congregate_coins(request):
    if request.method == 'GET':
        try:
            # Retrieve and split the input fields
            coin_texts = request.GET.get('coins', '').split(';')
            key_texts = request.GET.get('keys', '').split(';')
            if len(coin_texts) != len(key_texts):
                return JsonResponse({'error': 'The number of coins and keys must match.'}, status=400)

            total_amount = 0.0
           
            for coin_text, key_text in zip(coin_texts, key_texts):
                crypto = coin_text.strip()
                key = key_text.strip()

                if not coin_text or not key_text:
                    continue

                try:
                    # Decrypt and verify the coin using the provided key
                    encrypted_coin_final = coin_text
                    permission, coin_obj_con, coin_obj_al = verification(request, crypto, key)

                    if permission:
                        total_amount += float(coin_obj_al.amount)
                    else:
                        return JsonResponse({'error': f'Permission denied for coin with text {encrypted_coin_final}.'}, status=403)

                except Standart_Coin.DoesNotExist:
                    return JsonResponse({'error': f'Coin with text {encrypted_coin_final} does not exist.'}, status=400)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)

            # Create a new coin with the aggregated amount
            coin, coin_db, key_two = utils.create_coin(total_amount)  # Assuming key_text is used for the new coin
            

            new_coin = Standart_Coin(**coin_db)

            new_coin.save()
            
            for coin_text, key_text in zip(coin_texts, key_texts):
                crypto = coin_text.strip()
                key = key_text.strip()

                if not coin_text or not key_text:
                    continue

                try:
                    # Decrypt and verify the coin using the provided key
                    encrypted_coin_final = coin_text
                    permission, coin_obj_con, coin_obj_al = verification(request, crypto, key)

                    if permission:
                        coin_obj_al.delete()
                    else:
                        return JsonResponse({'error': f'Permission denied for coin with text {encrypted_coin_final}.'}, status=403)

                except Standart_Coin.DoesNotExist:
                    return JsonResponse({'error': f'Coin with text {encrypted_coin_final} does not exist.'}, status=400)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)
            
            response_data = {
                'success': True,
                'coin_info': coin,
                'key':key_two
            }

            return render(request, 'Main/congregate.html', response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'congregate.html')


#divide_coin
def create_divide_page(request):
    return render(request, 'Main/divide.html')

def divide_coin(request):
    if request.method == 'POST':
        try:
            times = int(request.POST.get('times', 1))
            coin_text = request.POST.get('coin', '').strip()

            try:
                coin = Standart_Coin.objects.get(encrypted_coin_final=coin_text)
                
                if coin.amount % times != 0:
                    return JsonResponse({'error': 'The coin amount cannot be evenly divided by the given number of times.'}, status=400)

                divided_amount = coin.amount / times
                new_coins = []
                for _ in range(times):
                    new_coin = Standart_Coin(amount=divided_amount, encrypted_coin_final="some_encrypted_value")
                    new_coins.append(new_coin)
                    new_coin.save()

                return JsonResponse({'success': True, 'new_coins': [coin.encrypted_coin_final for coin in new_coins]})

            except Standart_Coin.DoesNotExist:
                return JsonResponse({'error': 'Coin does not exist.'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'divide.html')