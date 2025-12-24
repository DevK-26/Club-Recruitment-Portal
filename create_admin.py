"""Create admin user from environment variables"""
import os
import sys

# Ensure FLASK_APP is set
os.environ.setdefault('FLASK_APP', 'run.py')

from app import create_app, db
from app.models import User

def create_admin():
    print("=" * 60)
    print("ADMIN USER CREATION SCRIPT")
    print("=" * 60)
    
    try:
        app = create_app()
        print("✓ Flask app created")
    except Exception as e:
        print(f"✗ Failed to create Flask app: {str(e)}")
        sys.exit(1)
    
    with app.app_context():
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_name = os.environ.get('ADMIN_NAME')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        print(f"Environment variables:")
        print(f"  ADMIN_EMAIL: {'✓ Set' if admin_email else '✗ Not set'}")
        print(f"  ADMIN_NAME: {'✓ Set' if admin_name else '✗ Not set'}")
        print(f"  ADMIN_PASSWORD: {'✓ Set' if admin_password else '✗ Not set'}")
        
        if not all([admin_email, admin_name, admin_password]):
            print("\n⚠️  ERROR: Admin credentials not set in environment variables")
            print("Please set ADMIN_EMAIL, ADMIN_NAME, and ADMIN_PASSWORD in Render dashboard")
            print("=" * 60)
            sys.exit(1)
        
        # Check if admin already exists
        try:
            existing_admin = User.query.filter_by(email=admin_email).first()
            if existing_admin:
                print(f"\n✓ Admin user already exists: {admin_email}")
                print(f"  Role: {existing_admin.role}")
                print(f"  Active: {existing_admin.is_active}")
                print("=" * 60)
                return
        except Exception as e:
            print(f"\n✗ Error checking existing admin: {str(e)}")
            print("=" * 60)
            sys.exit(1)
        
        # Create new admin
        print(f"\nCreating admin user: {admin_email}")
        try:
            admin = User(
                name=admin_name,
                email=admin_email,
                role='admin',
                is_active=True,
                first_login=False
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Admin user created successfully!")
            print(f"  Email: {admin_email}")
            print(f"  Name: {admin_name}")
            print(f"  Role: admin")
            print("=" * 60)
        except Exception as e:
            print(f"✗ Error creating admin user: {str(e)}")
            print("=" * 60)
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    try:
        create_admin()
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {str(e)}")
        print("=" * 60)
        sys.exit(1)
