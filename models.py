from database import db
from flask_login import UserMixin
from datetime import datetime, timedelta


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', back_populates='team', lazy=True)
    deals = db.relationship('Deal', back_populates='team', lazy=True)

    def __repr__(self):
        return f'<Team {self.name}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member', index=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 2FA (Two-Factor Authentication) fields
    two_factor_secret = db.Column(db.String(32), nullable=True)  # TOTP secret key (for app-based 2FA)
    two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_type = db.Column(db.String(20), nullable=True, default='app')  # 'app' for TOTP/QR, 'email' for email-based
    two_factor_backup_codes = db.Column(db.Text, nullable=True)  # JSON array of backup codes
    
    # Account lockout fields
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)

    team = db.relationship('Team', back_populates='users')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def is_locked(self):
        """Check if account is locked"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def lock_account(self, minutes=30):
        """Lock account for specified minutes"""
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        self.failed_login_attempts = 0
    
    def unlock_account(self):
        """Unlock account and reset failed attempts"""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def increment_failed_attempts(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
    
    def reset_failed_attempts(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    industry = db.Column(db.String(100), nullable=True, index=True)  # Industry/sector classification
    location = db.Column(db.String(200))
    memo = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New extended fields
    employee_size = db.Column(db.Integer, nullable=True)
    hq_location = db.Column(db.String(200), nullable=True)
    website = db.Column(db.String(300), nullable=True)
    needs = db.Column(db.Text, nullable=True)
    kpi_current = db.Column(db.Text, nullable=True)
    heat_score = db.Column(db.Integer, nullable=True, default=1)  # 1-5段階の温度感スコア
    last_contacted_at = db.Column(db.DateTime, nullable=True)
    next_action_at = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)  # Comma-separated for now, can migrate to JSON later
    
    # Analysis & Classification fields (v3.0.0)
    company_size_id = db.Column(db.Integer, db.ForeignKey('company_sizes.id'), nullable=True, index=True)  # 企業規模
    area = db.Column(db.String(200), nullable=True, index=True)  # エリア（都道府県など）
    customer_status_id = db.Column(db.Integer, db.ForeignKey('customer_statuses.id'), nullable=True, index=True)  # 顧客ステータス（新規/既存/休眠）
    
    contacts = db.relationship('Contact', backref='company', lazy=True, cascade='all, delete-orphan')
    deals = db.relationship('Deal', backref='company', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='company', lazy=True, cascade='all, delete-orphan')
    company_size = db.relationship('CompanySize', backref='companies')
    customer_status = db.relationship('CustomerStatus', backref='companies')
    
    def __repr__(self):
        return f'<Company {self.name}>'
    
    def get_tags_list(self):
        """Helper method to get tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags_list(self, tags_list):
        """Helper method to set tags from a list"""
        self.tags = ','.join(tags_list) if tags_list else None

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New extended fields
    role = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Contact {self.name}>'

class Deal(db.Model):
    __tablename__ = 'deals'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    stage = db.Column(db.String(50), nullable=False, index=True)
    amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), nullable=False, index=True)  # 'OPEN', 'WON', 'LOST'
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True, index=True)
    
    # Extended fields
    stage_entered_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    assignee = db.Column(db.String(100), nullable=True, index=True)  # 後方互換性のため残す
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)  # 担当者（User ID）
    meeting_minutes = db.Column(db.Text, nullable=True)
    next_action = db.Column(db.Text, nullable=True)
    heat_score = db.Column(db.String(20), default='C', nullable=True, index=True)  # 'A', 'B', 'C', 'ネタ'
    appointment_date = db.Column(db.Date, nullable=True, index=True)
    
    # Win/Loss reason fields (v2.6.0)
    win_reason_category = db.Column(db.String(100), nullable=True, index=True)
    win_reason_detail = db.Column(db.Text, nullable=True)
    lost_reason_category = db.Column(db.String(100), nullable=True, index=True)
    lost_reason_detail = db.Column(db.Text, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True, index=True)
    revenue_month = db.Column(db.String(7), nullable=True, index=True)  # 'YYYY-MM' format
    
    # Analysis fields (v3.0.0)
    lead_source_id = db.Column(db.Integer, db.ForeignKey('lead_sources.id'), nullable=True, index=True)  # リードソース
    new_or_existing = db.Column(db.String(20), nullable=True, index=True)  # '新規' or '既存'
    gross_profit = db.Column(db.Float, nullable=True)  # 粗利
    won_date = db.Column(db.Date, nullable=True, index=True)  # 受注日
    lost_date = db.Column(db.Date, nullable=True, index=True)  # 失注日
    probability_rank = db.Column(db.String(10), nullable=True, index=True)  # 見込ランク（A/B/C）
    competitor_name = db.Column(db.String(200), nullable=True)  # 競合名
    first_contact_date = db.Column(db.Date, nullable=True, index=True)  # 初回接触日
    proposal_date = db.Column(db.Date, nullable=True, index=True)  # 提案日
    
    # Relationships
    assignee_user = db.relationship('User', foreign_keys=[assignee_id], backref='assigned_deals')
    team = db.relationship('Team', back_populates='deals')
    lead_source = db.relationship('LeadSource', backref='deals')
    tasks = db.relationship('Task', backref='deal', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='deal', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Deal {self.title}>'
    
    @property
    def days_in_stage(self):
        """Calculate days in current stage"""
        if self.stage_entered_at:
            return (datetime.utcnow() - self.stage_entered_at).days
        return 0
    
    
    def get_assignee_name(self):
        """Get assignee name (from User if assignee_id exists, else from assignee string)"""
        if self.assignee_id and self.assignee_user:
            return self.assignee_user.name
        elif self.assignee:
            return self.assignee
        return None

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=True)
    deal_name = db.Column(db.String(200), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False)
    assignee = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Google Calendar integration
    google_calendar_event_id = db.Column(db.String(255), nullable=True, index=True)
    
    def __repr__(self):
        return f'<Task {self.title}>'


