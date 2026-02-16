import io
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile
from PIL import Image

from core.crypto_utils import encrypt_data, decrypt_data, embed_data, extract_data
from core.image_utils import generate_cover_image

router = Router()

class EncodeState(StatesGroup):
    waiting_for_text = State()
    waiting_for_password = State()
    waiting_for_image = State()

class DecodeState(StatesGroup):
    waiting_for_file = State()
    waiting_for_pass = State()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🕵️‍♂️ **StegoBot (Offline Mode)**\n\n"
        "I turn your secrets into images.\n"
        "🔒 /encode — Encrypt message\n"
        "🔓 /decode — Decrypt message\n\n"
        "Bot works completely offline, no AI."
    )

@router.message(Command("encode"))
async def start_encode(message: types.Message, state: FSMContext):
    await message.answer("✍️ Enter secret text:")
    await state.set_state(EncodeState.waiting_for_text)

@router.message(EncodeState.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    await state.update_data(secret_text=message.text)
    await message.answer("🔑 Enter password:")
    await state.set_state(EncodeState.waiting_for_password)

@router.message(EncodeState.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.answer(
        "🖼 **Choose container:**\n\n"
        "1. 📸 **Send me a photo** (compressed is OK).\n"
        "   I'll convert it to PNG and hide the text there.\n\n"
        "2. 🎲 Type /generate, and I'll draw an image myself."
    )
    await state.set_state(EncodeState.waiting_for_image)

@router.message(EncodeState.waiting_for_image, F.photo | F.document)
async def process_custom_image(message: types.Message, state: FSMContext):
    data = await state.get_data()
    secret_text = data['secret_text']
    password = data['password']
    
    if message.photo:
        file_id = message.photo[-1].file_id
        info_msg = await message.answer("📥 Received photo. Converting to PNG...")
    elif message.document:
        if not message.document.mime_type.startswith('image/'):
            await message.answer("⛔ This is not an image.")
            return
        file_id = message.document.file_id
        info_msg = await message.answer("📥 Received file. Processing...")
    else:
        return

    try:
        file = await message.bot.get_file(file_id)
        file_io = io.BytesIO()
        await message.bot.download_file(file.file_path, file_io)

        img = Image.open(file_io).convert("RGB")
        png_io = io.BytesIO()
        img.save(png_io, format="PNG")
        image_bytes = png_io.getvalue()
        
        encrypted_data = encrypt_data(secret_text, password, ttl_minutes=60)
        stego_bytes = embed_data(image_bytes, encrypted_data)
        
        input_file = BufferedInputFile(stego_bytes, filename="secret_msg.png")
        await message.answer_document(
            input_file, 
            caption="✅ **Secret hidden!**\nSave this file.\n(Original photo doesn't contain data, only this file)."
        )
        await info_msg.delete()
        
    except Exception as e:
        await message.answer(f"❌ Error: {e}")
    
    await state.clear()

@router.message(EncodeState.waiting_for_image, Command("generate"))
async def process_generate(message: types.Message, state: FSMContext):
    data = await state.get_data()
    secret_text = data['secret_text']
    password = data['password']
    
    msg = await message.answer("🎨 Drawing pattern...")
    
    try:
        image_bytes = await generate_cover_image()
        
        encrypted_data = encrypt_data(secret_text, password, ttl_minutes=60)
        stego_bytes = embed_data(image_bytes, encrypted_data)
        
        input_file = BufferedInputFile(stego_bytes, filename="secret_generated.png")
        await message.answer_document(
            input_file, 
            caption="✅ **Secret hidden!**\nImage created by bot."
        )
        await msg.delete()
    except Exception as e:
        await message.answer(f"❌ Error: {e}")
        
    await state.clear()

@router.message(Command("decode"))
async def start_decode(message: types.Message, state: FSMContext):
    await message.answer("📂 Send **PNG file** with secret.")
    await state.set_state(DecodeState.waiting_for_file)

@router.message(DecodeState.waiting_for_file, F.photo)
async def reject_photo_decode(message: types.Message):
    await message.answer(
        "📛 **Can't send as photo!**\n"
        "Telegram compressed the image and destroyed the secret.\n"
        "Send file as **Document** (uncompressed)."
    )

@router.message(DecodeState.waiting_for_file, F.document)
async def process_decode_file(message: types.Message, state: FSMContext):
    if message.document.mime_type != "image/png":
        await message.answer("📛 Need PNG file only.")
        return

    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    file_io = io.BytesIO()
    await message.bot.download_file(file.file_path, file_io)
    
    await state.update_data(file_bytes=file_io.getvalue())
    await message.answer("🔑 Enter password:")
    await state.set_state(DecodeState.waiting_for_pass)

@router.message(DecodeState.waiting_for_pass)
async def process_decode_pass(message: types.Message, state: FSMContext):
    password = message.text
    data = await state.get_data()
    file_bytes = data['file_bytes']
    
    try:
        extracted = extract_data(file_bytes)
        text = decrypt_data(extracted, password)
        await message.answer(text)
    except Exception:
        await message.answer("❌ Wrong password or file is empty.")
    
    await state.clear()