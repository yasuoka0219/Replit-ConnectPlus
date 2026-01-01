import os
from datetime import datetime
from fpdf import FPDF
from models import Quote, Invoice, OrgProfile


class JapanesePDF(FPDF):
    """Custom PDF class with Japanese font support (Meiryo-style appearance)"""
    
    def __init__(self):
        super().__init__()
        self.font_path = os.path.join('static', 'fonts', 'MPLUSRounded1c-Regular.ttf')
        
        if os.path.exists(self.font_path):
            try:
                self.add_font('Meiryo', '', self.font_path)
                self.font_family = 'Meiryo'
            except Exception as e:
                print(f"Font loading error: {e}")
                self.font_family = 'Helvetica'
        else:
            self.font_family = 'Helvetica'
    
    def header(self):
        pass
    
    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family, '', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def generate_quote_pdf(quote_id):
    """
    Generate PDF for a quote
    
    Args:
        quote_id: Quote ID
    
    Returns:
        bytes: PDF file content
    """
    from app import app, db
    
    with app.app_context():
        quote = db.session.get(Quote, quote_id)
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")
        
        org = db.session.query(OrgProfile).first()
        if not org:
            class FallbackOrg:
                org_name = "株式会社サンプル"
                org_name_kana = ""
                postal_code = ""
                address = "東京都渋谷区1-2-3"
                phone = "03-1234-5678"
                email = "info@example.com"
                representative = ""
                registration_number = ""
                bank_info = ""
            org = FallbackOrg()
        
        pdf = JapanesePDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)
        
        pdf.set_font(pdf.font_family, '', 20)
        pdf.cell(0, 15, '見積書', 0, 1, 'C')
        pdf.ln(5)
        
        pdf.set_font(pdf.font_family, '', 10)
        pdf.set_text_color(100)
        if quote.quote_no:
            pdf.cell(0, 6, f'見積番号: {quote.quote_no}', 0, 1, 'R')
        pdf.cell(0, 6, f'発行日: {quote.issue_date.strftime("%Y年%m月%d日")}', 0, 1, 'R')
        if quote.expire_date:
            pdf.cell(0, 6, f'有効期限: {quote.expire_date.strftime("%Y年%m月%d日")}', 0, 1, 'R')
        pdf.ln(10)
        
        pdf.set_text_color(0)
        pdf.set_font(pdf.font_family, '', 12)
        pdf.cell(0, 8, f'{quote.company.name} 御中', 0, 1)
        if quote.contact:
            pdf.set_font(pdf.font_family, '', 10)
            pdf.cell(0, 6, f'  {quote.contact.name} 様', 0, 1)
        pdf.ln(5)
        
        pdf.set_font(pdf.font_family, '', 11)
        pdf.cell(0, 8, f'件名: {quote.subject}', 0, 1)
        pdf.ln(5)
        
        pdf.set_font(pdf.font_family, '', 10)
        pdf.cell(0, 6, '下記の通りお見積り申し上げます。', 0, 1)
        pdf.ln(5)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font(pdf.font_family, '', 10)
        pdf.cell(80, 8, '品目', 1, 0, 'C', True)
        pdf.cell(20, 8, '数量', 1, 0, 'C', True)
        pdf.cell(40, 8, '単価', 1, 0, 'C', True)
        pdf.cell(50, 8, '金額', 1, 1, 'C', True)
        
        pdf.set_font(pdf.font_family, '', 9)
        for item in quote.items:
            pdf.cell(80, 7, item.item_name[:30], 1, 0)
            pdf.cell(20, 7, f'{item.qty:.0f}', 1, 0, 'R')
            pdf.cell(40, 7, f'¥{item.unit_price:,.0f}', 1, 0, 'R')
            pdf.cell(50, 7, f'¥{item.line_total:,.0f}', 1, 1, 'R')
            
            if item.description:
                pdf.set_font(pdf.font_family, '', 8)
                pdf.set_text_color(100)
                desc_lines = item.description[:80].split('\n')
                for line in desc_lines[:2]:
                    pdf.cell(80, 5, f'  {line}', 0, 1)
                pdf.set_text_color(0)
                pdf.set_font(pdf.font_family, '', 9)
        
        pdf.ln(3)
        
        pdf.set_font(pdf.font_family, '', 10)
        x_pos = pdf.get_x() + 100
        pdf.set_x(x_pos)
        pdf.cell(40, 7, '小計:', 0, 0, 'R')
        pdf.cell(50, 7, f'¥{quote.subtotal:,.0f}', 0, 1, 'R')
        
        pdf.set_x(x_pos)
        pdf.cell(40, 7, f'消費税 ({quote.tax_rate*100:.0f}%):', 0, 0, 'R')
        pdf.cell(50, 7, f'¥{quote.tax_amount:,.0f}', 0, 1, 'R')
        
        pdf.set_x(x_pos)
        pdf.set_font(pdf.font_family, '', 12)
        pdf.cell(40, 10, '合計:', 0, 0, 'R')
        pdf.cell(50, 10, f'¥{quote.total:,.0f}', 0, 1, 'R')
        
        if quote.notes:
            pdf.ln(5)
            pdf.set_font(pdf.font_family, '', 9)
            pdf.multi_cell(0, 5, f'備考: {quote.notes}')
        
        pdf.ln(10)
        pdf.set_draw_color(200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        
        pdf.set_font(pdf.font_family, '', 9)
        pdf.set_text_color(80)
        pdf.cell(0, 5, org.org_name, 0, 1)
        if org.address:
            pdf.cell(0, 5, f'住所: {org.address}', 0, 1)
        if org.phone:
            pdf.cell(0, 5, f'TEL: {org.phone}', 0, 1)
        if org.email:
            pdf.cell(0, 5, f'Email: {org.email}', 0, 1)
        if org.registration_number:
            pdf.cell(0, 5, f'適格請求書登録番号: {org.registration_number}', 0, 1)
        
        return pdf.output(dest='S')


def generate_invoice_pdf(invoice_id):
    """
    Generate PDF for an invoice
    
    Args:
        invoice_id: Invoice ID
    
    Returns:
        bytes: PDF file content
    """
    from app import app, db
    
    with app.app_context():
        invoice = db.session.get(Invoice, invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        org = db.session.query(OrgProfile).first()
        if not org:
            class FallbackOrg:
                org_name = "株式会社サンプル"
                org_name_kana = ""
                postal_code = ""
                address = "東京都渋谷区1-2-3"
                phone = "03-1234-5678"
                email = "info@example.com"
                representative = ""
                registration_number = ""
                bank_info = ""
            org = FallbackOrg()
        
        pdf = JapanesePDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)
        
        pdf.set_font(pdf.font_family, '', 20)
        pdf.cell(0, 15, '請求書', 0, 1, 'C')
        pdf.ln(5)
        
        pdf.set_font(pdf.font_family, '', 10)
        pdf.set_text_color(100)
        if invoice.invoice_no:
            pdf.cell(0, 6, f'請求番号: {invoice.invoice_no}', 0, 1, 'R')
        pdf.cell(0, 6, f'請求日: {invoice.issue_date.strftime("%Y年%m月%d日")}', 0, 1, 'R')
        if invoice.due_date:
            pdf.cell(0, 6, f'支払期限: {invoice.due_date.strftime("%Y年%m月%d日")}', 0, 1, 'R')
        pdf.ln(10)
        
        pdf.set_text_color(0)
        pdf.set_font(pdf.font_family, '', 12)
        pdf.cell(0, 8, f'{invoice.company.name} 御中', 0, 1)
        if invoice.contact:
            pdf.set_font(pdf.font_family, '', 10)
            pdf.cell(0, 6, f'  {invoice.contact.name} 様', 0, 1)
        pdf.ln(5)
        
        pdf.set_font(pdf.font_family, '', 11)
        pdf.cell(0, 8, f'件名: {invoice.subject}', 0, 1)
        pdf.ln(5)
        
        pdf.set_font(pdf.font_family, '', 10)
        pdf.cell(0, 6, '下記の通りご請求申し上げます。', 0, 1)
        pdf.ln(5)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font(pdf.font_family, '', 10)
        pdf.cell(80, 8, '品目', 1, 0, 'C', True)
        pdf.cell(20, 8, '数量', 1, 0, 'C', True)
        pdf.cell(40, 8, '単価', 1, 0, 'C', True)
        pdf.cell(50, 8, '金額', 1, 1, 'C', True)
        
        pdf.set_font(pdf.font_family, '', 9)
        for item in invoice.items:
            pdf.cell(80, 7, item.item_name[:30], 1, 0)
            pdf.cell(20, 7, f'{item.qty:.0f}', 1, 0, 'R')
            pdf.cell(40, 7, f'¥{item.unit_price:,.0f}', 1, 0, 'R')
            pdf.cell(50, 7, f'¥{item.line_total:,.0f}', 1, 1, 'R')
            
            if item.description:
                pdf.set_font(pdf.font_family, '', 8)
                pdf.set_text_color(100)
                desc_lines = item.description[:80].split('\n')
                for line in desc_lines[:2]:
                    pdf.cell(80, 5, f'  {line}', 0, 1)
                pdf.set_text_color(0)
                pdf.set_font(pdf.font_family, '', 9)
        
        pdf.ln(3)
        
        pdf.set_font(pdf.font_family, '', 10)
        x_pos = pdf.get_x() + 100
        pdf.set_x(x_pos)
        pdf.cell(40, 7, '小計:', 0, 0, 'R')
        pdf.cell(50, 7, f'¥{invoice.subtotal:,.0f}', 0, 1, 'R')
        
        pdf.set_x(x_pos)
        pdf.cell(40, 7, f'消費税 ({invoice.tax_rate*100:.0f}%):', 0, 0, 'R')
        pdf.cell(50, 7, f'¥{invoice.tax_amount:,.0f}', 0, 1, 'R')
        
        pdf.set_x(x_pos)
        pdf.set_font(pdf.font_family, '', 12)
        pdf.cell(40, 10, '合計:', 0, 0, 'R')
        pdf.cell(50, 10, f'¥{invoice.total:,.0f}', 0, 1, 'R')
        
        if invoice.notes:
            pdf.ln(5)
            pdf.set_font(pdf.font_family, '', 9)
            pdf.multi_cell(0, 5, f'備考: {invoice.notes}')
        
        pdf.ln(10)
        pdf.set_draw_color(200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        
        pdf.set_font(pdf.font_family, '', 9)
        pdf.set_text_color(80)
        pdf.cell(0, 5, org.org_name, 0, 1)
        if org.address:
            pdf.cell(0, 5, f'住所: {org.address}', 0, 1)
        if org.phone:
            pdf.cell(0, 5, f'TEL: {org.phone}', 0, 1)
        if org.email:
            pdf.cell(0, 5, f'Email: {org.email}', 0, 1)
        if org.registration_number:
            pdf.cell(0, 5, f'適格請求書登録番号: {org.registration_number}', 0, 1)
        if org.bank_info:
            pdf.ln(3)
            pdf.set_font(pdf.font_family, '', 8)
            pdf.multi_cell(0, 4, f'振込先:\n{org.bank_info}')
        
        return pdf.output(dest='S')
