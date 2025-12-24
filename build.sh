#!/usr/bin/env bash
# Build script for deployment

set -o errexit  # Exit on error

# Install dependencies
pip install -r requirements.txt

# Run database migrations
flask db upgrade

# Auto-create admin if environment variables are set
if [ ! -z "$ADMIN_EMAIL" ] && [ ! -z "$ADMIN_PASSWORD" ] && [ ! -z "$ADMIN_NAME" ]; then
    echo "Creating admin user from environment variables..."
    python -c "
from app import create_app, db
from app.models import User
from app.utils.security import hash_password
import os

app = create_app('production')
with app.app_context():
    admin_email = os.getenv('ADMIN_EMAIL')
    existing = User.query.filter_by(email=admin_email).first()
    
    if not existing:
        admin = User(
            email=admin_email,
            name=os.getenv('ADMIN_NAME'),
            password_hash=hash_password(os.getenv('ADMIN_PASSWORD')),
            role='admin',
            first_login=False,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f'✅ Admin user {admin_email} created successfully!')
    else:
        print(f'ℹ️  Admin user {admin_email} already exists.')
"
else
    echo "ℹ️  Skipping admin creation (set ADMIN_EMAIL, ADMIN_NAME, ADMIN_PASSWORD to auto-create)"
fi
