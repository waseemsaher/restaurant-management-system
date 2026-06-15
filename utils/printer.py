import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

class PrinterUtility:
    def __init__(self, config=None):
        self.config = config or {}
        
    def get_printers(self):
        """Get list of available printers using lpstat"""
        printers = []
        try:
            result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if line.startswith('printer'):
                    parts = line.split(' ')
                    if len(parts) > 1:
                        printers.append(parts[1])
        except Exception:
            pass
        return printers

    def generate_invoice_image(self, order_data, items_data, filename="temp_invoice.png"):
        """Generate an image for the invoice (80mm format)"""
        # 80mm thermal paper is approx 576 dots wide (or 512 for 58mm). Let's use 576.
        width = 576
        
        # Estimate height
        height = 300 + (len(items_data) * 50) + 200
        
        img = Image.new('RGB', (width, height), color='white')
        d = ImageDraw.Draw(img)
        
        try:
            # Try to load a font, fallback to default
            # Normally we need an Arabic font here
            font = ImageFont.truetype("assets/fonts/NotoSansArabic.ttf", 24)
            title_font = ImageFont.truetype("assets/fonts/NotoSansArabic.ttf", 36)
        except Exception:
            font = ImageFont.load_default()
            title_font = font
            
        # Unicode LRM to fix RTL number display
        LRM = "\u200e"
        y = 20
        d.text((width/2 - 100, y), "فاتورة", font=title_font, fill=(0,0,0))
        y += 60
        
        d.text((20, y), f"رقم الأوردر: {LRM}{order_data.get('order_number', '')}", font=font, fill=(0,0,0))
        y += 40
        d.text((20, y), f"التاريخ: {LRM}{order_data.get('created_at', '')}", font=font, fill=(0,0,0))
        y += 50
        
        d.line([(20, y), (width-20, y)], fill=(0,0,0), width=2)
        y += 20
        
        for item in items_data:
            qty = item.get('quantity', 0)
            price = item.get('price_at_time', 0)
            subtotal = qty * price
            name = item.get('name', 'Unknown')
            d.text((20, y), f"{name}", font=font, fill=(0,0,0))
            d.text((width - 200, y), f"{LRM}{qty}x", font=font, fill=(0,0,0))
            d.text((width - 100, y), f"{LRM}{subtotal:.2f}", font=font, fill=(0,0,0))
            y += 40
            
        d.line([(20, y), (width-20, y)], fill=(0,0,0), width=2)
        y += 20
        
        total = order_data.get('total', 0)
        d.text((20, y), f"الإجمالي:", font=title_font, fill=(0,0,0))
        d.text((width - 150, y), f"{LRM}{total:.2f} ج.م", font=title_font, fill=(0,0,0))
        y += 80
        
        # Thank you message
        msg = self.config.get('invoice', {}).get('thank_you_message', 'شكرا لزيارتكم')
        d.text((width/2 - 100, y), msg, font=font, fill=(0,0,0))
        
        # Crop to actual height
        img = img.crop((0, 0, width, y + 60))
        img.save(filename)
        return filename

    def print_image(self, image_path, printer_name=None):
        """Print the generated image"""
        if not os.path.exists(image_path):
            raise FileNotFoundError("Image not found")
            
        cmd = ['lp']
        if printer_name:
            cmd.extend(['-d', printer_name])
            
        # Add options for fitting to page
        cmd.extend(['-o', 'fit-to-page', image_path])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"Print failed: {e.stderr.decode('utf-8', errors='ignore')}")
