# CONNECT+ - フルスタックCRMアプリケーション

## Overview
CONNECT+ is a lightweight CRM system designed for sales teams, centralizing customer, deal, and task management. It aims to provide a simple, stylish, and intuitive management tool with a modern UI inspired by Notion and Linear. The project's ambition is to streamline sales operations through enhanced dashboards, comprehensive data management, and insightful analytics.

**Latest Version:** v3.1.0 (Dashboard UI Optimization)

## User Preferences
- デザイン: NotionやLinear風のモダンで直感的なUI
- レスポンシブ対応（PC・タブレット）
- 日本語インターフェース
- データの安全性：既存機能の破壊的変更を避け、スキーマ拡張のみで機能追加

## System Architecture
CONNECT+ is built as a full-stack Flask application using Python for the backend and PostgreSQL for the database. Frontend utilizes Flask templating with TailwindCSS for styling, ensuring a modern and intuitive user experience. Chart.js is integrated for data visualization on the dashboard.

**Key Features:**

*   **Extended Dashboard (v3.1.0 Optimized):** Real-time KPIs with month-over-month comparison (売上/パイプライン/成約率/新規リード + 前月比%). Low-saturation color scheme (emerald/sky/violet/orange). Compact summary section (企業数/連絡先/案件数/総額). Winning strategy summary with Top3 tables for lead source and industry. Stage funnel chart, monthly trend chart (6 months default), alerts for stagnant deals, and period selection.
*   **Customer Management:** CRUD operations for companies and contacts. Companies feature tag management, a detailed view with tabs for deals, contacts, and activity history.
*   **Deal Management:** Lifecycle management including phase tracking, amount/progress updates, "heat score" (A/B/C/ネタ) for prioritization, appointment date tracking, stagnation detection, meeting minutes, and "NEXT ACTION" fields.
*   **Activity History Management:** Tracks various activity types (calls, meetings, emails, notes) displayed in a timeline, automatically updates last contact dates, and links activities to specific deals.
*   **Task Management:** Manages ToDo items linked to deals, with due dates and assignees, filterable by status.
*   **Quotation & Invoice Management:** Features for creating, editing, and issuing quotations and invoices with dynamic item lists, tax calculation, auto-numbering (YYYY-####), and PDF generation using `fpdf2` with Japanese font support. Includes an organization profile setup for company details on documents.
*   **Conversion Analytics:** Dashboard section for win/loss analysis, displaying win rates, and top 5 win/loss reasons visualized with horizontal bar charts, integrated with period selection.
*   **Cross-Tabulation Analytics (v3.0.0):** Advanced analytics dashboard featuring:
    - KPI Summary cards (revenue, new wins, win rate, new leads)
    - Lead Source × Results analysis (appointment rate, win rate, avg amount)
    - Industry × Win Rate / Revenue cross-tabulation
    - Assignee × Activity × Win Rate analysis
    - Stage Funnel visualization with transition rates
    - Monthly Trend charts (revenue, new customers, win rate over time)
    - Lost Reason analysis with mode toggle (by industry/by assignee)
    - All charts connected to period filter for dynamic analysis
*   **User/Account Settings:** Basic login information display and theme switching (dark/light mode).

**UI/UX Decisions:**

*   Modern, intuitive design inspired by Notion and Linear.
*   Responsive design targeting PC and tablet users.
*   Visual alerts (e.g., ⚠️ for stagnant deals).
*   Gradient KPI cards on the dashboard.

**Technical Implementations:**

*   **Backend Framework:** Flask (Python)
*   **Database ORM:** SQLAlchemy
*   **Authentication:** Flask-Login for secure session management.
*   **Frontend Styling:** TailwindCSS for utility-first CSS.
*   **Charting Library:** Chart.js for interactive data visualizations.
*   **PDF Generation:** `fpdf2` with Noto Sans JP font for Japanese character support in PDFs.
*   **Security:** CSRF protection via Flask-WTF, password hashing with Werkzeug.

**Project Structure:**

```
.
├── app.py                    # Main Flask application
├── models.py                 # Database models
├── database.py               # Database connection settings
├── migrate_db.py             # Database migration script
├── seed.py                   # Seed data script
├── README.md                 # Project documentation
├── templates/                # HTML templates (base, login, dashboard, company/deal/task management, settings, etc.)
├── static/                   # Static files (CSS, JS)
├── utils/                    # Utility scripts (pdf_generator.py, numbering.py)
└── requirements.txt         # Python dependencies
```

## External Dependencies
*   **PostgreSQL:** Relational database for all application data.
*   **Flask-Login:** For user authentication and session management.
*   **Flask-WTF:** For form handling and CSRF protection.
*   **TailwindCSS:** CSS framework for styling.
*   **Chart.js:** JavaScript library for data visualization.
*   **fpdf2:** Python library for generating PDF documents.
*   **Werkzeug:** Used for password hashing.