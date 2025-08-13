#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CREADOR DE ICONO PROFESIONAL PARA ZEROX
=======================================
Crea un icono de alta calidad con el logo de ZEROX
"""

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import os
    import math
    
    def crear_icono_zerox():
        """Crea un icono profesional para ZEROX"""
        
        # Tamaños de icono necesarios para Windows
        sizes = [16, 32, 48, 64, 128, 256]
        images = []
        
        for size in sizes:
            # Crear imagen con transparencia
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Fondo circular con gradiente
            center = size // 2
            for i in range(size//2, 0, -1):
                # Gradiente de azul oscuro a cyan
                ratio = i / (size//2)
                r = int(10 * ratio)
                g = int(20 + 235 * (1-ratio))
                b = int(40 + 215 * (1-ratio))
                alpha = 255
                
                draw.ellipse([center-i, center-i, center+i, center+i], 
                           fill=(r, g, b, alpha))
            
            # Borde brillante
            draw.ellipse([2, 2, size-2, size-2], 
                        outline=(0, 255, 255, 255), width=max(1, size//32))
            
            # Letra Z estilizada
            if size >= 32:
                # Calcular tamaño de fuente proporcional
                font_size = int(size * 0.6)
                
                # Dibujar Z con efecto 3D
                z_points = [
                    (size*0.25, size*0.25),  # Superior izquierda
                    (size*0.75, size*0.25),  # Superior derecha
                    (size*0.25, size*0.75),  # Inferior izquierda
                    (size*0.75, size*0.75),  # Inferior derecha
                ]
                
                # Sombra
                shadow_offset = max(1, size//64)
                draw.line([
                    (z_points[0][0]+shadow_offset, z_points[0][1]+shadow_offset),
                    (z_points[1][0]+shadow_offset, z_points[1][1]+shadow_offset)
                ], fill=(0, 0, 0, 128), width=max(2, size//16))
                
                draw.line([
                    (z_points[1][0]+shadow_offset, z_points[1][1]+shadow_offset),
                    (z_points[2][0]+shadow_offset, z_points[2][1]+shadow_offset)
                ], fill=(0, 0, 0, 128), width=max(2, size//16))
                
                draw.line([
                    (z_points[2][0]+shadow_offset, z_points[2][1]+shadow_offset),
                    (z_points[3][0]+shadow_offset, z_points[3][1]+shadow_offset)
                ], fill=(0, 0, 0, 128), width=max(2, size//16))
                
                # Z principal
                draw.line([z_points[0], z_points[1]], 
                         fill=(255, 255, 255, 255), width=max(3, size//12))
                draw.line([z_points[1], z_points[2]], 
                         fill=(255, 255, 255, 255), width=max(3, size//12))
                draw.line([z_points[2], z_points[3]], 
                         fill=(255, 255, 255, 255), width=max(3, size//12))
                
                # Puntos brillantes en las esquinas
                for point in z_points:
                    draw.ellipse([
                        point[0]-size//32, point[1]-size//32,
                        point[0]+size//32, point[1]+size//32
                    ], fill=(0, 255, 255, 255))
            
            # Efecto de brillo
            if size >= 64:
                # Crear capa de brillo
                overlay = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                
                # Brillo superior
                for y in range(size//3):
                    alpha = int(100 * (1 - y/(size//3)))
                    overlay_draw.line([(0, y), (size, y)], 
                                    fill=(255, 255, 255, alpha))
                
                # Combinar con la imagen principal
                img = Image.alpha_composite(img, overlay)
            
            images.append(img)
        
        # Guardar como ICO con múltiples resoluciones
        os.makedirs('assets/icons', exist_ok=True)
        images[5].save('assets/icons/zerox.ico', format='ICO', 
                      sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
                      append_images=images[:-1])
        
        # También crear PNG de alta resolución
        images[5].save('assets/icons/zerox.png', format='PNG')
        
        print("✅ Icono profesional creado exitosamente")
        print("📁 Ubicación: assets/icons/zerox.ico")
        
        # Crear icono de Bitget
        crear_icono_bitget()
        
    def crear_icono_bitget():
        """Crea un icono para el botón de Bitget"""
        size = 128
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Fondo azul Bitget
        draw.rounded_rectangle([0, 0, size, size], radius=20, 
                              fill=(0, 123, 255, 255))
        
        # Letra B estilizada
        draw.text((size//2, size//2), "B", 
                 fill=(255, 255, 255, 255), 
                 anchor="mm",
                 font=None)  # Usar fuente por defecto
        
        img.save('assets/icons/bitget.png', format='PNG')
        print("✅ Icono de Bitget creado")
        
    # Ejecutar
    crear_icono_zerox()
    
except ImportError:
    print("❌ Instala Pillow: pip install pillow")
    
    # Crear iconos básicos como fallback
    import os
    os.makedirs('assets/icons', exist_ok=True)
    
    # Crear archivos vacíos
    with open('assets/icons/zerox.ico', 'wb') as f:
        # ICO header mínimo
        f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x20\x00')
        f.write(b'\x68\x04\x00\x00\x16\x00\x00\x00' + b'\x00' * 1128)
    
    print("⚠️ Iconos temporales creados")