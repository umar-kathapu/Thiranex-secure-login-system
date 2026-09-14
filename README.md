# Thiranex-secure-login-system
Secure Login System with bcrypt authentication and TOTP 2FA
# 🔐 Secure Login System

A secure web-based authentication system developed as part of my **Thiranex Cyber Security Internship**.

This project demonstrates secure user registration, password hashing, authentication, session management, protected routes, SQL injection protection, and optional **Two-Factor Authentication (2FA)** using TOTP.

## 🚀 Features

- 👤 User Registration
- 🔐 Secure Password Hashing using bcrypt
- 🔑 User Login Authentication
- 🛡️ Protected Dashboard
- 🔒 Session Management
- 🚪 Secure Logout
- 🔢 TOTP-based Two-Factor Authentication (2FA)
- 📱 Authenticator App Support
- 🛡️ Basic SQL Injection Protection
- ✅ Input Validation
- 🗄️ SQLite Database
- 🎨 Responsive Web Interface
- ⚠️ Error and Success Messages

## 🛠️ Technologies Used

- **Python**
- **Flask**
- **Flask-SQLAlchemy**
- **Flask-Bcrypt**
- **PyOTP**
- **SQLite**
- **HTML5**
- **CSS3**
- **Git & GitHub**

## 📁 Project Structure

```text
Thiranex-secure-login-system/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── setup_2fa.html
│   └── verify_2fa.html
│
└── static/
    └── style.css
