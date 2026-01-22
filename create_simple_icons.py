"""
Create simple PNG icons without PIL using raw PNG format
"""
import struct
import zlib

def create_simple_png(size, color_rgb):
    """Create a simple solid color PNG without PIL"""
    width = height = size

    # PNG signature
    png_signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_chunk = create_chunk(b'IHDR', ihdr_data)

    # Create image data (solid color)
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # No filter
        for x in range(width):
            raw_data.extend(color_rgb)

    # IDAT chunk
    compressed_data = zlib.compress(bytes(raw_data), 9)
    idat_chunk = create_chunk(b'IDAT', compressed_data)

    # IEND chunk
    iend_chunk = create_chunk(b'IEND', b'')

    # Combine all parts
    png_data = png_signature + ihdr_chunk + idat_chunk + iend_chunk

    return png_data

def create_chunk(chunk_type, data):
    """Create a PNG chunk"""
    length = struct.pack('>I', len(data))
    crc = struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
    return length + chunk_type + data + crc

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Generate icons
sizes = [72, 96, 128, 144, 152, 192, 384, 512]
color = hex_to_rgb('#667eea')  # Task Multiverse theme color

for size in sizes:
    png_data = create_simple_png(size, color)
    filename = f'/home/user/JRA/assets/icons/icon-{size}x{size}.png'

    with open(filename, 'wb') as f:
        f.write(png_data)

    print(f"✅ Created icon-{size}x{size}.png")

print("\n✨ All icons created successfully!")
print("   Note: These are simple placeholder icons.")
print("   For better icons, install Pillow and run generate_icons.py")
