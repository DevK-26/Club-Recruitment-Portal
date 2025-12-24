# 🚀 Alternative Hosting Options (Free Tier + Shell Access)

Since Render requires premium for shell access, here are your best alternatives.

---

## ⭐ Option 1: Fly.io (RECOMMENDED)

**Best for**: Full control, SSH access, free tier

### Features:
- ✅ **FREE**: $5 credit/month (enough for 1 small app)
- ✅ **SSH Access**: Full terminal access on free tier
- ✅ **PostgreSQL**: Can connect to external Neon
- ✅ **Auto-deploy**: From GitHub
- ✅ **No credit card**: Required but not charged on free tier

### Setup (10 min):

1. **Install Fly CLI**:
   ```bash
   # macOS
   brew install flyctl
   
   # Or
   curl -L https://fly.io/install.sh | sh
   ```

2. **Sign Up**:
   ```bash
   fly auth signup
   # Or login: fly auth login
   ```

3. **Deploy**:
   ```bash
   cd /Users/lakshya/Developement/hiring_sys_club
   
   # Initialize
   fly launch
   # Follow prompts:
   # - App name: hiring-system
   # - Region: closest to you
   # - PostgreSQL: No (using Neon)
   # - Deploy now: No
   ```

4. **Set Environment Variables**:
   ```bash
   fly secrets set FLASK_ENV=production
   fly secrets set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   fly secrets set DATABASE_URL="your-neon-connection-string"
   fly secrets set MAIL_SERVER=smtp.gmail.com
   fly secrets set MAIL_PORT=587
   fly secrets set MAIL_USE_TLS=True
   fly secrets set MAIL_USERNAME=your-email@gmail.com
   fly secrets set MAIL_PASSWORD=your-app-password
   fly secrets set BASE_URL=https://your-app.fly.dev
   fly secrets set CLUB_NAME="Tech Club"
   fly secrets set SUPPORT_EMAIL=support@techclub.com
   ```

5. **Deploy**:
   ```bash
   fly deploy
   ```

6. **Access Shell** (Create Admin):
   ```bash
   fly ssh console
   # Once in:
   cd /app
   flask create-admin
   ```

### Pros:
- ✅ SSH access on free tier
- ✅ Global edge network
- ✅ Easy CLI deployment
- ✅ Great documentation

### Cons:
- ⚠️ Requires credit card (not charged)
- ⚠️ CLI-based (learning curve)

---

## ⭐ Option 2: Railway (ALTERNATIVE)

**Best for**: Simple UI, easy setup

### Features:
- ✅ **FREE**: $5 credit/month
- ✅ **Shell Access**: Available on free tier
- ✅ **GitHub Deploy**: One-click
- ✅ **PostgreSQL**: Built-in or external

### Setup (5 min):

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables (same as above)
6. Deploy

### Access Shell:
1. Project → Service → **"Shell"** tab
2. Run: `flask create-admin`

### Pros:
- ✅ Simple UI
- ✅ Shell access
- ✅ Auto-deploy from GitHub

### Cons:
- ⚠️ $5/month credit (may run out)
- ⚠️ Requires credit card

---

## ⭐ Option 3: PythonAnywhere (EASIEST)

**Best for**: Beginners, always-on, no credit card

### Features:
- ✅ **100% FREE**: No credit card required
- ✅ **Console Access**: Built-in bash console
- ✅ **Always-on**: No cold starts
- ⚠️ **Database**: MySQL included (free) - **Neon requires paid tier ($5/month)**

### Important Note About Neon:
**Free PythonAnywhere tier does NOT support external PostgreSQL connections** (including Neon). 

You have two options:
1. **Use built-in MySQL** (included in free tier) - requires minor code changes
2. **Upgrade to paid tier** ($5/month) - supports external PostgreSQL/Neon

### Setup (15 min):

1. Sign up at https://www.pythonanywhere.com
2. Go to **"Consoles"** → Start bash console
3. Clone your repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
   cd YOUR_REPO
   ```

4. Create virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 myenv
   pip install -r requirements.txt
   ```

5. Set up web app:
   - Go to **"Web"** tab → Add new web app
   - Manual configuration → Python 3.10
   - Configure WSGI file (see below)

6. Set environment variables:
   - **"Web"** tab → Environment variables section
   - Add all your variables

7. **Create Admin** (in console):
   ```bash
   cd YOUR_REPO
   export DATABASE_URL="your-neon-connection-string"
   flask create-admin
   ```

### WSGI Configuration:
Edit `/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`:
```python
import sys
import os

path = '/home/YOUR_USERNAME/YOUR_REPO'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DATABASE_URL'] = 'your-neon-connection-string'
os.environ['SECRET_KEY'] = 'your-secret-key'
os.environ['FLASK_ENV'] = 'production'
# ... other vars

from run import app as application
```

### Pros:
- ✅ No credit card required (free tier)
- ✅ Always-on (no spin down)
- ✅ Console access
- ✅ Very beginner-friendly

