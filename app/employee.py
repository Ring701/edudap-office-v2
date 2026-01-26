"""Employee Blueprint"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Attendance, Leave, Expense, Task, TaskChat, ToDoAlarm
from app.forms import LeaveForm, ExpenseForm, TaskChatForm
from datetime import datetime, date
import os
from werkzeug.utils import secure_filename

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

@employee_bp.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    """Attendance with mandatory GPS capture"""
    today_record = Attendance.query.filter_by(user_id=current_user.id, date=date.today()).first()
    is_punched_in = today_record is not None and today_record.punch_out is None
    history = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.date.desc()).limit(30).all()

    if request.method == 'POST':
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        address = request.form.get('address', '')

        # Mandatory GPS Capture
        if not lat or not lon:
            flash('Error: Location Services Required to Punch. Please enable GPS.', 'danger')
            return redirect(url_for('employee.attendance'))

        if is_punched_in:
            # Punch Out
            today_record.punch_out = datetime.now()
            db.session.commit()
            flash('Punched OUT successfully.', 'warning')
        else:
            # Punch In
            new_punch = Attendance(
                user_id=current_user.id,
                punch_in=datetime.now(),
                location_lat=lat,
                location_lon=lon,
                location_address=address
            )
            db.session.add(new_punch)
            db.session.commit()
            flash('Punched IN successfully.', 'success')
        
        return redirect(url_for('employee.attendance'))

    return render_template('attendance.html', is_punched_in=is_punched_in, history=history, today_record=today_record)


@employee_bp.route('/leave', methods=['GET', 'POST'])
@login_required
def leave():
    """Leave request form"""
    form = LeaveForm()
    
    if form.validate_on_submit():
        start = form.start_date.data
        end = form.end_date.data
        l_type = form.leave_type.data
        reason = form.reason.data

        if end < start:
            flash('End date must be after start date.', 'danger')
            return redirect(url_for('employee.leave'))

        new_leave = Leave(
            user_id=current_user.id,
            start_date=start,
            end_date=end,
            leave_type=l_type,
            reason=reason
        )
        db.session.add(new_leave)
        db.session.commit()
        flash('Leave request submitted.', 'info')
        return redirect(url_for('employee.leave'))

    history = Leave.query.filter_by(user_id=current_user.id).order_by(Leave.start_date.desc()).all()
    return render_template('leave.html', form=form, history=history)


@employee_bp.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    """Expenses with mandatory bill attachment"""
    form = ExpenseForm()
    
    if form.validate_on_submit():
        amount = form.amount.data
        category = form.category.data
        desc = form.description.data
        bill_file = form.bill.data
        
        # Save bill file
        if bill_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = secure_filename(f"{timestamp}_{bill_file.filename}")
            upload_folder = os.path.join('uploads', 'bills')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            bill_file.save(file_path)
            
            new_expense = Expense(
                user_id=current_user.id,
                amount=amount,
                category=category,
                description=desc,
                bill_filename=filename,
                bill_path=file_path
            )
            db.session.add(new_expense)
            db.session.commit()
            flash('Expense claim added with bill attachment.', 'success')
        else:
            flash('Bill attachment is mandatory.', 'danger')
        
        return redirect(url_for('employee.expenses'))

    history = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    return render_template('expenses.html', form=form, history=history)


@employee_bp.route('/assigned')
@login_required
def assigned():
    """View assigned tasks with deadlines and live chat"""
    tasks = Task.query.filter_by(
        assigned_to_id=current_user.id,
        task_type='assigned'
    ).order_by(Task.due_date.asc(), Task.created_at.desc()).all()
    
    return render_template('assigned_tasks.html', tasks=tasks)


@employee_bp.route('/task/<int:task_id>/chat', methods=['GET', 'POST'])
@login_required
def task_chat(task_id):
    """Live progress chat with admin"""
    task = Task.query.get_or_404(task_id)
    
    # Verify user has access to this task
    if task.assigned_to_id != current_user.id and task.created_by_id != current_user.id:
        if not current_user.is_admin:
            flash('Access denied.', 'danger')
            return redirect(url_for('employee.assigned'))
    
    form = TaskChatForm()
    
    if form.validate_on_submit():
        message = form.message.data
        chat = TaskChat(
            task_id=task_id,
            user_id=current_user.id,
            message=message
        )
        db.session.add(chat)
        db.session.commit()
        flash('Message sent.', 'success')
        return redirect(url_for('employee.task_chat', task_id=task_id))
    
    messages = TaskChat.query.filter_by(task_id=task_id).order_by(TaskChat.created_at.asc()).all()
    return render_template('task_chat.html', task=task, messages=messages, form=form)


@employee_bp.route('/todo', methods=['GET', 'POST'])
@login_required
def todo():
    """Personal To-Do List with Priority and Alarms"""
    if request.method == 'POST':
        if 'title' in request.form:
            # Create new task
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
            
            # Create alarm if alarm time provided
            alarm_time_str = request.form.get('alarm_time')
            if alarm_time_str:
                try:
                    alarm_time = datetime.strptime(alarm_time_str, '%Y-%m-%dT%H:%M')
                    alarm = ToDoAlarm(
                        task_id=new_task.id,
                        alarm_time=alarm_time
                    )
                    db.session.add(alarm)
                    db.session.commit()
                except:
                    pass
            
            flash('Task added!', 'success')
            
        elif 'complete_task_id' in request.form:
            # Complete task
            task_id = int(request.form.get('complete_task_id'))
            task = Task.query.get_or_404(task_id)
            if task.assigned_to_id == current_user.id:
                task.is_completed = True
                db.session.commit()
                flash('Task marked as completed!', 'success')
        
        return redirect(url_for('employee.todo'))
    
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
    
    return render_template('todo.html', pending=pending, completed=completed)
