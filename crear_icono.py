#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crear icono temporal para ZEROX
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Crear imagen 256x256
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fondo degradado
    for y in range(256):
        color = int(255 * (1 - y/256))
        draw.rectangle([(0, y), (256, y+1)], fill=(0, color, color, 255))
    
    # Círculo central
    draw.ellipse([20, 20, 236, 236], fill=(0, 255, 255, 200), outline=(255, 255, 255, 255), width=5)
    
    # Texto ZEROX
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    # Sombra del texto
    draw.text((128, 128), "Z", font=font, fill=(0, 0, 0, 255), anchor="mm")
    draw.text((126, 126), "Z", font=font, fill=(255, 255, 255, 255), anchor="mm")
    
    # Guardar como ICO
    os.makedirs('assets/icons', exist_ok=True)
    img.save('assets/icons/zerox.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    
    print("✅ Icono creado: assets/icons/zerox.ico")
    
except ImportError:
    print("❌ Instala Pillow: pip install pillow")
except Exception as e:
    print(f"❌ Error: {e}")