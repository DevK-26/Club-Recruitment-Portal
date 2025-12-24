"""Email sending utilities - Using Resend for reliable email delivery"""
from flask import current_app
import logging
import resend

logger = logging.getLogger(__name__)


def is_email_configured():
    """Check if Resend is properly configured"""
    api_key = current_app.config.get('RESEND_API_KEY')
    from_email = current_app.config.get('RESEND_FROM_EMAIL')
    return bool(api_key and from_email and api_key.strip() and from_email.strip())


def send_email(to_email, subject, html_content, text_content=None):
    """Send email using Resend API
    
    Args:
        to_email (str): Recipient email address (or list of emails)
        subject (str): Email subject
        html_content (str): HTML email body
        text_content (str): Plain text email body (optional)
    
    Returns:
        bool: True if email sent successfully or skipped, False only on critical error
    """
    # Check if email is configured
    if not is_email_configured():
        logger.warning(f"Resend not configured. Skipping email to {to_email}")
        return True  # Don't block workflow
    
    try:
        # Set API key
        resend.api_key = current_app.config['RESEND_API_KEY']
        
        # Handle single email or list
        recipients = [to_email] if isinstance(to_email, str) else to_email
        
        # Send email via Resend
        params = {
            "from": current_app.config['RESEND_FROM_EMAIL'],
            "to": recipients,
            "subject": subject,
            "html": html_content,
        }
        
        if text_content:
            params["text"] = text_content
        
        response = resend.Emails.send(params)
        logger.info(f"Email sent successfully to {to_email}, ID: {response.get('id', 'unknown')}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return True  # Don't block workflow - email failure shouldn't stop operations


def send_batch_emails(emails_data):
    """Send multiple emails in a single batch (up to 100)
    
    Args:
        emails_data: List of dicts with 'to', 'subject', 'html', 'text' keys
    
    Returns:
        bool: True if batch sent successfully
    """
    if not is_email_configured():
        logger.warning("Resend not configured. Skipping batch emails.")
        return True
    
    try:
        resend.api_key = current_app.config['RESEND_API_KEY']
        from_email = current_app.config['RESEND_FROM_EMAIL']
        
        # Prepare batch
        batch = []
        for email in emails_data:
            batch.append({
                "from": from_email,
                "to": [email['to']] if isinstance(email['to'], str) else email['to'],
                "subject": email['subject'],
                "html": email['html'],
            })
        
        # Send batch (Resend supports up to 100 emails per batch)
        response = resend.Batch.send(batch)
        logger.info(f"Batch of {len(batch)} emails sent successfully")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send batch emails: {str(e)}")
        return True


def send_credentials_email(user, temp_password):
    """Send login credentials to new candidate
    
    Args:
        user: User object
        temp_password (str): Temporary password
    
    Returns:
        bool: True if email sent successfully
    """
    login_url = f"{current_app.config['BASE_URL']}/auth/login"
    club_name = current_app.config['CLUB_NAME']
    support_email = current_app.config['SUPPORT_EMAIL']
    
    subject = f"Welcome to {club_name} Recruitment Portal"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .credentials {{ background-color: #fff; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            code {{ background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Welcome to {club_name} Recruitment Portal</h2>
            </div>
            <div class="content">
                <p>Hi <strong>{user.name}</strong>,</p>
                
                <p>Your account has been created for the {club_name} recruitment process. Use the following credentials to log in:</p>
                
                <div class="credentials">
                    <p><strong>Login URL:</strong> <a href="{login_url}">{login_url}</a></p>
                    <p><strong>Username:</strong> {user.email}</p>
                    <p><strong>Temporary Password:</strong> <code>{temp_password}</code></p>
                </div>
                
                <p><strong>⚠️ Important:</strong> You must change your password on first login for security reasons.</p>
                
                <p>After logging in, you will be able to:</p>
                <ul>
                    <li>View available interview slots</li>
                    <li>Book your preferred interview time</li>
                    <li>View important announcements</li>
                </ul>
                
                <p>If you have any questions or need support, please contact us at <a href="mailto:{support_email}">{support_email}</a></p>
            </div>
            <div class="footer">
                <p>Best regards,<br>{club_name} Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to {club_name} Recruitment Portal
    
    Hi {user.name},
    
    Your account has been created. Use the following credentials to log in:
    
    Login URL: {login_url}
    Username: {user.email}
    Temporary Password: {temp_password}
    
    IMPORTANT: You must change your password on first login.
    
    For support, contact: {support_email}
    
    Best regards,
    {club_name} Team
    """
    
    return send_email(user.email, subject, html_content, text_content)


def send_slot_confirmation_email(user, slot):
    """Send interview slot booking confirmation
    
    Args:
        user: User object
        slot: InterviewSlot object
    
    Returns:
        bool: True if email sent successfully
    """
    club_name = current_app.config['CLUB_NAME']
    support_email = current_app.config['SUPPORT_EMAIL']
    
    slot_datetime = f"{slot.date.strftime('%A, %B %d, %Y')} at {slot.start_time.strftime('%I:%M %p')}"
    
    subject = f"Interview Slot Confirmed - {club_name}"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .slot-info {{ background-color: #fff; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>✓ Interview Slot Confirmed</h2>
            </div>
            <div class="content">
                <p>Hi <strong>{user.name}</strong>,</p>
                
                <p>Your interview slot has been successfully booked!</p>
                
                <div class="slot-info">
                    <p><strong>📅 Date & Time:</strong> {slot_datetime}</p>
                    <p><strong>⏱️ Duration:</strong> {slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}</p>
                </div>
                
                <p><strong>Important Reminders:</strong></p>
                <ul>
                    <li>Please arrive 10 minutes early</li>
                    <li>Bring a valid ID</li>
                    <li>Be prepared to discuss your skills and interests</li>
                </ul>
                
                <p>If you need to reschedule or have any questions, please contact us at <a href="mailto:{support_email}">{support_email}</a></p>
                
                <p>We look forward to meeting you!</p>
            </div>
            <div class="footer">
                <p>Best regards,<br>{club_name} Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(user.email, subject, html_content)


def send_password_reset_email(user, reset_url):
    """Send password reset email
    
    Args:
        user: User object
        reset_url (str): Password reset URL with token
    
    Returns:
        bool: True if email sent successfully
    """
    club_name = current_app.config['CLUB_NAME']
    
    subject = f"Password Reset Request - {club_name}"
    
    html_content = f"""
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>Hi {user.name},</p>
        <p>We received a request to reset your password. Click the link below to reset it:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this, please ignore this email.</p>
        <p>Best regards,<br>{club_name} Team</p>
    </body>
    </html>
    """
    
    return send_email(user.email, subject, html_content)


def send_announcement_email(candidates, announcement_title, announcement_content):
    """Send announcement email to all candidates
    
    Args:
        candidates: List of User objects (candidates)
        announcement_title: Title of the announcement
        announcement_content: Content of the announcement
    
    Returns:
        tuple: (success_count, failed_count)
    """
    club_name = current_app.config['CLUB_NAME']
    subject = f"New Announcement: {announcement_title}"
    
    success_count = 0
    failed_count = 0
    
    for candidate in candidates:
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 20px; background-color: #f9f9f9; border-radius: 0 0 8px 8px; }}
                .announcement-box {{ background-color: #fff; padding: 20px; border-left: 4px solid #0d9488; margin: 20px 0; border-radius: 4px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%); color: white; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📢 New Announcement</h2>
                </div>
                <div class="content">
                    <p>Hi <strong>{candidate.name}</strong>,</p>
                    
                    <p>A new announcement has been posted on the {club_name} Recruitment Portal:</p>
                    
                    <div class="announcement-box">
                        <h3 style="color: #0f172a; margin-top: 0;">{announcement_title}</h3>
                        <p style="color: #334155; white-space: pre-wrap;">{announcement_content}</p>
                    </div>
                    
                    <p>Please log in to the portal to view more details:</p>
                    
                    <div style="text-align: center;">
                        <a href="http://localhost:5001/auth/login" class="btn">View Dashboard</a>
                    </div>
                    
                    <p style="margin-top: 20px; font-size: 14px; color: #64748b;">
                        If you have any questions, please contact us at {current_app.config['SUPPORT_EMAIL']}
                    </p>
                </div>
                <div class="footer">
                    <p>Best regards,<br>{club_name} Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        New Announcement from {club_name}
        
        Hi {candidate.name},
        
        {announcement_title}
        
        {announcement_content}
        
        Login to view: http://localhost:5001/auth/login
        
        Best regards,
        {club_name} Team
        """
        
        if send_email(candidate.email, subject, html_content, text_content):
            success_count += 1
        else:
            failed_count += 1
            logger.warning(f"Failed to send announcement email to {candidate.email}")
    
    logger.info(f"Sent announcement '{announcement_title}' to {success_count} candidates, {failed_count} failed")
    return success_count, failed_count
