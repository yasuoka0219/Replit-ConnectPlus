# CONNECT+ - フルスタックCRMアプリケーション

営業チーム向けの軽量でモダンなCRMシステム。顧客・案件・タスクを一元管理し、営業プロセスを効率化します。

![CONNECT+ Screenshot](https://via.placeholder.com/800x400?text=CONNECT+CRM)

## 🌟 主要機能

### ダッシュボード
- **リアルタイムKPI**: 月次売上、パイプライン総額、成約率を視覚化
- **グラフ分析**: Chart.jsによる案件ステージ別の可視化
- **アラート機能**: 30日以上滞留している案件を自動検出
- **成長トレンド**: 前月比での売上成長率を表示
- **業界別受注率ランキング**: 業界ごとの受注率を横棒グラフで表示
- **業界別ドリルダウン分析**: 業界と分析種別を選択して詳細データを可視化

### 顧客管理
- **企業プロファイル**: 業界（15業種から選択）、所在地、従業員数、ウェブサイト情報
- **業界分類**: 製造業、IT・ソフトウェア、医療・福祉など15の業界カテゴリ
- **温度感スコア**: 1-5段階の🔥アイコンで商談の熱量を可視化
- **タグ管理**: カンマ区切りで複数タグを設定可能
- **詳細ページ**: タブ形式で案件・担当者・活動履歴を一元表示

### 案件管理
- **ステージ管理**: 初回接触→提案→見積→交渉→成約の段階別管理
- **滞留検知**: 30日以上同じステージにある案件に⚠️バッジ表示
- **金額管理**: 案件ごとの金額と総パイプライン価値を追跡
- **自動トラッキング**: ステージ変更時に滞留日数を自動計算

### 活動履歴
- **多様な活動タイプ**: 電話📞、ミーティング👥、メール📧、メモ📝
- **タイムライン表示**: 最新の活動から時系列で表示
- **顧客連携**: 最終接触日を自動更新
- **案件紐付け**: 各活動を特定の案件に関連付け可能

### タスク管理
- **期限管理**: 案件に紐づくToDoと期限を設定
- **担当者割当**: チームメンバーにタスクを割り当て
- **ステータス追跡**: 未着手・進行中・完了の3段階管理

### 見積・請求管理 (v2.7.0)
- **見積書作成**: 企業ごとの見積書を作成・管理
- **請求書作成**: 企業ごとの請求書を作成・管理
- **採番システム**: YYYY-####形式の自動採番（年ごとにリセット）
- **PDF生成**: 日本語対応のPDF出力（fpdf2使用）
- **組織プロフィール**: 自社情報を登録してPDFに表示
- **明細管理**: 複数品目の動的な追加・編集・削除
- **消費税計算**: 自動的な小計・消費税・合計金額の計算
- **ステータス管理**: 下書き・発行済みの2段階管理

## 🚀 クイックスタート

### 前提条件
- Python 3.10以上
- PostgreSQL（Replitでは自動提供）

### インストール

1. **依存パッケージのインストール**
```bash
pip install -r requirements.txt
```

2. **データベースのマイグレーション**
```bash
python migrate_db.py
```

3. **デモデータの投入（オプション）**
```bash
python seed.py
```

4. **アプリケーションの起動**
```bash
python app.py
```

ブラウザで `http://localhost:5000` にアクセスしてください。

### デモアカウント

シードスクリプトを実行した場合、以下のアカウントでログインできます：

- **メールアドレス**: demo@example.com
- **パスワード**: demo1234

## 📁 プロジェクト構成

```
.
├── app.py                      # メインアプリケーション
├── models.py                   # データベースモデル
├── database.py                 # データベース接続設定
├── migrate_db.py               # マイグレーションスクリプト
├── seed.py                     # シードデータスクリプト
├── requirements.txt            # Python依存パッケージ
├── templates/                  # HTMLテンプレート
│   ├── base.html              # 基本レイアウト
│   ├── login.html             # ログイン
│   ├── register.html          # 新規登録
│   ├── dashboard.html         # ダッシュボード
│   ├── companies.html         # 企業一覧
│   ├── company_detail.html    # 企業詳細（タブUI）
│   ├── company_form.html      # 企業登録/編集
│   ├── contacts.html          # 連絡先一覧
│   ├── contact_form.html      # 連絡先登録/編集
│   ├── deals.html             # 案件一覧
│   ├── deal_form.html         # 案件登録/編集
│   ├── tasks.html             # タスク一覧
│   ├── task_form.html         # タスク登録/編集
│   └── settings.html          # 設定
└── static/                     # 静的ファイル
    ├── css/
    └── js/
```

## 📊 データベース構成

### テーブル一覧

#### users
ユーザー認証情報

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | Integer | 主キー |
| name | String(100) | ユーザー名 |
| email | String(120) | メールアドレス（ユニーク） |
| password_hash | String(200) | パスワードハッシュ |
| created_at | DateTime | 作成日時 |

#### companies
企業情報

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | Integer | 主キー |
| name | String(200) | 企業名 |
| industry | String(100) | 業種 |
| location | String(200) | 所在地 |
| employee_size | Integer | 従業員数 |
| hq_location | String(200) | 本社所在地 |
| website | String(300) | ウェブサイトURL |
| needs | Text | ニーズ |
| kpi_current | Text | 現状KPI |
| heat_score | Integer | 温度感スコア（1-5） |
| last_contacted_at | DateTime | 最終接触日 |
| next_action_at | DateTime | 次回アクション予定日 |
| tags | String(500) | タグ（カンマ区切り） |
| memo | Text | メモ |
| created_at | DateTime | 作成日時 |

#### contacts
連絡先情報

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | Integer | 主キー |
| company_id | Integer | 企業ID（外部キー） |
| name | String(100) | 氏名 |
| title | String(100) | 役職 |
| email | String(120) | メールアドレス |
| phone | String(20) | 電話番号 |
| role | String(100) | 役割（意思決定者など） |
| notes | Text | メモ |
| created_at | DateTime | 作成日時 |

#### deals
案件情報

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | Integer | 主キー |
| company_id | Integer | 企業ID（外部キー） |
| title | String(200) | 案件名 |
| stage | String(50) | ステージ |
| amount | Float | 金額 |
| status | String(50) | ステータス |
| stage_entered_at | DateTime | ステージ開始日時 |
| note | Text | メモ |
| created_at | DateTime | 作成日時 |

#### tasks
タスク情報

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | Integer | 主キー |
| deal_id | Integer | 案件ID（外部キー） |
| title | String(200) | タスク名 |
| due_date | Date | 期限 |
| status | String(50) | ステータス |
| assignee | String(100) | 担当者 |
| created_at | DateTime | 作成日時 |

#### activities
活動履歴

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | Integer | 主キー |
| company_id | Integer | 企業ID（外部キー） |
| deal_id | Integer | 案件ID（外部キー、NULL可） |
| user_id | Integer | ユーザーID（外部キー） |
| type | String(50) | 活動タイプ（call/meeting/email/note） |
| title | String(200) | タイトル |
| body | Text | 本文 |
| happened_at | DateTime | 発生日時 |
| created_at | DateTime | 作成日時 |

## 🎨 技術スタック

### バックエンド
- **Flask**: Pythonの軽量Webフレームワーク
- **SQLAlchemy**: ORMライブラリ
- **PostgreSQL**: リレーショナルデータベース
- **Flask-Login**: 認証管理
- **Flask-WTF**: フォーム処理とCSRF保護
- **Flask-Migrate**: データベースマイグレーション

### フロントエンド
- **TailwindCSS**: ユーティリティファーストCSSフレームワーク
- **Chart.js**: データ可視化ライブラリ
- **Vanilla JavaScript**: ダイナミックなUI更新

### セキュリティ
- **CSRF保護**: 全てのPOSTリクエストにCSRFトークン
- **パスワードハッシュ**: Werkzeugによる安全なハッシュ化
- **セッション管理**: Flask-Loginによる安全な認証

## 🔧 API エンドポイント

### 認証
- `POST /login` - ログイン
- `POST /register` - 新規登録
- `GET /logout` - ログアウト

### ダッシュボード
- `GET /api/dashboard-data` - 基本統計データ
- `GET /api/dashboard-kpis` - 拡張KPIデータ

### 業界分析
- `GET /api/analytics/industry/win_rate_ranking` - 業界別受注率ランキング
- `GET /api/analytics/industry/avg_amount` - 業界別平均単価
- `GET /api/analytics/industry/win_rate` - 業界別受注率
- `GET /api/analytics/industry/win_reasons` - 業界別受注理由分布
- `GET /api/analytics/industry/loss_reasons` - 業界別失注理由分布

### 企業
- `GET /companies` - 企業一覧
- `GET /companies/<id>` - 企業詳細
- `GET /api/companies/<id>` - 企業詳細（JSON）
- `PUT /api/companies/<id>` - 企業更新（JSON）
- `POST /companies/create` - 企業作成
- `POST /companies/<id>/edit` - 企業編集
- `POST /companies/<id>/delete` - 企業削除

### 活動履歴
- `GET /api/companies/<id>/activities` - 企業の活動履歴取得
- `POST /api/companies/<id>/activities` - 活動履歴作成

### 案件・連絡先・タスク
各リソースに対して、一覧、作成、編集、削除のエンドポイントが用意されています。

## 🎯 開発のポイント

### 新機能の追加方法

1. **モデル変更時**: `migrate_db.py`を実行してスキーマを更新
2. **新しいページ追加**: `templates/`にHTMLファイルを作成し、`app.py`にルートを追加
3. **API追加**: `app.py`に新しいルートを追加し、JSON形式でレスポンス

### コーディング規約
- PEP 8に準拠したPythonコード
- テンプレートはJinja2構文を使用
- クラス名はPascalCase、関数名はsnake_case
- 全てのPOSTフォームに`csrf_token()`を含める

## 🔐 セキュリティ

### 実装済みのセキュリティ対策
- ✅ CSRF保護（Flask-WTF）
- ✅ SQLインジェクション対策（SQLAlchemy ORM）
- ✅ パスワードハッシュ化（Werkzeug）
- ✅ セッション管理（Flask-Login）
- ✅ XSS対策（Jinja2自動エスケープ）

### 本番環境での推奨事項
- 環境変数で機密情報を管理
- HTTPS通信の強制
- レート制限の実装
- 定期的なセキュリティアップデート

## 📈 パフォーマンス

### 最適化施策
- データベースインデックス（name, heat_score）
- 遅延ロード（活動履歴はタブクリック時に取得）
- ページネーション（活動履歴APIはlimit/offset対応）

## 🐛 トラブルシューティング

### よくある問題

**Q: データベース接続エラーが出る**
A: `DATABASE_URL`環境変数が正しく設定されているか確認してください。

**Q: マイグレーションが失敗する**
A: 既存データがある場合、`migrate_db.py`は安全に実行できますが、手動でデータベースをバックアップすることをお勧めします。

**Q: シードデータが投入できない**
A: データベースが初期化されているか確認し、`python migrate_db.py`を先に実行してください。

**Q: ログインできない**
A: シードデータを実行した場合は `demo@example.com / demo1234` でログイン可能です。新規ユーザーは `/register` から登録してください。

## 🚢 デプロイ

Replitでのデプロイは簡単です：

1. Replitの「Deploy」ボタンをクリック
2. デプロイタイプを選択（Autoscale推奨）
3. 環境変数を設定（`DATABASE_URL`、`SESSION_SECRET`）
4. デプロイを実行

## ✨ 業界分析機能 (v2.8.0)

### 業界分類
全ての企業は以下の15業界から選択可能：
- 製造業
- 小売・卸売
- 飲食・宿泊
- IT・ソフトウェア
- 広告・メディア
- 建設・不動産
- 人材・教育
- 医療・福祉
- 金融・保険
- 物流・運輸
- 自治体・公共
- 専門サービス
- エネルギー・インフラ
- エンタメ・スポーツ
- その他

### ダッシュボード機能
1. **業界別受注率ランキング**
   - 業界ごとの受注率を降順で表示
   - 横棒グラフ（Horizontal Bar）で可視化
   - ツールチップに受注件数・失注件数を表示

2. **業界別ドリルダウン分析**
   - 業界選択：15業界＋「すべて」から選択
   - 分析種別の選択：
     - 平均単価：受注案件の平均金額を表示
     - 受注率：WON / (WON+LOST) の割合を表示
     - 受注理由：カテゴリ別の受注理由分布（Doughnutチャート）
     - 失注理由：カテゴリ別の失注理由分布（Doughnutチャート）
   - 期間フィルタ：今月・四半期・今年・カスタム期間に対応

### 動作確認手順

1. **データベースマイグレーション**
   ```bash
   python migrate_db.py
   ```
   ※ companies.industry列にインデックスが作成されます

2. **企業の業界設定**
   - 企業編集画面（`/companies/<id>/edit`）にアクセス
   - 「業界」プルダウンから業界を選択
   - 既存企業は「未設定」状態

3. **案件のクローズと理由入力**
   - 案件を「受注（WON）」または「失注（LOST）」に変更
   - ステータス変更時に受注/失注理由カテゴリと詳細を入力
   - closed_atが自動的に記録されます

4. **ダッシュボードで確認**
   - `/dashboard`にアクセス
   - 「業界別受注率ランキング」グラフを確認
   - 「業界別分析」セクションで業界と分析種別を選択
   - 期間フィルタで集計期間を変更

### 技術詳細

**パフォーマンス最適化:**
- companies.industryにインデックス作成
- deals.closed_at、deals.win_reason_category、deals.lost_reason_categoryにインデックス作成
- JOINクエリで効率的なデータ取得

**エラーハンドリング:**
- APIエラー時もUI崩壊なし、トースト通知で表示
- 空データ時は「データがありません」メッセージを表示

**レスポンシブ対応:**
- PC・タブレットでの表示に最適化
- グラフはChart.jsの responsive: true で自動調整

## 📝 更新履歴

### v2.8.0 (2025-11-14)
- ✨ 業界分類機能を追加（15業界から選択）
- ✨ 業界別受注率ランキンググラフを追加
- ✨ 業界別ドリルダウン分析機能を追加（平均単価・受注率・理由分析）
- ✨ 5つの業界分析APIエンドポイントを追加
- 🔧 データベースインデックスを追加（パフォーマンス最適化）
- 🗑️ 案件ステータス別グラフを削除（業界別ランキングに置き換え）

### v2.0.0 (2025-11-12)
- 🎉 大規模機能拡張リリース
- ✨ 企業詳細ページ（タブUI）を追加
- ✨ 活動履歴機能を追加（電話・MTG・メール・メモ）
- ✨ 拡張KPIダッシュボード（月次売上、パイプライン、成約率）
- ✨ 温度感スコア（1-5段階）を追加
- ✨ タグ機能を追加
- ✨ 案件滞留検知機能を追加
- ✨ ステージ滞留日数の自動計算
- 🔧 データベースマイグレーションスクリプトを追加
- 🔧 シードデータスクリプトを追加
- 🎨 UIをモダンに刷新

### v1.0.0 (2025-11-11)
- 🎉 初回リリース
- ✨ 基本CRUD機能（企業・連絡先・案件・タスク）
- ✨ ダッシュボードとChart.js可視化
- ✨ ユーザー認証（Flask-Login）
- ✨ ダーク/ライトモード対応

## 👥 貢献

プルリクエストを歓迎します！大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 📄 ライセンス

MIT License

## 🙏 謝辞

- [Flask](https://flask.palletsprojects.com/)
- [TailwindCSS](https://tailwindcss.com/)
- [Chart.js](https://www.chartjs.org/)
- Replit Community

---

**CONNECT+** - 営業チームの生産性を最大化するCRMシステム
