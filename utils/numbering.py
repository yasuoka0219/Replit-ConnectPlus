from database import db
from datetime import datetime


def generate_quote_number(year=None):
    """
    Generate a unique quote number in the format YYYY-####
    Auto-resets counter when year changes
    
    Args:
        year: Optional year (defaults to current year)
    
    Returns:
        str: Quote number like "2025-0001"
    """
    if year is None:
        year = datetime.now().year
    
    prefix = f"{year}-"
    
    from models import Quote
    
    last_quote = (db.session.query(Quote)
                 .filter(Quote.quote_no.like(f'{prefix}%'))
                 .order_by(Quote.quote_no.desc())
                 .first())
    
    if last_quote and last_quote.quote_no:
        try:
            last_number = int(last_quote.quote_no.split('-')[1])
            next_number = last_number + 1
        except (IndexError, ValueError):
            next_number = 1
    else:
        next_number = 1
    
    return f"{prefix}{next_number:04d}"


def generate_invoice_number(year=None):
    """
    Generate a unique invoice number in the format YYYY-####
    Auto-resets counter when year changes
    
    Args:
        year: Optional year (defaults to current year)
    
    Returns:
        str: Invoice number like "2025-0001"
    """
    if year is None:
        year = datetime.now().year
    
    prefix = f"{year}-"
    
    from models import Invoice
    
    last_invoice = (db.session.query(Invoice)
                   .filter(Invoice.invoice_no.like(f'{prefix}%'))
                   .order_by(Invoice.invoice_no.desc())
                   .first())
    
    if last_invoice and last_invoice.invoice_no:
        try:
            last_number = int(last_invoice.invoice_no.split('-')[1])
            next_number = last_number + 1
        except (IndexError, ValueError):
            next_number = 1
    else:
        next_number = 1
    
    return f"{prefix}{next_number:04d}"
