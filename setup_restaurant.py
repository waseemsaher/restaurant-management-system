#!/usr/bin/env python3
from utils.config import ConfigManager

def setup_restaurant():
    """Interactive setup for new restaurant. If run non-interactively, defaults are used."""
    print("=== Restaurant Setup ===\n")

    try:
        name = input("اسم المطعم (عربي): ").strip() or "مطعم الكريب الذهبي"
    except EOFError:
        # non-interactive, use defaults
        name = "مطعم الكريب الذهبي"

    try:
        name_en = input("Restaurant Name (English): ").strip() or "Golden Crepe Restaurant"
    except EOFError:
        name_en = "Golden Crepe Restaurant"

    try:
        address = input("العنوان: ").strip() or "123 شارع الهرم، الجيزة"
    except EOFError:
        address = "123 شارع الهرم، الجيزة"

    try:
        phone = input("رقم التليفون: ").strip() or "0123456789"
    except EOFError:
        phone = "0123456789"

    try:
        currency = input("العملة (مثال: ج.م): ").strip() or "ج.م"
    except EOFError:
        currency = "ج.م"

    try:
        tax_id = input("الرقم الضريبي (اختياري): ").strip()
    except EOFError:
        tax_id = ""

    try:
        logo = input("مسار اللوجو (مثال: assets/logo.png): ").strip() or "assets/logo.png"
    except EOFError:
        logo = "assets/logo.png"

    try:
        primary = input("اللون الرئيسي (مثال: #2C3E50): ").strip() or "#2C3E50"
    except EOFError:
        primary = "#2C3E50"

    try:
        secondary = input("اللون الثانوي (مثال: #27AE60): ").strip() or "#27AE60"
    except EOFError:
        secondary = "#27AE60"

    try:
        thank_you = input("رسالة الشكر في الفاتورة: ").strip() or "شكراً لزيارتكم"
    except EOFError:
        thank_you = "شكراً لزيارتكم"

    try:
        footer = input("ملاحظة إضافية (اختياري): ").strip()
    except EOFError:
        footer = ""

    try:
        tables = input("تفعيل الطاولات؟ (yes/no): ").strip().lower() == 'yes'
    except EOFError:
        tables = False

    try:
        printer = input("تفعيل الطابعة؟ (yes/no): ").strip().lower() == 'yes'
    except EOFError:
        printer = False

    config = {
        "restaurant": {
            "name": name,
            "name_english": name_en,
            "address": address,
            "phone": phone,
            "tax_id": tax_id,
            "currency": currency,
            "footer_message": thank_you
        },
        "branding": {
            "logo_path": logo,
            "primary_color": primary,
            "secondary_color": secondary
        },
        "invoice": {
            "thank_you_message": thank_you,
            "footer_note": footer
        },
        "features": {
            "tables_enabled": tables,
            "printer_enabled": printer
        },
        "shifts": {
            "available_shifts": ["صباحي", "مسائي"]
        }
    }

    cm = ConfigManager('config.encrypted', 'config.key')
    cm.encrypt_config(config)

    print("\n✅ Configuration saved successfully!")
    print("📄 File: config.encrypted")

if __name__ == '__main__':
    setup_restaurant()
