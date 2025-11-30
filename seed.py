#!/usr/bin/env python
"""
CONNECT+ Seed Data Script
デモンストレーション用のサンプルデータを投入します
"""

import os
from datetime import datetime, timedelta, date
from app import app
from database import db
from models import User, Company, Contact, Deal, Task, Activity
from werkzeug.security import generate_password_hash

def clear_data():
    """既存のデータをクリア"""
    print("既存データをクリアしています...")
    Activity.query.delete()
    Task.query.delete()
    Deal.query.delete()
    Contact.query.delete()
    Company.query.delete()
    User.query.delete()
    db.session.commit()
    print("✓ データクリア完了")

def create_users():
    """ユーザーを作成"""
    print("\nユーザーを作成しています...")
    
    demo_user = User(
        name="山田太郎",
        email="demo@example.com",
        password_hash=generate_password_hash("demo1234", method='pbkdf2:sha256')
    )
    db.session.add(demo_user)
    db.session.commit()
    
    print(f"✓ ユーザー作成: {demo_user.name} ({demo_user.email})")
    return demo_user

def create_companies(user):
    """企業データを作成"""
    print("\n企業データを作成しています...")
    
    companies_data = [
        {
            "name": "株式会社テクノロジーソリューションズ",
            "industry": "IT・ソフトウェア",
            "location": "東京都渋谷区",
            "employee_size": 400,
            "hq_location": "東京本社",
            "website": "https://techsol.example.com",
            "needs": "営業プロセスのDX化、顧客データの一元管理",
            "kpi_current": "月間商談数: 50件、成約率: 15%",
            "heat_score": 5,
            "tags": "大手,優先,DX,SaaS",
            "memo": "決裁者との関係良好。来期予算確保済み。従業員数約400名。"
        },
        {
            "name": "グローバルトレーディング株式会社",
            "industry": "商社・貿易",
            "location": "大阪府大阪市",
            "employee_size": 200,
            "hq_location": "大阪本社",
            "website": "https://globaltrade.example.com",
            "needs": "在庫管理システムの刷新",
            "kpi_current": "在庫回転率: 年6回、欠品率: 2%",
            "heat_score": 4,
            "tags": "関西,成長中",
            "memo": "競合と比較検討中。価格重視の傾向あり。従業員数約200名。"
        },
        {
            "name": "株式会社マーケティングエクスプレス",
            "industry": "広告・マーケティング",
            "location": "東京都港区",
            "employee_size": 75,
            "hq_location": "東京本社",
            "website": "https://mktexpress.example.com",
            "needs": "マーケティングオートメーション導入",
            "kpi_current": "リード獲得数: 月200件、CVR: 3%",
            "heat_score": 3,
            "tags": "スタートアップ,成長中",
            "memo": "予算は限定的だが、導入意欲は高い。従業員数約75名。"
        },
        {
            "name": "日本製造株式会社",
            "industry": "製造業",
            "location": "愛知県名古屋市",
            "employee_size": 750,
            "hq_location": "名古屋本社",
            "heat_score": 2,
            "tags": "製造,老舗",
            "memo": "初回MTG実施。ニーズ深堀りが必要。従業員数約750名。"
        },
        {
            "name": "株式会社リテールチェーン",
            "industry": "小売・流通",
            "location": "東京都新宿区",
            "employee_size": 1200,
            "hq_location": "東京本社",
            "website": "https://retailchain.example.com",
            "needs": "店舗運営の効率化、POSシステム刷新",
            "heat_score": 4,
            "tags": "大手,優先,小売",
            "memo": "複数店舗での実証実験を検討中。従業員数約1200名。"
        }
    ]
    
    companies = []
    for data in companies_data:
        company = Company(**data)
        db.session.add(company)
        companies.append(company)
    
    db.session.commit()
    print(f"✓ {len(companies)}件の企業を作成")
    return companies

def create_contacts(companies):
    """連絡先データを作成"""
    print("\n連絡先データを作成しています...")
    
    contacts_data = [
        # テクノロジーソリューションズ
        {"company_id": companies[0].id, "name": "佐藤健一", "title": "CIO", "email": "k.sato@techsol.example.com", "phone": "03-1234-5678", "role": "意思決定者", "notes": "情報システム部所属。技術的な判断を担当。"},
        {"company_id": companies[0].id, "name": "鈴木美咲", "title": "営業部長", "email": "m.suzuki@techsol.example.com", "phone": "03-1234-5679", "role": "エンドユーザー", "notes": "営業部所属。実際の利用者。"},
        
        # グローバルトレーディング
        {"company_id": companies[1].id, "name": "田中誠", "title": "取締役", "email": "m.tanaka@globaltrade.example.com", "phone": "06-9876-5432", "role": "意思決定者", "notes": "経営企画室所属。予算承認権限あり。"},
        
        # マーケティングエクスプレス
        {"company_id": companies[2].id, "name": "高橋花子", "title": "マーケティングマネージャー", "email": "h.takahashi@mktexpress.example.com", "phone": "03-5555-1234", "role": "窓口担当", "notes": "マーケティング部所属。"},
        
        # 日本製造
        {"company_id": companies[3].id, "name": "渡辺太郎", "title": "製造部長", "email": "t.watanabe@nipponmfg.example.com", "phone": "052-777-8888", "role": "エンドユーザー", "notes": "製造部所属。"},
        
        # リテールチェーン
        {"company_id": companies[4].id, "name": "伊藤真一", "title": "システム部長", "email": "s.ito@retailchain.example.com", "phone": "03-6666-7777", "role": "意思決定者", "notes": "システム部所属。技術選定を担当。"},
        {"company_id": companies[4].id, "name": "山本明美", "title": "店舗運営部長", "email": "a.yamamoto@retailchain.example.com", "phone": "03-6666-7778", "role": "エンドユーザー", "notes": "店舗運営部所属。実運用の責任者。"}
    ]
    
    contacts = []
    for data in contacts_data:
        contact = Contact(**data)
        db.session.add(contact)
        contacts.append(contact)
    
    db.session.commit()
    print(f"✓ {len(contacts)}件の連絡先を作成")
    return contacts

