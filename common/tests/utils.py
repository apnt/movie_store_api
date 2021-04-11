import string
import random


def get_random_string(length=32, use_lowercase=True, use_uppercase=True, use_digits=True, use_punctuation=True):
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    punctuation = string.punctuation

    chars_to_use = ''
    chars_to_use += lowercase if use_lowercase else ''
    chars_to_use += uppercase if use_uppercase else ''
    chars_to_use += digits if use_digits else ''
    chars_to_use += punctuation if use_punctuation else ''

    chars = list(chars_to_use)
    random.shuffle(chars)
    return ''.join(random.choices(chars, k=length))