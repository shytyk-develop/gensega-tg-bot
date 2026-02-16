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
    input_field_placeholder="Press to cancel"
)

# --- Step 3/3: Choose method ---
image_selection_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📤 Send photo"),
            KeyboardButton(text="🎲 Generate pattern")
        ],
        [KeyboardButton(text="🔙 Cancel")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Choose method..."
)