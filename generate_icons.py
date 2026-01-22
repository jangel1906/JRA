"""
Simple icon generator for Task Multiverse PWA
Creates placeholder PNG icons in various sizes
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL/Pillow not installed. Creating placeholder HTML file instead.")

import os

# Icon sizes needed for PWA
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

def create_icon_with_pil(size):
    """Create an icon using PIL"""
    # Create image with gradient background
    img = Image.new('RGB', (size, size), color='#667eea')
    draw = ImageDraw.Draw(img)

    # Draw a simple multiverse representation (circles)
    center = size // 2

    # Draw multiple circles representing universes
    circles = [
        (center - size//4, center - size//4, size//3),
        (center + size//6, center - size//6, size//4),
        (center - size//6, center + size//6, size//4),
    ]

    for x, y, radius in circles:
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            fill='#ffffff',
            outline='#764ba2',
            width=max(2, size//64)
        )

    # Draw center text
    try:
        # Try to use a font, fallback to default if not available
        font_size = size // 4
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text = "TM"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2

    # Draw text with shadow
    shadow_offset = max(2, size//128)
    draw.text((text_x + shadow_offset, text_y + shadow_offset), text, fill='#00000044', font=font)
    draw.text((text_x, text_y), text, fill='#ffffff', font=font)

    return img

def create_icon_html():
    """Create an HTML file with SVG icons as a fallback"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Task Multiverse Icon Generator</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
        .icon-container { display: flex; flex-wrap: wrap; gap: 20px; }
        .icon-box { text-align: center; }
        canvas { border: 2px solid #667eea; border-radius: 10px; }
        h1 { color: #667eea; }
        .instructions { background: white; padding: 15px; border-radius: 10px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>🌌 Task Multiverse Icon Generator</h1>

    <div class="instructions">
        <h3>Instructions:</h3>
        <ol>
            <li>Right-click on each icon below and select "Save image as..."</li>
            <li>Save each icon with its corresponding size name (e.g., icon-72x72.png)</li>
            <li>Place all icons in the <code>/assets/icons/</code> folder</li>
            <li>Or install Pillow: <code>pip install Pillow</code> and run this script</li>
        </ol>
    </div>

    <div class="icon-container" id="icons"></div>

    <script>
        const sizes = [72, 96, 128, 144, 152, 192, 384, 512];
        const container = document.getElementById('icons');

        sizes.forEach(size => {
            const box = document.createElement('div');
            box.className = 'icon-box';

            const canvas = document.createElement('canvas');
            canvas.width = size;
            canvas.height = size;

            const ctx = canvas.getContext('2d');

            // Gradient background
            const gradient = ctx.createLinearGradient(0, 0, size, size);
            gradient.addColorStop(0, '#667eea');
            gradient.addColorStop(1, '#764ba2');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, size, size);

            // Draw circles (universes)
            const center = size / 2;
            const circles = [
                [center - size/4, center - size/4, size/6],
                [center + size/6, center - size/6, size/8],
                [center - size/6, center + size/6, size/8],
            ];

            circles.forEach(([x, y, r]) => {
                ctx.beginPath();
                ctx.arc(x, y, r, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                ctx.fill();
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = Math.max(2, size/64);
                ctx.stroke();
            });

            // Draw text
            ctx.fillStyle = '#ffffff';
            ctx.font = `bold ${size/4}px Arial`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
            ctx.shadowBlur = size/32;
            ctx.shadowOffsetX = size/128;
            ctx.shadowOffsetY = size/128;
            ctx.fillText('TM', center, center);

            const label = document.createElement('p');
            label.textContent = `${size}x${size}`;

            box.appendChild(canvas);
            box.appendChild(label);
            container.appendChild(box);
        });
    </script>
</body>
</html>"""

    with open('/home/user/JRA/assets/icons/icon-generator.html', 'w') as f:
        f.write(html_content)

    print("✅ Created icon-generator.html")
    print("   Open this file in a browser to download icons manually")

def main():
    """Main function to generate icons"""
    icons_dir = '/home/user/JRA/assets/icons'
    os.makedirs(icons_dir, exist_ok=True)

    if PIL_AVAILABLE:
        print("🎨 Generating icons with PIL...")
        for size in ICON_SIZES:
            icon = create_icon_with_pil(size)
            filename = f'icon-{size}x{size}.png'
            filepath = os.path.join(icons_dir, filename)
            icon.save(filepath, 'PNG')
            print(f"   ✅ Created {filename}")
        print("\n✨ All icons generated successfully!")
    else:
        print("📝 PIL not available. Creating HTML icon generator...")
        create_icon_html()
        print("\n💡 To generate icons automatically, install Pillow:")
        print("   pip install Pillow")
        print("   Then run this script again")

if __name__ == '__main__':
    main()
