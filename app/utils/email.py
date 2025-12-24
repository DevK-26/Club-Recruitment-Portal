"""Email sending utilities - Using Brevo SMTP for reliable email delivery

Brevo (formerly Sendinblue) offers:
- 300 emails/day free, no domain verification required
- Works immediately with any recipient email
- SMTP-based, works on all hosting platforms including Render

Setup:
1. Sign up at https://www.brevo.com (free)
2. Go to SMTP & API → SMTP tab
3. Get your SMTP credentials
4. Set environment variables:
   - BREVO_SMTP_SERVER=smtp-relay.brevo.com
   - BREVO_SMTP_PORT=587
   - BREVO_SMTP_LOGIN=your-login-email
   - BREVO_SMTP_PASSWORD=your-smtp-key
   - MAIL_FROM_EMAIL=your-verified-email@gmail.com
   - MAIL_FROM_NAME=Technical Club
"""
from flask import current_app
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def is_email_configured():
    """Check if Brevo SMTP is properly configured"""
    smtp_login = current_app.config.get('BREVO_SMTP_LOGIN')
    smtp_password = current_app.config.get('BREVO_SMTP_PASSWORD')
    from_email = current_app.config.get('MAIL_FROM_EMAIL')
    return bool(smtp_login and smtp_password and from_email)


