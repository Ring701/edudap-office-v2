from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='employee')  # admin or employee
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attendance = db.relationship('Attendance', backref='user', lazy=True, cascade='all, delete-orphan')
    leaves = db.relationship('Leave', backref='user', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    tasks_assigned = db.relationship('Task', foreign_keys='Task.assigned_to_id', backref='assignee', lazy=True)
    tasks_created = db.relationship('Task', foreign_keys='Task.created_by_id', backref='creator', lazy=True)
    uploaded_quotes = db.relationship('ProductQuote', backref='uploader', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


class ProductQuote(db.Model):
    """Smart Search & Price Intelligence Model"""
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False, index=True)
    cas_no = db.Column(db.String(100), index=True)
    cat_no = db.Column(db.String(100), index=True)
    make_brand = db.Column(db.String(100), nullable=False, index=True)
    base_price = db.Column(db.Float, nullable=False)
    gst_percent = db.Column(db.Float, default=18.0)
    specifications = db.Column(db.Text)
    file_url = db.Column(db.String(300))
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_private = db.Column(db.Boolean, default=False)  # Admin uploads are private
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # For deduplication: unique constraint on key fields
    __table_args__ = (
        db.Index('idx_dedup', 'item_name', 'make_brand', 'cas_no', 'cat_no', 'base_price'),
    )

    @property
    def total_price(self):
        return self.base_price * (1 + self.gst_percent / 100)

    def __repr__(self):
        return f'<ProductQuote {self.item_name} - {self.make_brand}>'


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False, index=True)
    punch_in = db.Column(db.DateTime, nullable=False)
    punch_out = db.Column(db.DateTime, nullable=True)
    location_lat = db.Column(db.String(50), nullable=True)
    location_lon = db.Column(db.String(50), nullable=True)
    location_address = db.Column(db.String(200), nullable=True)

    @property
    def duration(self):
        if self.punch_out and self.punch_in:
            return (self.punch_out - self.punch_in).total_seconds() / 3600
        return 0

    @property
    def status_color(self):
        """Visual Logic: < 9 hours = Red, >= 9 hours = Green"""
        return "green" if self.duration >= 9 else "red"

    def __repr__(self):
        return f'<Attendance {self.user_id} - {self.date}>'


class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending', index=True)  # Pending, Approved, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Leave {self.user_id} - {self.start_date}>'


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    bill_filename = db.Column(db.String(200), nullable=True)  # Mandatory bill attachment
    bill_path = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(20), default='Pending', index=True)  # Pending, Approved, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Expense {self.user_id} - {self.amount}>'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), default='Medium')  # High, Medium, Low
    due_date = db.Column(db.Date, nullable=True)
    task_type = db.Column(db.String(20), default='personal')  # assigned, personal
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_completed = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship for chat messages
    messages = db.relationship('TaskChat', backref='task', lazy=True, cascade='all, delete-orphan', order_by='TaskChat.created_at')

    def __repr__(self):
        return f'<Task {self.title}>'


class TaskChat(db.Model):
    """Live Progress Chat between Admin and Employee"""
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='chat_messages')

    def __repr__(self):
        return f'<TaskChat {self.task_id} - {self.user_id}>'


class ToDoAlarm(db.Model):
    """Alarms for To-Do List items"""
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    alarm_time = db.Column(db.DateTime, nullable=False)
    is_triggered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
