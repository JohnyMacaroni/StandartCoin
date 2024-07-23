from cryptography.fernet import Fernet
import json
import string
import secrets
import base64
import hashlib

from decimal import Decimal, ROUND_HALF_UP

# Function to generate a new encryption key
def generate_key():
    return Fernet.generate_key()


def generate_secure_string(length):
    if length < 4:
        raise ValueError("String length should be at least 4")

    # Define characters excluding specific ones
    characters = string.ascii_letters + string.digits + string.punctuation.replace('-', '').replace(';', '')
    
    # Ensure at least one character of each type
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation.replace('-', '').replace(';', ''))
    ]

    # Add remaining characters
    password += [secrets.choice(characters) for _ in range(length - 4)]
    
    # Shuffle to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)
    
    # Join the list into a string
    return ''.join(password)


# Function to create a new coin
def create_coin(amount):
    secure_string = generate_secure_string(32)  # Ensure the string is long enough
    
    # Hash the secure string to get a 32-byte digest
    hashed_string = hashlib.sha256(secure_string.encode()).digest()

    # Base64 encode the hashed string to make it URL-safe
    fernet_key = base64.urlsafe_b64encode(hashed_string)
    fernet_key_string = fernet_key.decode()
    fernet = Fernet(fernet_key)

    phase_copy = phase  = 1
    amount_copy = float(amount)
    name_id_copy= name_id = generate_secure_string(52)
    key_one = key_one_copy = fernet_key_string[0:22]
    key_two = fernet_key_string[22:]
    coin = {
        "phase": 1,
        "amount": amount_copy,
        "name_id": name_id_copy,
        "key_one": key_one_copy
    }

    coin_str = json.dumps(coin)

    encrypted_coin = fernet.encrypt(coin_str.encode())  # Convert string to bytes

    encrypted_coin_str = encrypted_coin.decode()
    
    encrypted_coin = f"{amount}---{encrypted_coin_str}"

    val = {
        "phase":phase,
        "amount": float(amount),
        "name_id": name_id,
        "key_one": key_one,
        "key_two": key_two,
        "encrypted_coin_str": encrypted_coin_str,
        "encrypted_coin": encrypted_coin
    }

    return encrypted_coin, val, key_two

# Function to verify a coin

def verify_coin(encrypted_coin, key_one, key_two):
    try:
        key = "{}{}".format(key_one, key_two)
        fernet = Fernet(key)
    

        # Split the string to extract amount and encrypted data
        amount_str, division, encrypted_data = encrypted_coin.partition('---')
        
        # Convert amount back to integer (if needed)
        amount = float(amount_str)
        
        # Decrypt the encrypted data
        decrypted_data = fernet.decrypt(encrypted_data.encode()).decode()
        
        # Parse the decrypted JSON data
        coin = json.loads(decrypted_data)
        
        # Return tuple (amount, decrypted_coin_data)
        encrypted = (True, amount, coin)

        return encrypted
    
    except Exception as e:
        print(f"Error verifying coin: {e}")
        return False


def get_real_price():
    pass

def get_policy():
    one = 'Neutral'
    two = 'Tighten'
    three = 'Relaxed'
    four = 'Not intervening'
    return four

def crypto(crypto):
    crypto_list = ["BTC","SOL","BNB","ETH","USDT"]
    for crypto_n in crypto_list:
        if crypto == crypto_n:
            return crypto
    return False

def get_rate():
    return float(0.93)

def has_at_most_x_decimals(amount,x):
    # Convert amount to string to handle different number formats
    amount_str = str(amount)

    # Check if there is a decimal point
    if '.' in amount_str:
        # Split the string based on the decimal point
        integer_part, decimal_part = amount_str.split('.')
        
        # Check if the length of the decimal part is at most 3
        if len(decimal_part) <= x:
            try:
                formatted_str = "{:.2f}".format(float(amount_str))
                return str(formatted_str)
            except ValueError:
                # Handle the case where input_str cannot be converted to float
                return False  # Return the original input if it's not a valid number
    elif int(amount):
        
        return f"{amount}.00"
    # If there is no decimal point or the decimal part is longer than 3
    return False