class Activity(db.Model):
    """Activity log for tracking interactions with companies"""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=True)
    
    type = db.Column(db.String(20), nullable=False)  # call, meeting, email, note
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=True)
    happened_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Google Calendar integration
    google_calendar_event_id = db.Column(db.String(255), nullable=True, index=True)
    
    # Activity analysis fields (v3.0.0)
    count = db.Column(db.Integer, default=1, nullable=False)  # 件数
    duration_minutes = db.Column(db.Integer, nullable=True)  # 所要時間（分）
    memo = db.Column(db.Text, nullable=True)  # メモ（body とは別）
    
    # Relationships
    user = db.relationship('User', backref='activities', lazy=True)
    
    # Create compound index for (company_id, happened_at DESC)
    __table_args__ = (
        db.Index('ix_activities_company_happened', 'company_id', 'happened_at'),
    )
    
    def __repr__(self):
        return f'<Activity {self.type}: {self.title}>'
    
    def to_dict(self):
        """Convert activity to dictionary for JSON responses"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'user_id': self.user_id,
            'deal_id': self.deal_id,
            'type': self.type,
            'title': self.title,
            'body': self.body,
            'happened_at': self.happened_at.isoformat() if self.happened_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_name': self.user.name if self.user else None
        }


class OrgProfile(db.Model):
    """Organization profile for PDF generation"""
    __tablename__ = 'org_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    org_name = db.Column(db.String(200), nullable=False, default='')
    org_name_kana = db.Column(db.String(200), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    representative = db.Column(db.String(100), nullable=True)
    registration_number = db.Column(db.String(100), nullable=True)
    bank_info = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<OrgProfile {self.org_name}>'


class Quote(db.Model):
    """Quote/Estimate model"""
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=True, index=True)
    quote_no = db.Column(db.String(50), unique=True, nullable=True, index=True)
    issue_date = db.Column(db.Date, nullable=False)
    expire_date = db.Column(db.Date, nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    currency = db.Column(db.String(10), default='JPY', nullable=False)
    tax_rate = db.Column(db.Float, default=0.10, nullable=False)
    subtotal = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='発行済み', nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    company = db.relationship('Company', backref='quotes')
    contact = db.relationship('Contact', backref='quotes')
    deal = db.relationship('Deal', backref='quotes')
    items = db.relationship('QuoteItem', backref='quote', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Quote {self.quote_no or self.id}: {self.subject}>'
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total from items"""
        self.subtotal = sum(item.line_total for item in self.items)
        self.tax_amount = round(self.subtotal * self.tax_rate)
        self.total = self.subtotal + self.tax_amount


class QuoteItem(db.Model):
    """Quote item/line model"""
    __tablename__ = 'quote_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False, index=True)
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    qty = db.Column(db.Float, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0)
    tax_rate = db.Column(db.Float, default=0.10, nullable=False)
    line_total = db.Column(db.Float, default=0)
    
    def __repr__(self):
        return f'<QuoteItem {self.item_name}>'
    
    def calculate_line_total(self):
        """Calculate line total from qty and unit_price"""
        self.line_total = self.qty * self.unit_price


