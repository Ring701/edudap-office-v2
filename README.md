# EduDAP Office v2 - CRM System

**Version 1.0 (Intelligent Price Tracking)**

A comprehensive Customer Relationship Management (CRM) system with smart search, price intelligence, attendance tracking, leave management, expense claims, and task management.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

## 🎨 Color Theme

- **Deep Professional Blue**: `#004085`
- **Scientific Green**: `#4E7D5B`

## ✨ Features

### 1. Registration & Login System
- Automatic role assignment (First user = Admin, rest = Employees)
- Admin promotion feature
- Secure password hashing

### 2. Smart Search & Price Intelligence (Dashboard)
- Deep search indexing across PDFs/Excels
- Extracts: Item Name, CAS No, Cat No, Make/Brand, Specifications, Pricing
- Price Logic: Groups by brand, shows Min/Max prices
- Deduplication: Updates existing records instead of creating duplicates
- Visibility Rules: Employee uploads (public), Admin uploads (private)
- Motivational quote display

### 3. Employee Features
- **Attendance**: GPS-enabled punch in/out with visual indicators (< 9hrs = Red, ≥ 9hrs = Green)
- **Leave**: Request form with date and reason
- **Expenses**: Submit with mandatory bill attachment
- **Assigned Tasks**: View tasks, deadlines, and live chat with admin
- **To-Do List**: Personal tasks with priority levels and alarms

### 4. Admin Features
- **Dashboard**: Access to private and public data search
- **Assign**: Create tasks for employees, set deadlines, manage chat
- **To-Do List**: Personal tasks with alarms
- **Manage Hub**:
  - **Approvals**: Review, Accept, or Reject Leaves and Expenses
  - **Reporting**: Download Monthly Excel data
  - **Location**: View real-time GPS locations of punched-in employees
  - **Promote**: Change Employee role to Admin

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/edudap-office-v2.git
   cd edudap-office-v2
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and set SECRET_KEY
   # Generate: python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access**: `http://localhost:5000`

### Deploy to Render

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

**Quick Deploy:**
1. Push code to GitHub
2. Connect repository to Render
3. Set environment variables
4. Deploy!

## 📁 Project Structure

```
edudap-office-v2/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms definitions
│   ├── extensions.py        # Flask extensions
│   ├── utils.py             # Utility functions (PDF/Excel parsing)
│   ├── auth.py              # Authentication blueprint
│   ├── dashboard.py         # Dashboard blueprint (Search & Upload)
│   ├── employee.py          # Employee blueprint
│   ├── admin.py             # Admin blueprint
│   ├── templates/           # HTML templates
│   └── static/              # Static files
├── uploads/                 # Uploaded files
├── requirements.txt         # Python dependencies
├── Procfile                # Render deployment config
├── runtime.txt             # Python version
├── render.yaml             # Render blueprint config
├── run.py                  # Application entry point
├── wsgi.py                 # WSGI entry point
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///edudap.db  # or PostgreSQL URL for production
FLASK_ENV=development
UPLOAD_FOLDER=uploads
MAX_UPLOAD_SIZE=10485760
```

## 🛠️ Technologies

- **Backend**: Flask 3.0
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **File Parsing**: PyPDF2, pandas, openpyxl
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Deployment**: Gunicorn, Render

## 📊 Database

- **Development**: SQLite (automatic)
- **Production**: PostgreSQL (recommended)

Tables are created automatically on first run.

## 🔒 Security

- ✅ Password hashing with Werkzeug
- ✅ Session management with Flask-Login
- ✅ Role-based access control
- ✅ Input validation with Flask-WTF
- ✅ Environment-based configuration
- ✅ Secure file uploads

## 📝 License

This project is proprietary software for EduDAP India Pvt Ltd.

## 👥 Support

For issues or questions:
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for features
- Create an issue in the repository

---

**Version**: 1.0  
**Last Updated**: January 2026
