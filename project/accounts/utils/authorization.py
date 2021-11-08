import binascii
import os


def generate_token() -> str:
    """
    Generates an unique token.
    """
    return binascii.hexlify(os.urandom(40)).decode()
