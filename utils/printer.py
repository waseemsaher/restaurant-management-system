import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_BIDI = True
except ImportError:
    HAS_BIDI = False

class PrinterUtility:
    def __init__(self, config=None):
        self.config = config or {}
        
    def get_printers(self):
        """Get list of available printers"""
        printers = []
        if sys.platform == 'win32':
            # Basic fallback for Windows without win32print dependency
            printers.append("طابعة الويندوز الافتراضية")
            return printers
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

    def format_arabic_text(self, text):
        if not text:
            return ""
        if HAS_BIDI:
            reshaped_text = arabic_reshaper.reshape(str(text))
            return get_display(reshaped_text)
        return str(text)

    def generate_invoice_image(self, order_data, items_data, filename="temp_invoice.png"):
        """Generate an image for the invoice (80mm format)"""
        width = 576
        height = 300 + (len(items_data) * 50) + 200
        
        img = Image.new('RGB', (width, height), color='white')
        d = ImageDraw.Draw(img)
        
        try:
            # Need an Arabic font
            font_path = "assets/fonts/NotoSansArabic.ttf"
            if not os.path.exists(font_path):
                # fallback for missing font
                font = ImageFont.load_default()
                title_font = font
            else:
                font = ImageFont.truetype(font_path, 24)
                title_font = ImageFont.truetype(font_path, 36)
        except Exception:
            font = ImageFont.load_default()
            title_font = font
            
        y = 20
        d.text((width/2 - 50, y), self.format_arabic_text("فاتورة"), font=title_font, fill=(0,0,0))
        y += 60
        
        d.text((20, y), self.format_arabic_text(f"رقم الأوردر: {order_data.get('order_number', '')}"), font=font, fill=(0,0,0))
        y += 40
        d.text((20, y), self.format_arabic_text(f"التاريخ: {order_data.get('order_time', order_data.get('created_at', ''))}"), font=font, fill=(0,0,0))
        y += 50
        
        d.line([(20, y), (width-20, y)], fill=(0,0,0), width=2)
        y += 20
        
        for item in items_data:
            qty = item.get('quantity', 0)
            price = item.get('price_at_time', 0)
            subtotal = qty * price
            name = self.format_arabic_text(item.get('name', 'Unknown'))
            d.text((20, y), name, font=font, fill=(0,0,0))
            d.text((width - 200, y), str(qty) + "x", font=font, fill=(0,0,0))
            d.text((width - 100, y), f"{subtotal:.2f}", font=font, fill=(0,0,0))
            y += 40
            
        d.line([(20, y), (width-20, y)], fill=(0,0,0), width=2)
        y += 20
        
        # total_amount or total handle both schema versions
        total = order_data.get('total', order_data.get('total_amount', 0))
        d.text((20, y), self.format_arabic_text("الإجمالي:"), font=title_font, fill=(0,0,0))
        d.text((width - 150, y), self.format_arabic_text(f"{total:.2f} ج.م"), font=title_font, fill=(0,0,0))
        y += 80
        
        msg = self.config.get('invoice', {}).get('thank_you_message', 'شكرا لزيارتكم')
        d.text((width/2 - 80, y), self.format_arabic_text(msg), font=font, fill=(0,0,0))
        
        img = img.crop((0, 0, width, y + 60))
        img.save(filename)
        return filename

    def print_image(self, image_path, printer_name=None):
        """Print the generated image"""
        if not os.path.exists(image_path):
            raise FileNotFoundError("Image not found")
            
        if sys.platform == 'win32':
            # Print using Windows default associated print command
            try:
                os.startfile(os.path.abspath(image_path), "print")
                return True
            except Exception as e:
                raise Exception(f"Print failed on Windows: {str(e)}")

        cmd = ['lp']
        if printer_name:
            cmd.extend(['-d', printer_name])
            
        cmd.extend(['-o', 'fit-to-page', image_path])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"Print failed: {e.stderr.decode('utf-8', errors='ignore')}")
