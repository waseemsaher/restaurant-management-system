import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from datetime import datetime
import sys

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_BIDI = True
except ImportError:
    HAS_BIDI = False

class PDFGenerator:
    def __init__(self, config):
        self.config = config
        self.font_name = 'Helvetica'
        self.bold_font_name = 'Helvetica-Bold'
        
        # Try registering Arabic font
        font_path = "assets/fonts/NotoSansArabic.ttf"
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Arabic', font_path))
                self.font_name = 'Arabic'
                self.bold_font_name = 'Arabic'
            except Exception:
                pass

    def format_arabic(self, text):
        if not text:
            return ""
        if HAS_BIDI and self.font_name == 'Arabic':
            reshaped_text = arabic_reshaper.reshape(str(text))
            return get_display(reshaped_text)
        return str(text)
        
    def generate_sales_report(self, report_data, filename):
        """Generate PDF sales report"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        c.setFont(self.bold_font_name, 16)
        c.drawRightString(width - 20*mm, height - 20*mm, self.format_arabic("تقرير مبيعات المطعم"))
        
        c.setFont(self.font_name, 14)
        date_str = datetime.now().strftime('%Y/%m/%d %I:%M %p')
        c.drawRightString(width - 20*mm, height - 35*mm, self.format_arabic(f'التاريخ: {date_str}'))
        
        # Totals
        y = height - 50*mm
        c.setFont(self.bold_font_name, 14)
        # Using drawstring with RTL context means we should perhaps align right
        c.drawRightString(width - 20*mm, y, self.format_arabic("الملخص:"))
        y -= 10*mm
        
        c.setFont(self.font_name, 12)
        totals = report_data.get('totals', {})
        c.drawRightString(width - 20*mm, y, self.format_arabic(f"إجمالي المبيعات: {totals.get('total_sales', 0):.2f} ج.م"))
        y -= 7*mm
        c.drawRightString(width - 20*mm, y, self.format_arabic(f"إجمالي الأوردرات: {totals.get('total_orders', 0)}"))
        y -= 7*mm
        c.drawRightString(width - 20*mm, y, self.format_arabic(f"متوسط الأوردر: {totals.get('avg_order', 0):.2f} ج.م"))
        
        # Top items
        y -= 15*mm
        c.setFont(self.bold_font_name, 14)
        c.drawRightString(width - 20*mm, y, self.format_arabic("الأصناف الأكثر مبيعاً:"))
        y -= 10*mm
        
        c.setFont(self.font_name, 12)
        for idx, item in enumerate(report_data.get('top_items', []), 1):
            line_text = f"{idx}. {item['name']} - {item['qty']} وحدة"
            c.drawRightString(width - 20*mm, y, self.format_arabic(line_text))
            y -= 6*mm
            
        # Category breakdown
        y -= 10*mm
        c.setFont(self.bold_font_name, 14)
        c.drawRightString(width - 20*mm, y, self.format_arabic("مبيعات الأقسام:"))
        y -= 10*mm
        
        c.setFont(self.font_name, 12)
        for idx, cat in enumerate(report_data.get('category_sales', []), 1):
            line_text = f"{cat['name']}: {cat['total']:.2f} ج.م"
            c.drawRightString(width - 20*mm, y, self.format_arabic(line_text))
            y -= 6*mm
        
        c.save()
        return True