def create_deals(companies, user):
    """案件データを作成"""
    print("\n案件データを作成しています...")
    
    today = date.today()
    
    deals_data = [
        {
            "company_id": companies[0].id,
            "title": "CRMシステム導入プロジェクト",
            "stage": "交渉",
            "amount": 15000000,
            "status": "進行中",
            "note": "年度内導入を目指す。3社比較中。",
            "stage_entered_at": datetime.now() - timedelta(days=15)
        },
        {
            "company_id": companies[0].id,
            "title": "営業データ分析ツール",
            "stage": "提案",
            "amount": 3000000,
            "status": "進行中",
            "note": "CRMと連携予定。",
            "stage_entered_at": datetime.now() - timedelta(days=8)
        },
        {
            "company_id": companies[1].id,
            "title": "在庫管理システム",
            "stage": "見積",
            "amount": 8000000,
            "status": "進行中",
            "note": "見積提出済み。価格交渉の可能性あり。",
            "stage_entered_at": datetime.now() - timedelta(days=45)  # 滞留案件
        },
        {
            "company_id": companies[2].id,
            "title": "マーケティングオートメーション",
            "stage": "初回接触",
            "amount": 5000000,
            "status": "進行中",
            "note": "課題ヒアリング実施済み。",
            "stage_entered_at": datetime.now() - timedelta(days=3)
        },
        {
            "company_id": companies[3].id,
            "title": "生産管理システム",
            "stage": "初回接触",
            "amount": 12000000,
            "status": "進行中",
            "note": "ニーズ確認中。",
            "stage_entered_at": datetime.now() - timedelta(days=35)  # 滞留案件
        },
        {
            "company_id": companies[4].id,
            "title": "POSシステム刷新",
            "stage": "提案",
            "amount": 25000000,
            "status": "進行中",
            "note": "店舗での実証実験を提案中。",
            "stage_entered_at": datetime.now() - timedelta(days=20)
        },
        {
            "company_id": companies[4].id,
            "title": "店舗在庫連携システム",
            "stage": "交渉",
            "amount": 8000000,
            "status": "進行中",
            "note": "契約直前。細部を詰めている。",
            "stage_entered_at": datetime.now() - timedelta(days=5)
        },
        # 過去の受注案件
        {
            "company_id": companies[0].id,
            "title": "名刺管理システム導入",
            "stage": "成約",
            "amount": 1200000,
            "status": "受注",
            "note": "導入完了、満足度高い。",
            "created_at": datetime.now() - timedelta(days=60),
            "stage_entered_at": datetime.now() - timedelta(days=30)
        },
        {
            "company_id": companies[1].id,
            "title": "勤怠管理システム",
            "stage": "成約",
            "amount": 2500000,
            "status": "受注",
            "note": "運用中。追加提案の余地あり。",
            "created_at": datetime.now() - timedelta(days=90),
            "stage_entered_at": datetime.now() - timedelta(days=60)
        }
    ]
    
    deals = []
    for data in deals_data:
        deal = Deal(**data)
        db.session.add(deal)
        deals.append(deal)
    
    db.session.commit()
    print(f"✓ {len(deals)}件の案件を作成")
    return deals

def create_tasks(deals, user):
    """タスクデータを作成"""
    print("\nタスクデータを作成しています...")
    
    today = date.today()
    
    tasks_data = [
        {"deal_id": deals[0].id, "title": "契約書ドラフト作成", "due_date": today + timedelta(days=3), "status": "進行中", "assignee": user.name},
        {"deal_id": deals[0].id, "title": "デモ環境セットアップ", "due_date": today + timedelta(days=7), "status": "未着手", "assignee": "技術部 山本"},
        {"deal_id": deals[1].id, "title": "提案書最終確認", "due_date": today + timedelta(days=1), "status": "進行中", "assignee": user.name},
        {"deal_id": deals[2].id, "title": "価格交渉フォローアップ", "due_date": today + timedelta(days=5), "status": "未着手", "assignee": user.name},
        {"deal_id": deals[5].id, "title": "実証実験計画書作成", "due_date": today + timedelta(days=10), "status": "未着手", "assignee": "企画部 佐藤"},
        {"deal_id": deals[6].id, "title": "最終見積提出", "due_date": today + timedelta(days=2), "status": "進行中", "assignee": user.name},
    ]
    
    tasks = []
    for data in tasks_data:
        task = Task(**data)
        db.session.add(task)
        tasks.append(task)
    
    db.session.commit()
    print(f"✓ {len(tasks)}件のタスクを作成")
    return tasks

