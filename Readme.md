# Attendance System 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Description:**

The Attendance System is an automated, QR code-based attendance tracking system designed to streamline attendance management in educational institutions. Built with Flask, this system enables both students and staff to manage, track, and verify attendance using real-time QR code generation and scanning.

### Key Features:
- **QR Code-Based Attendance**
  - Dynamic QR code generation for each class session
  - Real-time scanning and verification of attendance
  - Supports file upload and live camera scanning
  
- **Dual User Roles**
  - Staff portal for managing classes and tracking attendance
  - Student portal for marking attendance and viewing records
  - Role-based access control for security
  
- **Comprehensive Attendance Management**
  - Real-time attendance tracking with timestamps
  - Automated entry and exit time recording
  - Detailed attendance reports for staff and students
  - Organized by college and department
  
- **Security Features**
  - Passwords securely hashed with bcrypt
  - Session management for users
  - Secure QR code verification for attendance
  
## 🎯 Features

- **Dynamic QR Code Generation:** Generate QR codes for each class session.
- **Attendance Tracking:** Real-time attendance monitoring and reports.
- **User Role Management:** Secure role-based access for staff and students.
- **Secure Login:** Passwords are hashed using bcrypt for safety.
- **PostgreSQL Database:** All attendance data and user credentials are stored in a PostgreSQL database.

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL
- **Frontend:** HTML5, CSS, JavaScript, Bootstrap
- **Libraries:** 
  - `qrcode` for QR code generation
  - `pyzbar` for QR code decoding
  - `Pillow` for image processing
  - `bcrypt` for password hashing
  - `psycopg2` for PostgreSQL database interaction

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- PostgreSQL Database

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/THILLAINATARAJAN-B/Attendance-System.git
   cd Attendance-System
   ```


2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure PostgreSQL:
   - Create a database named `Attendance`
   - Update the database credentials in the code:
     ```python
     dbhost = 'localhost'
     dbname = 'Attendance'
     dbuser = 'your_username'
     dbpass = 'your_password'
     ```

4. Run the application:
   ```bash
   python app.py
   ```

## 📁 Project Structure

```
Attendance-System/
├── app/
│   ├── static/          # Static files (CSS, JS, images)
│   ├── templates/       # HTML templates
├── requirements.txt     # Required Python packages
└── app.py               # Main application file
```

## 📸 Screenshots

![Attendance System Screenshot - Staff generating QR code for students to scan and register their attendance](images/Screenshot_7.png)

![Attendance System Screenshot - Student registering his attendance via QR code](images/Screenshot_10.png)





## 🤝 Contributing

We welcome contributions! If you’d like to contribute to this project, please fork the repository and create a Pull Request.

### How to contribute:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to your branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team Members

- **Thillainatarajan B**: Backend Python (Flask) Developer, Project Lead.
- **Sivaprakash S**: Database Design and Management
- **Adithiyan C**: UI Developer
- **Rajavarman**: Test and Validations

## 👥 Contact

**Project Lead:** [THILLAINATARAJAN B](https://github.com/THILLAINATARAJAN-B)

**Project Link:** [https://github.com/THILLAINATARAJAN-B/Attendance-System](https://github.com/THILLAINATARAJAN-B/Attendance-System)


## 🙏 Acknowledgments

- Flask Documentation
- PostgreSQL Documentation
- QR Code Libraries Documentation
- Bootstrap Templates
```

### How to use this `.md` file:
1. Copy the content above.
2. Create a new file named `README.md` in your project directory.
3. Paste the content into this file and save.
