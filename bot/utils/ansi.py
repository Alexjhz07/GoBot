from enum import Enum
from pydoc import text

class ANSI_Style(Enum):
    normal = 0
    bold = 1
    underline = 4
    bold_underline = '1;4'
    underline_bold = '1;4'

    @classmethod
    def from_str(cls, name: str):
        try:
            return cls[name.lower()]  # Converts input to lower to match enum keys
        except KeyError:
            raise ValueError(f"'{name}' is not a valid style. Available styles: {[c.name for c in cls]}")

class ANSI_Background(Enum):
    grey_light = 46
    grey = 44
    grey_medium = 43
    grey_dark = 42
    blue_dark = 40
    orange = 41
    indigo = 45
    white = 47

    @classmethod
    def from_str(cls, name: str):
        try:
            return cls[name.lower()]  # Converts input to lower to match enum keys
        except KeyError:
            raise ValueError(f"'{name}' is not a valid background color. Available colors: {[c.name for c in cls]}")

class ANSI_Color(Enum):
    grey = 30
    red = 31
    green = 32
    yellow = 33
    blue = 34
    pink = 35
    cyan = 36
    white = 37

    @classmethod
    def from_str(cls, name: str):
        try:
            return cls[name.lower()]  # Converts input to lower to match enum keys
        except KeyError:
            raise ValueError(f"'{name}' is not a valid text color. Available colors: {[c.name for c in cls]}")

def get_ansi_block(text: str, style = ANSI_Style.normal, background = None, color = ANSI_Color.white):
    return f"```ansi\n{get_ansi_raw(text, style, background, color)}```"
    
def get_ansi_raw(text: str, style = ANSI_Style.normal, background = None, color = ANSI_Color.white):
    if background:
        return f"\u001b[{style.value};{background.value};{color.value}m{text}\u001b[0m"
    else:
        return f"\u001b[{style.value};{color.value}m{text}\u001b[0m"

def get_rainbow_table():
    lines = []

    lines.append(get_ansi_raw("ANSI Styles", style=ANSI_Style.bold_underline))
    for style in ANSI_Style:
        lines.append(get_ansi_raw(style.name, style=style))
    lines.append('')
    
    lines.append(get_ansi_raw("ANSI Text Colors", style=ANSI_Style.bold_underline))
    for color in ANSI_Color:
        lines.append(get_ansi_raw(color.name, color=color))
    lines.append('')

    lines.append(get_ansi_raw("ANSI Background Colors", style=ANSI_Style.bold_underline))
    for background in ANSI_Background:
        lines.append(get_ansi_raw(background.name, background=background))
    lines.append('')

    lines.append(get_ansi_raw("ANSI rainbow", style=ANSI_Style.bold_underline))
    for color in ANSI_Color:
        line = []
        for background in ANSI_Background:
            line.append(get_ansi_raw("Rainbow", background=background, color=color))
        lines.append(' '.join(line))

    text = '\n'.join(lines)
    text = f"```ansi\n{text}```"

    return text