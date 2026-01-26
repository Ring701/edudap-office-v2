from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, EmailField, DateField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, NumberRange, Length, Optional

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired(), Length(min=2, max=150)])
    email = EmailField('Email ID', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])


class LeaveForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    leave_type = SelectField('Leave Type', choices=[
        ('Sick', 'Sick Leave'),
        ('Casual', 'Casual Leave'),
        ('Earned', 'Earned Leave'),
        ('Personal', 'Personal Leave')
    ], validators=[DataRequired()])
    reason = TextAreaField('Reason', validators=[Optional(), Length(max=500)])


class ExpenseForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    category = SelectField('Type', choices=[
        ('Travel', 'Travel'),
        ('Food', 'Food'),
        ('Office Supplies', 'Office Supplies'),
        ('Accommodation', 'Accommodation'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=200)])
    bill = FileField('Bill Attachment', validators=[FileRequired(), FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'Only PDF and image files allowed!')])


class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    priority = SelectField('Priority', choices=[
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ], validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[Optional()])
    assigned_to_id = SelectField('Assign To', coerce=int, validators=[DataRequired()])


class TaskChatForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=1000)])


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])


class QuoteUploadForm(FlaskForm):
    file = FileField('Upload PDF/Excel', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'xlsx', 'xls'], 'Only PDF and Excel files allowed!')
    ])
