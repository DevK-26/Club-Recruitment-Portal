"""Create admin user from environment variables"""
import os
from app import create_app, db
from app.models import User

def create_admin():
    app = create_app()
    with app.app_context():
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_name = os.environ.get('ADMIN_NAME')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        if not all([admin_email, admin_name, admin_password]):
            print("⚠️  Admin credentials not set in environment variables")
            print("Set ADMIN_EMAIL, ADMIN_NAME, and ADMIN_PASSWORD")
            return
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email=admin_email).first()
        if existing_admin:
            print(f"✓ Admin user already exists: {admin_email}")
            return
        
        # Create new admin
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
            print(f"✓ Admin user created successfully: {admin_email}")
        except Exception as e:
            print(f"✗ Error creating admin user: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    create_admin()
