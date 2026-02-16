import io
import random
from PIL import Image, ImageDraw

async def generate_cover_image() -> bytes:
    """Generate unique abstract image locally"""
    width, height = 512, 512
    
    c1 = (random.randint(0, 100), random.randint(0, 100), random.randint(50, 150))
    c2 = (random.randint(0, 50), random.randint(0, 50), random.randint(100, 255))
    
    img = Image.new('RGB', (width, height), c1)
    draw = ImageDraw.Draw(img, 'RGBA')
    
    for i in range(height):
        r = int(c1[0] + (c2[0] - c1[0]) * i / height)
        g = int(c1[1] + (c2[1] - c1[1]) * i / height)
        b = int(c1[2] + (c2[2] - c1[2]) * i / height)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    style = random.choice(['circles', 'lines', 'cyberpunk'])
    
    for _ in range(random.randint(20, 50)):
        x = random.randint(-50, width+50)
        y = random.randint(-50, height+50)
        size = random.randint(10, 150)
        
        color = (
            random.randint(50, 255), 
            random.randint(50, 255), 
            random.randint(50, 255), 
            random.randint(30, 100)
        )
        
        if style == 'circles':
            draw.ellipse([x, y, x+size, y+size], fill=color, outline=None)
        elif style == 'lines':
            x2 = x + random.randint(-100, 100)
            y2 = y + random.randint(-100, 100)
            width_line = random.randint(1, 5)
            draw.line([x, y, x2, y2], fill=color, width=width_line)
        elif style == 'cyberpunk':
            draw.rectangle([x, y, x+size, y+size/2], fill=color)

    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output.getvalue()