from lib.exceptions import InvalidValueException

# Cast a string into int, ensure that it is greater than 0
def number_greater(number: str, message: str = 'Amount must be greater than 0') -> int:
    number = int(number)
    if number <= 0: raise InvalidValueException(message)
    return number