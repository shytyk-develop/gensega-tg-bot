import os
import io
import random
import math
import re
import asyncio
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFilter

if os.environ.get("GOOGLE_API_KEY"):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel('gemini-1.5-flash')

PROMPTS = [
    "Draw a chaotic cyberpunk neon glitch pattern with lines and rectangles.",
    "Draw a serene abstract landscape with flowing curves and gradients.",
    "Draw a complex geometric mandala with symmetrical circles and triangles.",
    "Draw a retro synthwave sunset with a grid and a sun.",
    "Draw an abstract space nebula using randomly placed translucent ellipses.",
    "Draw a digital rain matrix style pattern."
]

async def generate_cover_image() -> bytes:
    try:
        selected_prompt = random.choice(PROMPTS)

        prompt_text = (
            f"Write Python code using the 'PIL' (Pillow) library to draw: {selected_prompt}. "
            "Assume variables 'img' (512x512 RGB) and 'draw' (ImageDraw object) are already created. "
            "Use 'width' and 'height' variables (512). "
            "Use 'random' and 'math' modules. "
            "Do NOT use 'import'. Do NOT use 'Image.new' or 'save'. "
            "Just write the drawing commands (draw.line, draw.rectangle, draw.ellipse, etc). "
            "Make it colorful and detailed. "
            "Output ONLY raw python code inside code blocks."
        )

        response = await asyncio.to_thread(
            model.generate_content,
            prompt_text,
            generation_config={"temperature": 1.0}
        )
        
        code = response.text
        
        clean_code = re.sub(r"```python|```", "", code).strip()
        
        width, height = 512, 512
        img = Image.new('RGB', (width, height), color=(10, 10, 10))
        draw = ImageDraw.Draw(img)
        
        local_scope = {
            'img': img,
            'draw': draw,
            'width': width,
            'height': height,
            'random': random,
            'math': math
        }
        
        try:
            exec(clean_code, {}, local_scope)
        except Exception as exec_error:
            print(f"Error: {exec_error}")
            draw.text((10, 10), "AI Art Error", fill=(255, 0, 0))

        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)
        return output.getvalue()

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return await generate_fallback_image(str(e))

async def generate_fallback_image(error_text: str = "") -> bytes:
    img = Image.new('RGB', (512, 512), (50, 0, 0)) 
    draw = ImageDraw.Draw(img)
    
    for i in range(0, 512, 50):
        draw.line([(i, 0), (i, 512)], fill=(100, 50, 50))
        draw.line([(0, i), (512, i)], fill=(100, 50, 50))
    if error_text:
        print(f"Fallback due to: {error_text}")
        
    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output.getvalue()