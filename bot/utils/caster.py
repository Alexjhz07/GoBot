from lib.exceptions import InvalidValueException
from datetime import datetime

# Cast a string into int, ensure that it is greater than 0
def str_number_greater(number: str, message: str = 'Amount must be greater than 0') -> int:
    number = int(number)
    if number <= 0: raise InvalidValueException(message)
    return number

# Cast a string representing a date to be a human readable time until string
def str_time_until(date_string: str) -> str:
    if len(date_string) < 32: date_string = date_string[:23] # Conversion items for misformatted times
    
    time = datetime.fromisoformat(date_string).replace(tzinfo=None)
    interval = time - datetime.now()
    days = interval.days
    hours = interval.seconds // 3600
    minutes = (interval.seconds % 3600) // 60
    seconds = interval.seconds % 60
    
    if days > 0:
        return f'{days} day{pluralize(days)} {hours} hour{pluralize(hours)}'
    elif hours > 0:
        return f'{hours} hour{pluralize(hours)} {minutes} minute{pluralize(minutes)}'
    elif minutes > 0:
        return f'{minutes} minute{pluralize(minutes)} {seconds} second{pluralize(seconds)}'
    else:
        return f'{seconds} second{pluralize(seconds)}'

# Return 's' if number is plural (greater than 1) else empty string
def pluralize(value: int):
    if value > 1: 
        return 's'
    else:
        return ''