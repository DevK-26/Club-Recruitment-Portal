"""Email sending utilities - Using Gmail SMTP

Gmail SMTP is the simplest and most reliable method:
1. Use your Gmail account
2. Enable 2-Factor Authentication on your Google account
3. Generate an App Password: https://myaccount.google.com/apppasswords
4. Set environment variables:
   - MAIL_USERNAME=your-email@gmail.com
   - MAIL_PASSWORD=your-16-char-app-password (no spaces)

That's it! No external service signup required.
"""
from flask import current_app
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def is_email_configured():
    """Check if Gmail SMTP is properly configured"""
    username = current_app.config.get('MAIL_USERNAME')
    password = current_app.config.get('MAIL_PASSWORD')
    return bool(username and password)


def send_email(to_email, subject, html_content, text_content=None):
    """Send email using Gmail SMTP
    
    Returns:
        bool: True always (never blocks workflow)
    """
    if not is_email_configured():
        logger.warning(f"Email not configured. Skipping email to {to_email}")
        return True
    
    try:
        username = current_app.config['MAIL_USERNAME']
        password = current_app.config['MAIL_PASSWORD']
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = to_email if isinstance(to_email, str) else ', '.join(to_email)
        
        if text_content:
            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # Send via Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as server:
            server.starttls()
            server.login(username, password)
            recipients = [to_email] if isinstance(to_email, str) else to_email
            server.sendmail(username, recipients, msg.as_string())
        
        logger.info(f"Email sent to {to_email}")
        return True
        
    except Exception as e:
        logger.warning(f"Email failed to {to_email}: {str(e)}")
        return True  # Never block workflow


def send_credentials_email(user, temp_password):
    """Send login credentials to new candidate"""
    club_name = current_app.config.get('CLUB_NAME', 'Tech Club')
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    login_url = f"{base_url}/auth/login"
    
    subject = f"Your {club_name} Login Credentials"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #0d9488; border-bottom: 2px solid #0d9488; padding-bottom: 10px;">
            Welcome to {club_name}
        </h2>
        
        <p>Hi <strong>{user.name}</strong>,</p>
        
        <p>Your account has been created. Here are your login credentials:</p>
        
        <div style="background: #f0fdfa; border-left: 4px solid #14b8a6; padding: 15px; margin: 20px 0;">
            <p style="margin: 5px 0;"><strong>Email:</strong> {user.email}</p>
            <p style="margin: 5px 0;"><strong>Password:</strong> <code style="background: #fff; padding: 2px 6px;">{temp_password}</code></p>
            <p style="margin: 5px 0;"><strong>Login:</strong> <a href="{login_url}">{login_url}</a></p>
        </div>
        
        <p style="background: #fef3c7; padding: 10px; border-radius: 4px;">
            ⚠️ <strong>Important:</strong> Please change your password after first login.
        </p>
        
        <p style="color: #666; font-size: 14px; margin-top: 30px;">
            Best regards,<br>{club_name} Team
        </p>
    </div>
    """
    
    text = f"""Welcome to {club_name}!

Hi {user.name},

Your login credentials:
- Email: {user.email}
- Password: {temp_password}
- Login URL: {login_url}

Please change your password after first login.

Best regards,
{club_name} Team
"""
    
    return send_email(user.email, subject, html, text)


def send_slot_confirmation_email(user, slot):
    """Send slot booking confirmation"""
    club_name = current_app.config.get('CLUB_NAME', 'Tech Club')
    
    subject = f"Interview Slot Confirmed - {club_name}"
    
    slot_time = slot.start_time.strftime('%B %d, %Y at %I:%M %p')
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #059669;">✓ Interview Slot Confirmed</h2>
        
        <p>Hi <strong>{user.name}</strong>,</p>
        
        <p>Your interview slot has been booked successfully!</p>
        
        <div style="background: #ecfdf5; border: 1px solid #10b981; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin: 0 0 15px 0; color: #065f46;">📅 Interview Details</h3>
            <p style="margin: 5px 0;"><strong>Date & Time:</strong> {slot_time}</p>
            <p style="margin: 5px 0;"><strong>Duration:</strong> {slot.duration} minutes</p>
            {f'<p style="margin: 5px 0;"><strong>Location:</strong> {slot.location}</p>' if slot.location else ''}
        </div>
        
        <p style="color: #666;">Please arrive 5-10 minutes early. Good luck!</p>
        
        <p style="color: #666; font-size: 14px; margin-top: 30px;">
            Best regards,<br>{club_name} Team
        </p>
    </div>
    """
    
    text = f"""Interview Slot Confirmed!

Hi {user.name},

Your interview is scheduled for: {slot_time}
Duration: {slot.duration} minutes
{f'Location: {slot.location}' if slot.location else ''}

Please arrive 5-10 minutes early. Good luck!

{club_name} Team
"""
    
    return send_email(user.email, subject, html, text)


def send_password_reset_email(user, reset_token):
    """Send password reset link"""
    club_name = current_app.config.get('CLUB_NAME', 'Tech Club')
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    reset_url = f"{base_url}/auth/reset-password/{reset_token}"
    
    subject = f"Password Reset - {club_name}"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #0d9488;">Password Reset Request</h2>
        
        <p>Hi <strong>{user.name}</strong>,</p>
        
        <p>We received a request to reset your password. Click the button below:</p>
        
        <p style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background: #14b8a6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                Reset Password
            </a>
        </p>
        
        <p style="color: #666; font-size: 14px;">
            This link expires in 1 hour. If you didn't request this, please ignore this email.
        </p>
        
        <p style="color: #666; font-size: 14px; margin-top: 30px;">
            {club_name} Team
        </p>
    </div>
    """
    
    text = f"""Password Reset Request

Hi {user.name},

Reset your password here: {reset_url}

This link expires in 1 hour.

{club_name} Team
"""
    
    return send_email(user.email, subject, html, text)


def send_announcement_email(announcement, candidates):
    """Send announcement to multiple candidates"""
    club_name = current_app.config.get('CLUB_NAME', 'Tech Club')
    
    subject = f"[{club_name}] {announcement.title}"
    
    success = 0
    failed = 0
    
    for candidate in candidates:
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #0d9488; border-bottom: 2px solid #0d9488; padding-bottom: 10px;">
                📢 {announcement.title}
            </h2>
            
            <p>Hi <strong>{candidate.name}</strong>,</p>
            
            <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                {announcement.content}
            </div>
            
            <p style="color: #666; font-size: 14px;">
                {club_name} Team
            </p>
        </div>
        """
        
        text = f"""{announcement.title}

Hi {candidate.name},

{announcement.content}

{club_name} Team
"""
        
        if send_email(candidate.email, subject, html, text):
            success += 1
        else:
            failed += 1
    
    return success, failed
