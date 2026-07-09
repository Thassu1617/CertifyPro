# CertifyPro — AI Certificate Generator & Verification System

An AI-powered certificate generation and verification system built with Flask, SQLite, Machine Learning, and a modern glassmorphism UI.

## Project Structure

```
certificate-system-v2/
├── app.py                    # Flask application factory
├── run.py                    # Entry point to start the server
├── config.py                 # Configuration (DB, secret key, paths)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── database/
│   ├── __init__.py           # SQLAlchemy init & DB initialization
│   ├── models.py             # All database models (User, Student, Course, Marks, Certificate, etc.)
│   └── certificates.db       # SQLite database (auto-created)
│
├── routes/
│   ├── __init__.py
│   ├── main.py               # Landing page & verification routes
│   ├── auth.py               # Login & registration routes
│   ├── admin.py              # Admin dashboard, students, courses
│   └── student.py            # Student dashboard, courses, certificates
│
├── templates/
│   ├── base.html             # Base template (navbar, footer, theme)
│   ├── index.html            # Landing page with hero section
│   ├── verify.html           # Certificate verification page
│   ├── auth/
│   │   ├── login.html        # Login form
│   │   └── register.html     # Registration form
│   ├── admin/
│   │   ├── dashboard.html    # Admin dashboard with stats
│   │   ├── students.html     # Student management
│   │   └── courses.html      # Course management
│   └── student/
│       ├── dashboard.html    # Student dashboard
│       ├── courses.html      # Enrolled courses view
│       └── certificates.html # Certificate history
│
├── static/
│   ├── css/
│   │   └── style.css         # Glassmorphism dark theme CSS
│   ├── js/
│   │   └── main.js           # Animations, counters, interactivity
│   └── certificates/         # Generated PDF certificates
│
├── models/                   # ML model classes (to be implemented)
├── ml/                       # ML training scripts (to be implemented)
└── utils/                    # Utility functions (to be implemented)
```

## Setup Instructions

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate    # Windows
   source venv/bin/activate  # macOS/Linux
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

4. **Open in browser**
   ```
   http://localhost:5000
   ```

5. **Default Admin Credentials**
   ```
   Username: admin
   Password: admin123
   ```

## Features (Roadmap)

- [x] Project structure & Flask setup
- [x] Glassmorphism dark-theme UI
- [x] Responsive navigation & landing page
- [x] SQLite database & models
- [ ] User authentication (register/login/logout)
- [ ] Admin: student & course management
- [ ] Marks & attendance management
- [ ] ML model for pass/fail & grade prediction
- [ ] PDF certificate generation with QR code
- [ ] Certificate verification system
- [ ] Student dashboard with predictions

## Tech Stack

- **Backend**: Python Flask, Flask-SQLAlchemy, Flask-Login
- **Database**: SQLite
- **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript
- **ML**: scikit-learn, pandas, numpy, joblib
- **PDF**: ReportLab, qrcode, Pillow
- **Charts**: Plotly.js
