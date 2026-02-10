# Online Exam System (Django)

This project is a web-based **Online Examination System** developed using **Django**.  
It allows teachers to create and manage exams, and students to participate in exams online with automatic and manual grading support.

---

## Features

### Authentication & Users
- Custom User model (Teacher / Student roles)
- User registration with email verification code
- Login & logout system
- Session management
- Role-based access control

---

### Teacher Capabilities
- Create, edit, delete exams
- Define exam properties (title, subject, duration, total score, start/end time)
- Add questions:
  - Multiple-choice questions
  - Descriptive questions
- Define correct answers for test questions
- Publish exams
- View student exam attempts
- Manually grade descriptive answers
- Automatic grading for multiple-choice questions
- Send exam results to students via email

---

### Student Capabilities
- View available exams
- Search exams by **title or subject**
- Participate in exams within allowed time
- Timer-based exam submission
- Submit answers (test & descriptive)
- View submitted exams and final scores

---

### Exam & Grading System
- Automatic scoring for test questions
- Manual grading for descriptive questions
- Final score calculation based on exam total score
- Email notification after grading

---

### Logging
- Application logs
- Request logs
- Error logs  
(All logs are stored in a dedicated `logs/` directory)

---

### Testing
- Unit tests for:
  - User authentication flow
  - Exam creation and participation
  - Auto-grading logic
- Django test framework used

---

## Technologies Used
- Python 3
- Django
- PostgreSQL
- HTML / CSS
- Django Templates
- SMTP (Email)
