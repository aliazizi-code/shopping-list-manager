import random
import string


def generate_otp():
    rand = random.SystemRandom()
    digits = rand.choices(string.digits, k=6)
    return ''.join(digits)
