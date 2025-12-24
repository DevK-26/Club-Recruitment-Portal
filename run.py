#!/usr/bin/env python3
"""Application entry point"""
import os
from app import create_app, db
from app.models import User, Application, InterviewSlot, SlotBooking, Announcement, SystemConfig, AuditLog

# Create application instance
app = create_app(os.getenv('FLASK_ENV') or 'development')


@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Application': Application,
        'InterviewSlot': InterviewSlot,
        'SlotBooking': SlotBooking,
        'Announcement': Announcement,
        'SystemConfig': SystemConfig,
        'AuditLog': AuditLog
    }


@app.cli.command()
def create_admin():
    """Create an admin user via CLI"""
    from app.utils.security import hash_password
    import getpass
    
    email = input("Admin email: ")
    name = input("Admin name: ")
    
    # Check if user exists
    if User.query.filter_by(email=email).first():
        print("User with this email already exists!")
        return
    
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if password != confirm_password:
        print("Passwords do not match!")
        return
    
    admin = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        role='admin',
        first_login=False,
        is_active=True
    )
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"Admin user '{name}' created successfully!")


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized!")


if __name__ == '__main__':
    app.run(debug=True)
