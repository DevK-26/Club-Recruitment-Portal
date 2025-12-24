#!/usr/bin/env bash
# Build script for deployment

set -o errexit  # Exit on error

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️  Running database migrations..."
echo "DATABASE_URL is set: $([ -z "$DATABASE_URL" ] && echo "NO" || echo "YES")"

# Ensure FLASK_APP is set
export FLASK_APP=run.py

# Run migrations
python -m flask db upgrade

echo "✅ Migrations completed!"

# Auto-create admin if environment variables are set
if [ ! -z "$ADMIN_EMAIL" ] && [ ! -z "$ADMIN_PASSWORD" ] && [ ! -z "$ADMIN_NAME" ]; then
    echo "👤 Creating admin user from environment variables..."
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

echo "🚀 Build complete!"
