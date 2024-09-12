from lib.exceptions import InvalidValueException

def number_g(number: str, message: str = 'Amount must be greater than 0') -> int:
    number = int(number)
    if number <= 0: raise InvalidValueException(message)
    return number