#!/usr/bin/env python3
"""
Database Migration Script for PDF Generation Tables
This script adds tables for quotes and invoices.
"""
import os
import sys
from datetime import datetime
from app import app, db
from models import Quote, QuoteItem, Invoice, InvoiceItem, OrgProfile

def run_migration():
    """Run database migration safely"""
    with app.app_context():
        print("=" * 60)
        print("CONNECT+ PDF Tables Migration Script")
        print("=" * 60)
        print("\nThis will add quote and invoice tables to your database.")
        print("Existing data will be preserved.\n")
        
        try:
            db.session.execute(db.text('SELECT 1'))
            print("✓ Database connection established")
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            return
        
        print("\nAdding new tables...")
        print("-" * 60)
        
        try:
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            is_postgres = 'postgresql' in db_url
            
            if is_postgres:
                print("PostgreSQL detected - using CREATE TABLE")
                migrate_postgresql()
            else:
                print("Using db.create_all() for all tables")
                db.create_all()
                
            print("\n" + "=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)
            print("\nNew tables added:")
            print("  - org_profile (organization info)")
            print("  - quotes (quote management)")
            print("  - quote_items (quote line items)")
            print("  - invoices (invoice management)")
            print("  - invoice_items (invoice line items)")
            print("\nYou can now create quotes and invoices with PDF generation!")
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            print("\nTrying to create all tables...")
            db.create_all()
            print("✓ Database schema updated")

def migrate_postgresql():
    """Migrate PostgreSQL database"""
    migrations = [
        """
        CREATE TABLE IF NOT EXISTS org_profile (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            address VARCHAR(500),
            tel VARCHAR(50),
            email VARCHAR(120),
            logo_path VARCHAR(300),
            invoice_registration_number VARCHAR(100),
            bank_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS quotes (
            id SERIAL PRIMARY KEY,
            company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
            contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
            quote_no VARCHAR(50) UNIQUE,
            issue_date DATE NOT NULL,
            expire_date DATE,
            subject VARCHAR(200) NOT NULL,
            currency VARCHAR(10) DEFAULT 'JPY' NOT NULL,
            tax_rate REAL DEFAULT 0.10 NOT NULL,
            subtotal REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total REAL DEFAULT 0,
            notes TEXT,
            status VARCHAR(20) DEFAULT 'draft' NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_quotes_company_id ON quotes(company_id);
        CREATE INDEX IF NOT EXISTS ix_quotes_quote_no ON quotes(quote_no);
        CREATE INDEX IF NOT EXISTS ix_quotes_status ON quotes(status);
        """,
        """
        CREATE TABLE IF NOT EXISTS quote_items (
            id SERIAL PRIMARY KEY,
            quote_id INTEGER NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
            item_name VARCHAR(200) NOT NULL,
            description TEXT,
            qty REAL DEFAULT 1 NOT NULL,
            unit_price REAL DEFAULT 0 NOT NULL,
            tax_rate REAL DEFAULT 0.10 NOT NULL,
            line_total REAL DEFAULT 0
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_quote_items_quote_id ON quote_items(quote_id);
        """,
        """
        CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
            company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
            contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
            invoice_no VARCHAR(50) UNIQUE,
            issue_date DATE NOT NULL,
            due_date DATE,
            subject VARCHAR(200) NOT NULL,
            currency VARCHAR(10) DEFAULT 'JPY' NOT NULL,
            tax_rate REAL DEFAULT 0.10 NOT NULL,
            subtotal REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total REAL DEFAULT 0,
            notes TEXT,
            status VARCHAR(20) DEFAULT 'draft' NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_invoices_company_id ON invoices(company_id);
        CREATE INDEX IF NOT EXISTS ix_invoices_invoice_no ON invoices(invoice_no);
        CREATE INDEX IF NOT EXISTS ix_invoices_status ON invoices(status);
        """,
        """
        CREATE TABLE IF NOT EXISTS invoice_items (
            id SERIAL PRIMARY KEY,
            invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
            item_name VARCHAR(200) NOT NULL,
            description TEXT,
            qty REAL DEFAULT 1 NOT NULL,
            unit_price REAL DEFAULT 0 NOT NULL,
            tax_rate REAL DEFAULT 0.10 NOT NULL,
            line_total REAL DEFAULT 0
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_invoice_items_invoice_id ON invoice_items(invoice_id);
        """
    ]
    
    for i, migration in enumerate(migrations, 1):
        try:
            db.session.execute(db.text(migration))
            db.session.commit()
            print(f"  ✓ Migration step {i} completed")
        except Exception as e:
            print(f"  ! Migration step {i}: {e} (might already exist)")
            db.session.rollback()

if __name__ == '__main__':
    run_migration()
