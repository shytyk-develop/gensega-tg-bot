import io
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, ReplyKeyboardRemove
from PIL import Image

# Import utilities
from core.crypto_utils import encrypt_data, decrypt_data, embed_data, extract_data
from core.image_utils import generate_cover_image
# Import keyboards
from core.keyboards import main_kb, cancel_kb, image_selection_kb

router = Router()

# --- FSM ---
class EncodeState(StatesGroup):
    waiting_for_text = State()          
    waiting_for_password = State()      
    waiting_for_method_choice = State() 
    waiting_for_upload = State()        

class DecodeState(StatesGroup):
    waiting_for_file = State()
    waiting_for_pass = State()

# --- GLOBAL CANCEL ---
@router.message(F.text == "🔙 Cancel")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Action cancelled.\nYou're back to the main menu.",
        reply_markup=main_kb
    )

# --- START ---
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🕵️‍♂️ StegoBot\n\n"
        "I turn your secrets into images.\n"
        "Choose an action from the menu below:",
        reply_markup=main_kb
    )

# ==========================================
# ENCRYPTION LOGIC (ENCODE)
# ==========================================

@router.message(F.text == "🔒 Encrypt")
@router.message(Command("encode"))
async def start_encode(message: types.Message, state: FSMContext):
    await message.answer(
        "✍️ **Step 1/3:** Enter the secret text you want to hide:",
        reply_markup=cancel_kb
    )
    await state.set_state(EncodeState.waiting_for_text)

@router.message(EncodeState.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    await state.update_data(secret_text=message.text)
    await message.answer(
        "🔑 **Step 2/3:** Create a password for encryption:",
        reply_markup=cancel_kb
    )
    await state.set_state(EncodeState.waiting_for_password)

@router.message(EncodeState.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    
    # This is the Step 3/3 request with buttons
    await message.answer(
        "🖼 **Step 3/3**\n\nChoose the way to encrypt:",
        reply_markup=image_selection_kb
    )
    # Transition to method choice state
    await state.set_state(EncodeState.waiting_for_method_choice)

# --- CHOICE: GENERATION ---
@router.message(EncodeState.waiting_for_method_choice, F.text == "🎲 Generate pattern")
async def process_generate(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg = await message.answer("🎨 Creating a unique pattern...", reply_markup=ReplyKeyboardRemove())
    
    try:
        # Generate
        image_bytes = await generate_cover_image()
        
        # Encrypt
        encrypted_data = encrypt_data(data['secret_text'], data['password'], ttl_minutes=60)
        stego_bytes = embed_data(image_bytes, encrypted_data)
        
        input_file = BufferedInputFile(stego_bytes, filename="secret_generated.png")
        await message.answer_document(
            input_file, 
            caption="✅ **Secret hidden!**\nSave this file as a document.",
            reply_markup=main_kb
        )
        await msg.delete()
    except Exception as e:
        await message.answer(f"❌ Error: {e}", reply_markup=main_kb)
        
    await state.clear()

# --- CHOICE: SEND PHOTO (Transition to upload) ---
@router.message(EncodeState.waiting_for_method_choice, F.text == "📤 Send photo")
async def intent_send_photo(message: types.Message, state: FSMContext):
    await message.answer(
        "📸 **Waiting for photo**\n\n"
        "Send an image (as photo or file).\n"
        "I'll hide the text inside it.",
        reply_markup=cancel_kb # Keep Cancel button
    )
    # Switch state to waiting for upload
    await state.set_state(EncodeState.waiting_for_upload)

# --- PROCESS UPLOADED PHOTO ---
@router.message(EncodeState.waiting_for_upload, F.photo | F.document)
async def process_custom_image(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    # Logic for getting file
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        if not message.document.mime_type.startswith('image/'):
            await message.answer("⛔ This is not an image. Try again.", reply_markup=cancel_kb)
            return
        file_id = message.document.file_id
    else:
        await message.answer("I'm waiting for an image.", reply_markup=cancel_kb)
        return

    status_msg = await message.answer("📥 Downloading and processing...", reply_markup=ReplyKeyboardRemove())

    try:
        file = await message.bot.get_file(file_id)
        file_io = io.BytesIO()
        await message.bot.download_file(file.file_path, file_io)
        
        # Convert to PNG
        img = Image.open(file_io).convert("RGB")
        png_io = io.BytesIO()
        img.save(png_io, format="PNG")
        image_bytes = png_io.getvalue()
        
        # Encrypt
        encrypted_data = encrypt_data(data['secret_text'], data['password'], ttl_minutes=60)
        stego_bytes = embed_data(image_bytes, encrypted_data)
        
        input_file = BufferedInputFile(stego_bytes, filename="secret_photo.png")
        await message.answer_document(
            input_file, 
            caption="✅ **Done!**\nText is hidden inside the file.",
            reply_markup=main_kb
        )
        await status_msg.delete()
        
    except Exception as e:
        await message.answer(f"❌ Error: {e}", reply_markup=main_kb)
    
    await state.clear()



# ==========================================
# DECRYPTION LOGIC (DECODE)
# ==========================================

@router.message(F.text == "🔓 Decrypt")
@router.message(Command("decode"))
async def start_decode(message: types.Message, state: FSMContext):
    await message.answer(
        "📂 Send me a **PNG file** with a hidden secret.",
        reply_markup=cancel_kb
    )
    await state.set_state(DecodeState.waiting_for_file)

@router.message(DecodeState.waiting_for_file, F.photo)
async def reject_photo_decode(message: types.Message):
    await message.answer(
        "📛 **You sent a photo!**\nTelegram compressed it and deleted the secret.\nPlease send it as a **File (Document)**.",
        reply_markup=cancel_kb
    )

@router.message(DecodeState.waiting_for_file, F.document)
async def process_decode_file(message: types.Message, state: FSMContext):
    if message.document.mime_type != "image/png":
        await message.answer("📛 Only PNG file is needed.", reply_markup=cancel_kb)
        return

    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    file_io = io.BytesIO()
    await message.bot.download_file(file.file_path, file_io)
    
    await state.update_data(file_bytes=file_io.getvalue())
    await message.answer(
        "🔑 Enter the message password:",
        reply_markup=cancel_kb
    )
    await state.set_state(DecodeState.waiting_for_pass)

@router.message(DecodeState.waiting_for_pass)
async def process_decode_pass(message: types.Message, state: FSMContext):
    password = message.text
    data = await state.get_data()
    
    try:
        extracted = extract_data(data['file_bytes'])
        text = decrypt_data(extracted, password)
        await message.answer(text, reply_markup=main_kb)
    except Exception:
        await message.answer(
            "❌ Could not decrypt.\nWrong password or file is corrupted.",
            reply_markup=main_kb
        )
    
    await state.clear()