class Invoice(db.Model):
    """Invoice model"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=True, index=True)
    invoice_no = db.Column(db.String(50), unique=True, nullable=True, index=True)
    issue_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    currency = db.Column(db.String(10), default='JPY', nullable=False)
    tax_rate = db.Column(db.Float, default=0.10, nullable=False)
    subtotal = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, nullable=True)
    person_in_charge = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='発行済み', nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    company = db.relationship('Company', backref='invoices')
    contact = db.relationship('Contact', backref='invoices')
    deal = db.relationship('Deal', backref='invoices')
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_no or self.id}: {self.subject}>'
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total from items"""
        self.subtotal = sum(item.line_total for item in self.items)
        self.tax_amount = round(self.subtotal * self.tax_rate)
        self.total = self.subtotal + self.tax_amount


class InvoiceItem(db.Model):
    """Invoice item/line model"""
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False, index=True)
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    qty = db.Column(db.Float, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0)
    tax_rate = db.Column(db.Float, default=0.10, nullable=False)
    line_total = db.Column(db.Float, default=0)
    
    def __repr__(self):
        return f'<InvoiceItem {self.item_name}>'
    
    def calculate_line_total(self):
        """Calculate line total from qty and unit_price"""
        self.line_total = self.qty * self.unit_price


class LoginAttempt(db.Model):
    """Login attempt tracking for brute force protection"""
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6対応
    user_agent = db.Column(db.String(500), nullable=True)
    success = db.Column(db.Boolean, default=False, nullable=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='login_attempts')
    
    def __repr__(self):
        return f'<LoginAttempt {self.email}: {"success" if self.success else "failed"}>'


class SecurityLog(db.Model):
    """Security audit log for tracking important security events"""
    __tablename__ = 'security_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)  # login, logout, password_change, 2fa_enabled, etc.
    event_description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    resource_type = db.Column(db.String(50), nullable=True)  # company, deal, contact, etc.
    resource_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', backref='security_logs')
    
    def __repr__(self):
        return f'<SecurityLog {self.event_type} by {self.user_id or "anonymous"}>'
    
    def to_dict(self):
        """Convert security log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'event_type': self.event_type,
            'event_description': self.event_description,
            'ip_address': self.ip_address,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Email2FACode(db.Model):
    """Email 2FA verification code storage"""
    __tablename__ = 'email_2fa_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    code = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='email_2fa_codes')
    
    def __repr__(self):
        return f'<Email2FACode user_id={self.user_id} used={self.used}>'
    
    def is_valid(self):
        """Check if code is still valid"""
        return not self.used and datetime.utcnow() <= self.expires_at


class PasswordResetToken(db.Model):
    """Password reset token storage"""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    used = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='password_reset_tokens')
    
    def __repr__(self):
        return f'<PasswordResetToken user_id={self.user_id} used={self.used}>'
    
    def is_valid(self):
        """Check if token is still valid"""
        return not self.used and datetime.utcnow() <= self.expires_at


class GoogleCalendarConnection(db.Model):
    """Google Calendar OAuth connection for users"""
    __tablename__ = 'google_calendar_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    
    # OAuth token information (encrypted in production)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    
    # Connection metadata
    calendar_id = db.Column(db.String(255), nullable=True, default='primary')  # Default calendar ID
    connected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_sync_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='google_calendar_connection')
    
    def __repr__(self):
        return f'<GoogleCalendarConnection user_id={self.user_id} active={self.is_active}>'
    
    def is_token_expired(self):
        """Check if access token is expired"""
        if not self.token_expiry:
            return True
        # Add 5 minute buffer for expiry check
        return datetime.utcnow() + timedelta(minutes=5) >= self.token_expiry


# ============================================================================
# Master Tables for Analysis & Classification (v3.0.0)
# ============================================================================

class Industry(db.Model):
    """Industry/Sector master"""
    __tablename__ = 'industries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(300), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Industry {self.name}>'


class CompanySize(db.Model):
    """Company size range master"""
    __tablename__ = 'company_sizes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(300), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CompanySize {self.name}>'


class CustomerStatus(db.Model):
    """Customer status master (新規/既存/休眠)"""
    __tablename__ = 'customer_statuses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(300), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CustomerStatus {self.name}>'


class LeadSource(db.Model):
    """Lead source master (紹介/Web/広告/展示会/テレアポ/代理店など)"""
    __tablename__ = 'lead_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(300), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LeadSource {self.name}>'


class Stage(db.Model):
    """Deal stage master"""
    __tablename__ = 'stages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(300), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Stage {self.name}>'


class LostReason(db.Model):
    """Lost reason master"""
    __tablename__ = 'lost_reasons'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(300), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LostReason {self.name}>'


class ActivityType(db.Model):
    """Activity type master (電話/メール/オンライン商談/訪問/提案書作成など)"""
    __tablename__ = 'activity_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(300), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ActivityType {self.name}>'
