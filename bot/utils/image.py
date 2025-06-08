from PIL import Image, ImageDraw, ImageFont
from collections import defaultdict

def get_best_status(statuses):
    # Priority order
    priority = {'matching': 3, 'misplaced': 2, 'absent': 1}
    best = 'absent'
    for s in statuses:
        if priority[s] > priority[best]:
            best = s
    return best

def _generate_wordle_game_state_image(guesses, results, filepath, word_length=5, max_attempts=6, box_size=50, padding=5, side_padding = 150, keyboard_top_margin = 10):
    keyboard = [
        ["Q","W","E","R","T","Y","U","I","O","P"],
        ["A","S","D","F","G","H","J","K","L"],
        ["Z","X","C","V","B","N","M"]
    ]

    key_width = 50
    key_height = 50
    key_padding = 6
    
    keyboard_height = (key_height + key_padding) * len(keyboard)
    grid_width = word_length * (box_size + padding) + padding + side_padding * 2
    grid_height = max_attempts * (box_size + padding) + padding
    total_height = grid_height + keyboard_height + keyboard_top_margin

    image = Image.new("RGB", (grid_width, total_height), color="white")
    draw = ImageDraw.Draw(image)

    colors = {
        'matching': (106, 170, 100),
        'misplaced': (201, 180, 88),
        'absent': (120, 124, 126),
        'empty': (211, 214, 218),
    }

    try:
        font = ImageFont.truetype("./utils/assets/arial.ttf", 18)
        key_font = ImageFont.truetype("./utils/assets/arial.ttf", 18)
    except IOError:
        font = ImageFont.load_default()
        key_font = ImageFont.load_default()

    # Draw the board
    for row in range(max_attempts):
        for col in range(word_length):
            x = padding + col * (box_size + padding) + side_padding
            y = padding + row * (box_size + padding)

            if row < len(guesses):
                # Accommodate longdle
                if col < len(guesses[row]):
                    char = guesses[row][col]
                    status = results[row][col]
                else:
                    char = ''
                    status = 'empty'
                color = colors[status]
            else:
                char = ''
                color = colors['empty']

            draw.rectangle([x, y, x + box_size, y + box_size], fill=color, outline=(0, 0, 0), width=2)

            if char:
                bbox = font.getbbox(char.upper())
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                draw.text((x + (box_size - w)/2, y + (box_size - h)/2 - 5), char.upper(), fill="white", font=font)

    # Build a map of letter to best status
    letter_statuses = defaultdict(list)
    for guess, fb in zip(guesses, results):
        for c, s in zip(guess.upper(), fb):
            letter_statuses[c].append(s)
    letter_colors = {c: colors[get_best_status(v)] for c, v in letter_statuses.items()}

    # Draw the keyboard
    y_offset = grid_height + keyboard_top_margin
    for r_idx, row_keys in enumerate(keyboard):
        row_width = len(row_keys) * (key_width + key_padding)
        x_offset = (grid_width - row_width) // 2
        for k_idx, key in enumerate(row_keys):
            x = x_offset + k_idx * (key_width + key_padding)
            y = y_offset + r_idx * (key_height + key_padding)

            color = letter_colors.get(key, colors['empty'])
            draw.rectangle([x, y, x + key_width, y + key_height], fill=color, outline=(0, 0, 0), width=2)

            bbox = key_font.getbbox(key)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text((x + (key_width - w)/2, y + (key_height - h)/2 - 2), key, fill="white", font=key_font)
    
    image.save(filepath)

def generate_wordle_image(guesses, results, user_id):
    filename = f'wordle_{user_id}.png'
    filepath = f'/tmp/{filename}'
    _generate_wordle_game_state_image(guesses, results, filepath=filepath, word_length=5, max_attempts=6)
    return filename, filepath

def generate_longdle_image(guesses, results, user_id, length):
    filename = f'longdle_{user_id}.png'
    filepath = f'/tmp/{filename}'
    _generate_wordle_game_state_image(guesses, results, filepath=filepath, word_length=length, max_attempts=length + 1, padding=7, keyboard_top_margin=5 + length, side_padding=(150 - ((length - 6) * 15)))
    return filename, filepath