### Cons:
- ❌ **Free tier cannot connect to Neon** (external DB blocked)
- ⚠️ Must use MySQL on free tier OR upgrade to paid ($5/month)
- ⚠️ Manual deployment (no auto-deploy)
- ⚠️ Limited CPU time
- ⚠️ More setup steps

---

## 🎯 Option 4: Create Admin Without Shell

**Use Render but create admin differently**

### Method A: Environment Variable Admin

Add this to your `run.py`:

```python
# At the end of run.py, before if __name__ == '__main__':

@app.cli.command()
def create_first_admin():
    """Create admin from environment variables"""
    import os
    from app.utils.security import hash_password
    
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_name = os.getenv('ADMIN_NAME')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    if not all([admin_email, admin_name, admin_password]):
        print("Set ADMIN_EMAIL, ADMIN_NAME, ADMIN_PASSWORD env vars")
        return
    
    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        print(f"Admin {admin_email} already exists")
        return
    
    admin = User(
        email=admin_email,
        name=admin_name,
        password_hash=hash_password(admin_password),
        role='admin',
        first_login=False,
        is_active=True
    )
    
    db.session.add(admin)
    db.session.commit()
    print(f"Admin {admin_name} created!")
```

Update `build.sh`:
```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
flask db upgrade

# Create admin if env vars are set
if [ ! -z "$ADMIN_EMAIL" ]; then
    python -c "from run import app, db; from app.models import User; from app.utils.security import hash_password; import os; app.app_context().push(); existing = User.query.filter_by(email=os.getenv('ADMIN_EMAIL')).first(); admin = User(email=os.getenv('ADMIN_EMAIL'), name=os.getenv('ADMIN_NAME'), password_hash=hash_password(os.getenv('ADMIN_PASSWORD')), role='admin', first_login=False, is_active=True) if not existing else None; db.session.add(admin) if admin else None; db.session.commit() if admin else None; print('Admin created!' if admin else 'Admin exists')"
fi
```

Then in Render, add:
```env
ADMIN_EMAIL=admin@example.com
ADMIN_NAME=Admin User
ADMIN_PASSWORD=SecurePassword123!
```

### Method B: Web-Based Admin Creation

Create a secure setup endpoint (use once, then disable):

Add to `app/auth/routes.py`:
```python
@auth_bp.route('/setup-admin', methods=['GET', 'POST'])
def setup_admin():
    # Check if any admin exists
    if User.query.filter_by(role='admin').first():
        return "Admin already exists", 403
    
    # Check setup key from environment
    setup_key = request.args.get('key')
    if setup_key != current_app.config.get('SETUP_KEY'):
        return "Invalid setup key", 403
    
    if request.method == 'POST':
        # Create admin from form
        # ... form handling
        pass
    
    return render_template('auth/setup_admin.html')
```

---

## 📊 Comparison

| Platform | Free Tier | Shell Access | Neon Support | Credit Card | Ease | Auto-Deploy |
|----------|-----------|--------------|--------------|-------------|------|-------------|
| **Fly.io** | $5 credit | ✅ SSH | ✅ Yes | Required | Medium | ✅ |
| **Railway** | $5 credit | ✅ Shell | ✅ Yes | Required | Easy | ✅ |
| **PythonAnywhere** | Always-on | ✅ Console | ❌ Paid only | ❌ | Easy | ❌ |
| **Render + workaround** | 750h | ❌ | ✅ Yes | ❌ | Easy | ✅ |

---

## 🎯 My Recommendation

### For You: **Fly.io** 🏆

**Why:**
1. ✅ Full SSH access (like having a real server)
2. ✅ Free tier is generous ($5/month credit)
3. ✅ Works with your existing Neon database
4. ✅ Professional infrastructure
5. ✅ Easy to scale later
6. ✅ Auto-deploy from GitHub

**Alternative if no credit card**: 
- **Use Render with environment variable method** (you already have this setup!)
- **Railway** ($5 credit, requires credit card but not charged)
- ~~PythonAnywhere~~ (free tier doesn't support external PostgreSQL)

---

## 🚀 Quick Start (Fly.io)

```bash
# 1. Install
brew install flyctl

# 2. Sign up
fly auth signup

# 3. Initialize (in your project directory)
cd /Users/lakshya/Developement/hiring_sys_club
fly launch --no-deploy

# 4. Set secrets
fly secrets set DATABASE_URL="your-neon-connection"
fly secrets set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
fly secrets set FLASK_ENV=production
# ... other secrets

# 5. Deploy
fly deploy

# 6. Create admin
fly ssh console
flask create-admin

# Done! 🎉
```

---

## 💡 Need Help Choosing?

- **Have credit card + want best option**: Use **Fly.io**
- **No credit card + using Neon**: Use **Render with environment variable method** (you already have this!)
- **No credit card + want shell access**: Switch to MySQL on **PythonAnywhere** (free) or pay $5/month for Neon support
- **Want simplest with Neon**: Use **Render + environment variables** (no changes needed!)

**Important**: If using Neon database, PythonAnywhere free tier won't work. Choose Render or Fly.io instead.
