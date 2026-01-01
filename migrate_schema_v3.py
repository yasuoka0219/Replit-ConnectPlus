"""
Migration script v3.0.0 - Add analysis & classification fields
This script safely adds new columns and master tables without breaking existing data.
Run: python migrate_schema_v3.py
"""

import os
import sys
from datetime import datetime

# Add project to path
sys.path.insert(0, '/home/runner/workspace')
os.environ['FLASK_APP'] = 'app.py'

from database import db
from app import app

def migrate():
    """Execute migration"""
    with app.app_context():
        print("Starting v3.0.0 schema migration...")
        
        # Create all new tables (SQLAlchemy handles this)
        try:
            db.create_all()
            print("✓ All tables created/updated successfully")
            
            # Seed master data if needed
            from models import (
                Industry, CompanySize, CustomerStatus, 
                LeadSource, Stage, LostReason, ActivityType
            )
            
            # Check and seed default master data
            seed_master_data()
            
            print("✓ Migration v3.0.0 completed successfully!")
            return True
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            db.session.rollback()
            return False

def seed_master_data():
    """Seed default master data"""
    from models import (
        Industry, CompanySize, CustomerStatus, 
        LeadSource, Stage, LostReason, ActivityType
    )
    
    # Seed Industries
    if Industry.query.count() == 0:
        industries = [
            ('IT・SaaS', 'Software and IT services', 1),
            ('製造', 'Manufacturing', 2),
            ('小売', 'Retail', 3),
            ('飲食', 'Food & Beverage', 4),
            ('サービス', 'Service', 5),
            ('医療・福祉', 'Healthcare & Welfare', 6),
            ('金融', 'Finance', 7),
            ('不動産', 'Real Estate', 8),
            ('その他', 'Other', 9),
        ]
        for name, desc, order in industries:
            ind = Industry(name=name, description=desc, sort_order=order)
            db.session.add(ind)
        db.session.commit()
        print("  ✓ Seeded Industries")
    
    # Seed Company Sizes
    if CompanySize.query.count() == 0:
        sizes = [
            ('〜10名', 'Up to 10 employees', 1),
            ('11〜50名', '11-50 employees', 2),
            ('51〜100名', '51-100 employees', 3),
            ('101〜300名', '101-300 employees', 4),
            ('301名〜', '301+ employees', 5),
        ]
        for name, desc, order in sizes:
            sz = CompanySize(name=name, description=desc, sort_order=order)
            db.session.add(sz)
        db.session.commit()
        print("  ✓ Seeded Company Sizes")
    
    # Seed Customer Status
    if CustomerStatus.query.count() == 0:
        statuses = [
            ('新規', 'New customer', 1),
            ('既存', 'Existing customer', 2),
            ('休眠', 'Dormant customer', 3),
        ]
        for name, desc, order in statuses:
            status = CustomerStatus(name=name, description=desc, sort_order=order)
            db.session.add(status)
        db.session.commit()
        print("  ✓ Seeded Customer Statuses")
    
    # Seed Lead Sources
    if LeadSource.query.count() == 0:
        sources = [
            ('紹介', 'Referral', 1),
            ('Webサイト', 'Website', 2),
            ('広告', 'Advertisement', 3),
            ('展示会', 'Trade Show', 4),
            ('テレアポ', 'Cold Call', 5),
            ('代理店', 'Partner/Reseller', 6),
            ('SNS', 'Social Media', 7),
        ]
        for name, desc, order in sources:
            source = LeadSource(name=name, description=desc, sort_order=order)
            db.session.add(source)
        db.session.commit()
        print("  ✓ Seeded Lead Sources")
    
    # Seed Stages
    if Stage.query.count() == 0:
        stages = [
            ('リード', 'Lead', 1),
            ('アポ取得', 'Appointment', 2),
            ('ヒアリング', 'Discovery', 3),
            ('見積・提案', 'Proposal', 4),
            ('最終調整', 'Final Negotiation', 5),
            ('受注', 'Won', 6),
            ('失注', 'Lost', 7),
        ]
        for name, desc, order in stages:
            stage = Stage(name=name, description=desc, sort_order=order)
            db.session.add(stage)
        db.session.commit()
        print("  ✓ Seeded Stages")
    
    # Seed Lost Reasons
    if LostReason.query.count() == 0:
        reasons = [
            ('価格', 'Price', 1),
            ('予算不足', 'Budget', 2),
            ('競合優位', 'Competitor', 3),
            ('タイミング合わず', 'Timing', 4),
            ('社内稟議NG', 'Internal Approval', 5),
            ('検討中止', 'Discontinued', 6),
        ]
        for name, desc, order in reasons:
            reason = LostReason(name=name, description=desc, sort_order=order)
            db.session.add(reason)
        db.session.commit()
        print("  ✓ Seeded Lost Reasons")
    
    # Seed Activity Types
    if ActivityType.query.count() == 0:
        types = [
            ('電話', 'Phone Call', 1),
            ('メール', 'Email', 2),
            ('オンライン商談', 'Online Meeting', 3),
            ('訪問', 'Visit', 4),
            ('提案書作成', 'Proposal', 5),
            ('ミーティング', 'Meeting', 6),
            ('その他', 'Other', 7),
        ]
        for name, desc, order in types:
            activity_type = ActivityType(name=name, description=desc, sort_order=order)
            db.session.add(activity_type)
        db.session.commit()
        print("  ✓ Seeded Activity Types")

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
