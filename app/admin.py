"""Admin Blueprint"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
from app.models import User, Task, Attendance, Leave, Expense, TaskChat
from app.extensions import db
from app.forms import TaskForm
from datetime import datetime, date
import csv
import io

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin Dashboard"""
    employees = User.query.filter_by(role='employee').all()
    pending_leaves = Leave.query.filter_by(status='Pending').order_by(Leave.created_at.desc()).all()
    pending_expenses = Expense.query.filter_by(status='Pending').order_by(Expense.created_at.desc()).all()
    
    return render_template('admin/index.html',
                         employees=employees,
                         pending_leaves=pending_leaves,
                         pending_expenses=pending_expenses)


@admin_bp.route('/assign', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_task():
    """Assign tasks to employees"""
    form = TaskForm()
    form.assigned_to_id.choices = [(u.id, u.username) for u in User.query.filter_by(role='employee').all()]
    
    if form.validate_on_submit():
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            task_type='assigned',
            created_by_id=current_user.id,
            assigned_to_id=form.assigned_to_id.data
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Task assigned!', 'success')
        return redirect(url_for('admin.assign_task'))
    
    history = Task.query.filter_by(
        created_by_id=current_user.id,
        task_type='assigned'
    ).order_by(Task.created_at.desc()).all()
    
    return render_template('admin/assign.html', form=form, history=history)


@admin_bp.route('/task/<int:task_id>/chat', methods=['GET', 'POST'])
@login_required
@admin_required
def task_chat(task_id):
    """Chat with employee about task"""
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            chat = TaskChat(
                task_id=task_id,
                user_id=current_user.id,
                message=message
            )
            db.session.add(chat)
            db.session.commit()
            flash('Message sent.', 'success')
            return redirect(url_for('admin.task_chat', task_id=task_id))
    
    messages = TaskChat.query.filter_by(task_id=task_id).order_by(TaskChat.created_at.asc()).all()
    return render_template('admin/task_chat.html', task=task, messages=messages)


@admin_bp.route('/todo', methods=['GET', 'POST'])
@login_required
@admin_required
def todo_list():
    """Admin personal To-Do List"""
    if request.method == 'POST':
        if 'title' in request.form:
            title = request.form.get('title')
            priority = request.form.get('priority', 'Medium')
            due_date_str = request.form.get('due_date')
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
            
            new_task = Task(
                title=title,
                priority=priority,
                due_date=due_date,
                task_type='personal',
                assigned_to_id=current_user.id,
                created_by_id=current_user.id
            )
            db.session.add(new_task)
            db.session.commit()
            flash('Task added!', 'success')
        elif 'complete_task_id' in request.form:
            task_id = int(request.form.get('complete_task_id'))
            task = Task.query.get_or_404(task_id)
            if task.assigned_to_id == current_user.id:
                task.is_completed = True
                db.session.commit()
                flash('Task completed!', 'success')
        return redirect(url_for('admin.todo_list'))
    
    from sqlalchemy import case
    pending = Task.query.filter_by(
        assigned_to_id=current_user.id,
        task_type='personal',
        is_completed=False
    ).order_by(
        case((Task.priority == 'High', 1), (Task.priority == 'Medium', 2), else_=3),
        Task.due_date.asc()
    ).all()
    
    completed = Task.query.filter_by(
        assigned_to_id=current_user.id,
        task_type='personal',
        is_completed=True
    ).order_by(Task.created_at.desc()).limit(10).all()
    
    return render_template('admin/todo.html', pending=pending, completed=completed)


@admin_bp.route('/manage')
@login_required
@admin_required
def manage():
    """Admin Hub - Central management panel"""
    return render_template('admin/manage.html')


@admin_bp.route('/manage/approvals')
@login_required
@admin_required
def approvals():
    """Review, Accept, or Reject Leaves and Expenses"""
    pending_leaves = Leave.query.filter_by(status='Pending').order_by(Leave.created_at.desc()).all()
    pending_expenses = Expense.query.filter_by(status='Pending').order_by(Expense.created_at.desc()).all()
    
    return render_template('admin/approvals.html',
                         pending_leaves=pending_leaves,
                         pending_expenses=pending_expenses)


@admin_bp.route('/approve-leave/<int:id>')
@login_required
@admin_required
def approve_leave(id):
    """Approve leave request"""
    leave = Leave.query.get_or_404(id)
    leave.status = 'Approved'
    db.session.commit()
    flash('Leave Approved', 'success')
    return redirect(url_for('admin.approvals'))


@admin_bp.route('/reject-leave/<int:id>')
@login_required
@admin_required
def reject_leave(id):
    """Reject leave request"""
    leave = Leave.query.get_or_404(id)
    leave.status = 'Rejected'
    db.session.commit()
    flash('Leave Rejected', 'danger')
    return redirect(url_for('admin.approvals'))


@admin_bp.route('/approve-expense/<int:id>')
@login_required
@admin_required
def approve_expense(id):
    """Approve expense claim"""
    expense = Expense.query.get_or_404(id)
    expense.status = 'Approved'
    db.session.commit()
    flash('Expense Approved', 'success')
    return redirect(url_for('admin.approvals'))


@admin_bp.route('/reject-expense/<int:id>')
@login_required
@admin_required
def reject_expense(id):
    """Reject expense claim"""
    expense = Expense.query.get_or_404(id)
    expense.status = 'Rejected'
    db.session.commit()
    flash('Expense Rejected', 'danger')
    return redirect(url_for('admin.approvals'))


@admin_bp.route('/manage/reporting')
@login_required
@admin_required
def reporting():
    """Download Monthly Excel data for business analysis"""
    return render_template('admin/reporting.html')


@admin_bp.route('/download-report')
@login_required
@admin_required
def download_report():
    """Generate and download monthly report as CSV"""
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write Headers
    writer.writerow(['Type', 'User', 'Date', 'Details', 'Status/Amount'])
    
    # Write Attendance
    for a in Attendance.query.filter(
        db.extract('year', Attendance.date) == int(month.split('-')[0]),
        db.extract('month', Attendance.date) == int(month.split('-')[1])
    ).all():
        writer.writerow([
            'Attendance',
            a.user.username,
            a.date,
            f"In: {a.punch_in.strftime('%H:%M')} / Out: {a.punch_out.strftime('%H:%M') if a.punch_out else 'N/A'}",
            f"{a.duration:.2f} hrs"
        ])
    
    # Write Leaves
    for l in Leave.query.filter(
        db.extract('year', Leave.start_date) == int(month.split('-')[0]),
        db.extract('month', Leave.start_date) == int(month.split('-')[1])
    ).all():
        writer.writerow([
            'Leave',
            l.user.username,
            l.start_date,
            f"{l.leave_type}: {l.reason[:50]}",
            l.status
        ])
    
    # Write Expenses
    for e in Expense.query.filter(
        db.extract('year', Expense.date) == int(month.split('-')[0]),
        db.extract('month', Expense.date) == int(month.split('-')[1])
    ).all():
        writer.writerow([
            'Expense',
            e.user.username,
            e.date,
            f"{e.category}: {e.description[:50]}",
            f"INR {e.amount} ({e.status})"
        ])

    output.seek(0)
    
    # Send as file
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'EduDAP_Report_{month}.csv'
    )


@admin_bp.route('/manage/location')
@login_required
@admin_required
def location():
    """View real-time GPS locations of all employees who are currently punched in"""
    # Get all employees currently punched in (today, no punch out)
    active_attendances = Attendance.query.filter(
        Attendance.date == date.today(),
        Attendance.punch_out.is_(None)
    ).all()
    
    locations = []
    for att in active_attendances:
        locations.append({
            'user_id': att.user_id,
            'username': att.user.username,
            'lat': att.location_lat,
            'lon': att.location_lon,
            'address': att.location_address,
            'punch_in_time': att.punch_in.strftime('%H:%M:%S')
        })
    
    return render_template('admin/location.html', locations=locations)


@admin_bp.route('/manage/promote', methods=['GET', 'POST'])
@login_required
@admin_required
def promote():
    """Promote Employee to Admin"""
    employees = User.query.filter_by(role='employee').all()
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user = User.query.get_or_404(user_id)
        if user.role == 'employee':
            user.role = 'admin'
            db.session.commit()
            flash(f'{user.username} has been promoted to Admin!', 'success')
        else:
            flash('User is already an admin.', 'warning')
        return redirect(url_for('admin.promote'))
    
    return render_template('admin/promote.html', employees=employees)