def send_email(to_email, subject, html_content, text_content=None):
    """Send email using Brevo SMTP
    
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
        logger.warning(f"Brevo SMTP not configured. Skipping email to {to_email}")
        return True  # Don't block workflow
    
    try:
        # Get SMTP config
        smtp_server = current_app.config.get('BREVO_SMTP_SERVER', 'smtp-relay.brevo.com')
        smtp_port = int(current_app.config.get('BREVO_SMTP_PORT', 587))
        smtp_login = current_app.config['BREVO_SMTP_LOGIN']
        smtp_password = current_app.config['BREVO_SMTP_PASSWORD']
        from_email = current_app.config['MAIL_FROM_EMAIL']
        from_name = current_app.config.get('MAIL_FROM_NAME', current_app.config.get('CLUB_NAME', 'Recruitment Portal'))
        
        # Handle single email or list
        recipients = [to_email] if isinstance(to_email, str) else to_email
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = ', '.join(recipients)
        
        # Add text and HTML parts
        if text_content:
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(part1)
        
        part2 = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part2)
        
        # Send email via SMTP
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_login, smtp_password)
            server.sendmail(from_email, recipients, msg.as_string())
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
    
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {str(e)}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending to {to_email}: {str(e)}")
        return True  # Don't block workflow
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return True  # Don't block workflow


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
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f1f5f9; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 40px; text-align: center;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">Welcome to {club_name}</h1>
                                <p style="color: #94a3b8; margin: 10px 0 0 0; font-size: 16px;">Recruitment Portal</p>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px;">
                                <p style="color: #334155; font-size: 16px; margin: 0 0 20px 0;">Hi <strong>{user.name}</strong>,</p>
                                
                                <p style="color: #475569; font-size: 15px; line-height: 1.6; margin: 0 0 30px 0;">
                                    Your account has been created for the {club_name} recruitment process. Use the following credentials to log in:
                                </p>
                                
                                <!-- Credentials Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%); border-radius: 12px; border-left: 4px solid #14b8a6; margin: 0 0 30px 0;">
                                    <tr>
                                        <td style="padding: 24px;">
                                            <p style="margin: 0 0 12px 0; color: #0f766e; font-size: 14px;">
                                                <strong>Login URL:</strong><br>
                                                <a href="{login_url}" style="color: #0d9488; word-break: break-all;">{login_url}</a>
                                            </p>
                                            <p style="margin: 0 0 12px 0; color: #0f766e; font-size: 14px;">
                                                <strong>Username:</strong><br>
                                                <span style="color: #134e4a;">{user.email}</span>
                                            </p>
                                            <p style="margin: 0; color: #0f766e; font-size: 14px;">
                                                <strong>Temporary Password:</strong><br>
                                                <code style="background-color: #ffffff; padding: 4px 8px; border-radius: 4px; font-family: monospace; color: #0f172a; font-size: 16px;">{temp_password}</code>
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Warning -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fef3c7; border-radius: 8px; margin: 0 0 30px 0;">
                                    <tr>
                                        <td style="padding: 16px;">
                                            <p style="margin: 0; color: #92400e; font-size: 14px;">
                                                ⚠️ <strong>Important:</strong> You must change your password on first login for security reasons.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #475569; font-size: 15px; margin: 0 0 15px 0;">After logging in, you will be able to:</p>
                                <ul style="color: #64748b; font-size: 14px; line-height: 1.8; margin: 0 0 30px 0; padding-left: 20px;">
                                    <li>View available interview slots</li>
                                    <li>Book your preferred interview time</li>
                                    <li>View important announcements</li>
                                </ul>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center">
                                            <a href="{login_url}" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px;">Login to Portal</a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8fafc; padding: 24px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="margin: 0 0 8px 0; color: #64748b; font-size: 13px;">
                                    Need help? Contact us at <a href="mailto:{support_email}" style="color: #0d9488;">{support_email}</a>
                                </p>
                                <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                                    © 2025 {club_name}. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
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

After logging in, you can:
- View available interview slots
- Book your preferred interview time
- View important announcements

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
    base_url = current_app.config['BASE_URL']
    
    slot_date = slot.date.strftime('%A, %B %d, %Y')
    slot_time = f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}"
    
    subject = f"Interview Slot Confirmed - {club_name}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f1f5f9; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #059669 0%, #047857 100%); padding: 40px; text-align: center;">
                                <div style="font-size: 48px; margin-bottom: 10px;">✅</div>
                                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600;">Interview Slot Confirmed</h1>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px;">
                                <p style="color: #334155; font-size: 16px; margin: 0 0 20px 0;">Hi <strong>{user.name}</strong>,</p>
                                
                                <p style="color: #475569; font-size: 15px; line-height: 1.6; margin: 0 0 30px 0;">
                                    Great news! Your interview slot has been successfully booked. Here are the details:
                                </p>
                                
                                <!-- Slot Info -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border-radius: 12px; border-left: 4px solid #10b981; margin: 0 0 30px 0;">
                                    <tr>
                                        <td style="padding: 24px;">
                                            <p style="margin: 0 0 16px 0; color: #065f46; font-size: 15px;">
                                                📅 <strong>Date:</strong> {slot_date}
                                            </p>
                                            <p style="margin: 0; color: #065f46; font-size: 15px;">
                                                ⏰ <strong>Time:</strong> {slot_time}
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #475569; font-size: 15px; margin: 0 0 15px 0;"><strong>Important Reminders:</strong></p>
                                <ul style="color: #64748b; font-size: 14px; line-height: 1.8; margin: 0 0 30px 0; padding-left: 20px;">
                                    <li>Please arrive 10 minutes early</li>
                                    <li>Bring a valid ID</li>
                                    <li>Be prepared to discuss your skills and interests</li>
                                </ul>
                                
                                <!-- CTA -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center">
                                            <a href="{base_url}/candidate/slots" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px;">View My Booking</a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8fafc; padding: 24px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="margin: 0 0 8px 0; color: #64748b; font-size: 13px;">
                                    Need to reschedule? Contact <a href="mailto:{support_email}" style="color: #0d9488;">{support_email}</a>
                                </p>
                                <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                                    © 2025 {club_name}. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    text_content = f"""
Interview Slot Confirmed - {club_name}

Hi {user.name},

Your interview slot has been booked!

Date: {slot_date}
Time: {slot_time}

Important Reminders:
- Please arrive 10 minutes early
- Bring a valid ID
- Be prepared to discuss your skills and interests

Need to reschedule? Contact: {support_email}

