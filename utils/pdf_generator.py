import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from datetime import datetime

class PDFGenerator:
    def __init__(self, config):
        self.config = config
        # For simplicity, we just use default fonts if Arabic is not available,
        # but in a real scenario we'd load an Arabic font.
        # pdfmetrics.registerFont(TTFont('Arabic', 'assets/fonts/NotoSansArabic.ttf'))
        
    def generate_sales_report(self, report_data, filename):
        """Generate PDF sales report"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # We'll use a simple layout. Arabic might not render perfectly without shaping, 
        # but reportlab handles basic text if font is loaded.
        # Fallback to Helvetica
        c.setFont('Helvetica-Bold', 16)
        c.drawRightString(width - 20*mm, height - 20*mm, "Restaurant Sales Report")
        
        c.setFont('Helvetica', 14)
        date_str = datetime.now().strftime('%Y/%m/%d %I:%M %p')
        c.drawRightString(width - 20*mm, height - 35*mm, f'Date: {date_str}')
        
        # Totals
        y = height - 50*mm
        c.setFont('Helvetica-Bold', 14)
        c.drawString(20*mm, y, "Summary:")
        y -= 10*mm
        
        c.setFont('Helvetica', 12)
        totals = report_data.get('totals', {})
        c.drawString(20*mm, y, f"Total Sales: {totals.get('total_sales', 0):.2f} EGP")
        y -= 7*mm
        c.drawString(20*mm, y, f"Total Orders: {totals.get('total_orders', 0)}")
        y -= 7*mm
        c.drawString(20*mm, y, f"Average Order: {totals.get('avg_order', 0):.2f} EGP")
        
        # Top items
        y -= 15*mm
        c.setFont('Helvetica-Bold', 14)
        c.drawString(20*mm, y, "Top Selling Items:")
        y -= 10*mm
        
        c.setFont('Helvetica', 12)
        for idx, item in enumerate(report_data.get('top_items', []), 1):
            c.drawString(20*mm, y, f"{idx}. {item['name']} - {item['qty']} units")
            y -= 6*mm
            
        # Category breakdown
        y -= 10*mm
        c.setFont('Helvetica-Bold', 14)
        c.drawString(20*mm, y, "Sales by Category:")
        y -= 10*mm
        
        c.setFont('Helvetica', 12)
        for idx, cat in enumerate(report_data.get('category_sales', []), 1):
            c.drawString(20*mm, y, f"{cat['name']}: {cat['total']:.2f} EGP")
            y -= 6*mm
        
        c.save()
        return True
