"""
企業規模、顧客ステータス、リードソースのマスターデータを作成するスクリプト
"""
from database import db
from models import CompanySize, CustomerStatus, LeadSource

def seed_company_masters():
    """企業規模、顧客ステータス、リードソースのマスターデータを作成"""
    print("マスターデータを作成します...")
    
    # 企業規模の作成
    company_sizes = [
        {'name': '小規模', 'description': '従業員数が少ない企業', 'sort_order': 1},
        {'name': '中規模', 'description': '従業員数が中程度の企業', 'sort_order': 2},
        {'name': '大規模', 'description': '従業員数が多い企業', 'sort_order': 3},
    ]
    
    for size_data in company_sizes:
        existing = CompanySize.query.filter_by(name=size_data['name']).first()
        if not existing:
            company_size = CompanySize(**size_data)
            db.session.add(company_size)
            print(f"  ✓ 企業規模「{size_data['name']}」を作成しました")
        else:
            print(f"  - 企業規模「{size_data['name']}」は既に存在します")
    
    # 顧客ステータスの作成
    customer_statuses = [
        {'name': '新規', 'description': '新規顧客', 'sort_order': 1},
        {'name': '既存', 'description': '既存顧客', 'sort_order': 2},
        {'name': '休眠', 'description': '休眠顧客', 'sort_order': 3},
    ]
    
    for status_data in customer_statuses:
        existing = CustomerStatus.query.filter_by(name=status_data['name']).first()
        if not existing:
            customer_status = CustomerStatus(**status_data)
            db.session.add(customer_status)
            print(f"  ✓ 顧客ステータス「{status_data['name']}」を作成しました")
        else:
            print(f"  - 顧客ステータス「{status_data['name']}」は既に存在します")
    
    # リードソースの作成
    lead_sources = [
        # オンライン
        {'name': '自社Webサイト（問い合わせ）', 'description': '自社Webサイトからの問い合わせ', 'sort_order': 1},
        {'name': '自社Webサイト（資料請求）', 'description': '自社Webサイトからの資料請求', 'sort_order': 2},
        {'name': 'LP（広告用）', 'description': '広告用ランディングページ', 'sort_order': 3},
        {'name': 'オウンドメディア／SEO', 'description': 'オウンドメディアやSEO経由', 'sort_order': 4},
        {'name': 'SNS（X / Instagram / Facebook / TikTok など）', 'description': 'ソーシャルメディア経由', 'sort_order': 5},
        {'name': 'Web広告', 'description': 'Web広告全般', 'sort_order': 6},
        {'name': 'Google広告', 'description': 'Google広告経由', 'sort_order': 7},
        {'name': 'Yahoo広告', 'description': 'Yahoo広告経由', 'sort_order': 8},
        {'name': 'Meta広告', 'description': 'Meta広告（Facebook/Instagram）経由', 'sort_order': 9},
        {'name': 'その他DSP', 'description': 'その他DSP広告経由', 'sort_order': 10},
        # オフライン
        {'name': '電話（インバウンド）', 'description': 'インバウンド電話', 'sort_order': 11},
        {'name': '展示会／イベント', 'description': '展示会やイベントでの接触', 'sort_order': 12},
        {'name': 'セミナー／ウェビナー', 'description': 'セミナーやウェビナー経由', 'sort_order': 13},
        {'name': 'DM（郵送・FAX）', 'description': 'ダイレクトメール（郵送・FAX）', 'sort_order': 14},
        {'name': '飛び込み', 'description': '飛び込み営業', 'sort_order': 15},
        # 人的ネットワーク
        {'name': '紹介（既存顧客）', 'description': '既存顧客からの紹介', 'sort_order': 16},
        {'name': '紹介（パートナー）', 'description': 'パートナーからの紹介', 'sort_order': 17},
        {'name': '代理店', 'description': '代理店経由', 'sort_order': 18},
        {'name': 'アライアンス', 'description': 'アライアンス経由', 'sort_order': 19},
    ]
    
    for source_data in lead_sources:
        existing = LeadSource.query.filter_by(name=source_data['name']).first()
        if not existing:
            lead_source = LeadSource(**source_data)
            db.session.add(lead_source)
            print(f"  ✓ リードソース「{source_data['name']}」を作成しました")
        else:
            print(f"  - リードソース「{source_data['name']}」は既に存在します")
    
    db.session.commit()
    print("\nマスターデータの作成が完了しました！")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        seed_company_masters()