def create_activities(companies, deals, user):
    """活動履歴データを作成"""
    print("\n活動履歴データを作成しています...")
    
    activities_data = [
        # テクノロジーソリューションズ
        {
            "company_id": companies[0].id,
            "deal_id": deals[0].id,
            "user_id": user.id,
            "type": "meeting",
            "title": "CIO面談 - 要件ヒアリング",
            "body": "・現状の課題：営業データが分散、レポート作成に時間がかかる\n・導入目標：営業効率30%向上\n・予算：1500万円程度\n・導入時期：来年度Q1",
            "happened_at": datetime.now() - timedelta(days=10)
        },
        {
            "company_id": companies[0].id,
            "deal_id": deals[0].id,
            "user_id": user.id,
            "type": "call",
            "title": "営業部長との電話MTG",
            "body": "デモの日程調整。来週火曜日14時で確定。",
            "happened_at": datetime.now() - timedelta(days=3)
        },
        {
            "company_id": companies[0].id,
            "user_id": user.id,
            "type": "email",
            "title": "提案書送付",
            "body": "CRMシステムの詳細提案書をメール送信。3営業日以内に回答予定。",
            "happened_at": datetime.now() - timedelta(days=1)
        },
        # グローバルトレーディング
        {
            "company_id": companies[1].id,
            "deal_id": deals[2].id,
            "user_id": user.id,
            "type": "meeting",
            "title": "取締役との商談",
            "body": "見積内容について説明。価格が予算オーバーとのこと。値引き交渉の可能性あり。",
            "happened_at": datetime.now() - timedelta(days=20)
        },
        {
            "company_id": companies[1].id,
            "user_id": user.id,
            "type": "note",
            "title": "競合情報",
            "body": "A社とB社が提案中。価格面でB社が有利との情報。機能面で差別化が必要。",
            "happened_at": datetime.now() - timedelta(days=15)
        },
        # マーケティングエクスプレス
        {
            "company_id": companies[2].id,
            "deal_id": deals[3].id,
            "user_id": user.id,
            "type": "meeting",
            "title": "初回訪問",
            "body": "マーケティングマネージャーと面談。リード獲得の課題をヒアリング。",
            "happened_at": datetime.now() - timedelta(days=3)
        },
        # リテールチェーン
        {
            "company_id": companies[4].id,
            "deal_id": deals[5].id,
            "user_id": user.id,
            "type": "meeting",
            "title": "システム部長との打ち合わせ",
            "body": "POSシステムの現状課題を確認。実証実験の実施を提案。",
            "happened_at": datetime.now() - timedelta(days=18)
        },
        {
            "company_id": companies[4].id,
            "deal_id": deals[6].id,
            "user_id": user.id,
            "type": "call",
            "title": "契約条件の確認",
            "body": "店舗運営部長と電話。契約条件について最終確認。来週契約予定。",
            "happened_at": datetime.now() - timedelta(days=2)
        }
    ]
    
    activities = []
    for data in activities_data:
        activity = Activity(**data)
        db.session.add(activity)
        activities.append(activity)
        
        # Update company last_contacted_at
        company = Company.query.get(data['company_id'])
        if company:
            if not company.last_contacted_at or data['happened_at'] > company.last_contacted_at:
                company.last_contacted_at = data['happened_at']
    
    db.session.commit()
    print(f"✓ {len(activities)}件の活動履歴を作成")
    return activities

def main():
    """メイン実行"""
    print("=" * 60)
    print("CONNECT+ シードデータ投入スクリプト")
    print("=" * 60)
    
    with app.app_context():
        # データベース初期化
        db.create_all()
        
        # データクリア
        clear_data()
        
        # データ作成
        user = create_users()
        companies = create_companies(user)
        contacts = create_contacts(companies)
        deals = create_deals(companies, user)
        tasks = create_tasks(deals, user)
        activities = create_activities(companies, deals, user)
        
        print("\n" + "=" * 60)
        print("✓ シードデータ投入完了")
        print("=" * 60)
        print("\nログイン情報:")
        print("  メールアドレス: demo@example.com")
        print("  パスワード: demo1234")
        print("\nデータサマリー:")
        print(f"  ユーザー: 1件")
        print(f"  企業: {len(companies)}件")
        print(f"  連絡先: {len(contacts)}件")
        print(f"  案件: {len(deals)}件")
        print(f"  タスク: {len(tasks)}件")
        print(f"  活動履歴: {len(activities)}件")
        print("\nアプリケーションを起動してログインしてください:")
        print("  python app.py")
        print("=" * 60)

if __name__ == "__main__":
    main()
