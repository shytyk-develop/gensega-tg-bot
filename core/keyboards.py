from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- Main menu ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔒 Encrypt"),
            KeyboardButton(text="🔓 Decrypt")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Choose an action..."
)

# --- Cancel button ---
cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Cancel")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Enter data or press Cancel"
)

# --- Image mode selection ---
image_selection_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎲 Generate pattern")],
        [KeyboardButton(text="🔙 Cancel")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Send a photo or click 'Generate pattern'"
)