Best regards,
{club_name} Team
    """
    
    return send_email(user.email, subject, html_content, text_content)


def send_password_reset_email(user, reset_url):
    """Send password reset email
    
    Args:
        user: User object
        reset_url (str): Password reset URL with token
    
    Returns:
        bool: True if email sent successfully
    """
    club_name = current_app.config['CLUB_NAME']
    support_email = current_app.config['SUPPORT_EMAIL']
    
    subject = f"Password Reset Request - {club_name}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f1f5f9; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 40px; text-align: center;">
                                <div style="font-size: 48px; margin-bottom: 10px;">🔐</div>
                                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600;">Password Reset</h1>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px;">
                                <p style="color: #334155; font-size: 16px; margin: 0 0 20px 0;">Hi <strong>{user.name}</strong>,</p>
                                
                                <p style="color: #475569; font-size: 15px; line-height: 1.6; margin: 0 0 30px 0;">
                                    We received a request to reset your password. Click the button below to create a new password:
                                </p>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 30px 0;">
                                    <tr>
                                        <td align="center">
                                            <a href="{reset_url}" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px;">Reset Password</a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #64748b; font-size: 13px; line-height: 1.6; margin: 0 0 20px 0;">
                                    Or copy and paste this link in your browser:<br>
                                    <a href="{reset_url}" style="color: #0d9488; word-break: break-all;">{reset_url}</a>
                                </p>
                                
                                <!-- Warning -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fef3c7; border-radius: 8px;">
                                    <tr>
                                        <td style="padding: 16px;">
                                            <p style="margin: 0; color: #92400e; font-size: 14px;">
                                                ⏰ This link will expire in <strong>1 hour</strong>.<br>
                                                🔒 If you didn't request this, please ignore this email.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8fafc; padding: 24px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="margin: 0 0 8px 0; color: #64748b; font-size: 13px;">
                                    Need help? Contact <a href="mailto:{support_email}" style="color: #0d9488;">{support_email}</a>
                                </p>
                                <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                                    © 2025 {club_name}. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    text_content = f"""
Password Reset Request - {club_name}

Hi {user.name},

We received a request to reset your password.

Click here to reset: {reset_url}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
{club_name} Team
    """
    
    return send_email(user.email, subject, html_content, text_content)


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
    support_email = current_app.config['SUPPORT_EMAIL']
    base_url = current_app.config['BASE_URL']
    
    subject = f"New Announcement: {announcement_title} - {club_name}"
    
    success_count = 0
    failed_count = 0
    
    for candidate in candidates:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f1f5f9; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 40px; text-align: center;">
                                    <div style="font-size: 48px; margin-bottom: 10px;">📢</div>
                                    <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600;">New Announcement</h1>
                                </td>
                            </tr>
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px;">
                                    <p style="color: #334155; font-size: 16px; margin: 0 0 20px 0;">Hi <strong>{candidate.name}</strong>,</p>
                                    
                                    <p style="color: #475569; font-size: 15px; line-height: 1.6; margin: 0 0 30px 0;">
                                        A new announcement has been posted on the {club_name} Recruitment Portal:
                                    </p>
                                    
                                    <!-- Announcement Box -->
                                    <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%); border-radius: 12px; border-left: 4px solid #14b8a6; margin: 0 0 30px 0;">
                                        <tr>
                                            <td style="padding: 24px;">
                                                <h3 style="margin: 0 0 15px 0; color: #0f172a; font-size: 18px;">{announcement_title}</h3>
                                                <p style="margin: 0; color: #334155; font-size: 14px; line-height: 1.7; white-space: pre-wrap;">{announcement_content}</p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- CTA -->
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td align="center">
                                                <a href="{base_url}/auth/login" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px;">View Dashboard</a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #f8fafc; padding: 24px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                                    <p style="margin: 0 0 8px 0; color: #64748b; font-size: 13px;">
                                        Questions? Contact <a href="mailto:{support_email}" style="color: #0d9488;">{support_email}</a>
                                    </p>
                                    <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                                        © 2025 {club_name}. All rights reserved.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        text_content = f"""
New Announcement from {club_name}

Hi {candidate.name},

{announcement_title}

{announcement_content}

Login to view: {base_url}/auth/login

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
