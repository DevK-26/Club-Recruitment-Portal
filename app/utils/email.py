"""Email sending utilities - Using Resend API with beautiful professional templates

Resend Setup:
1. Sign up at https://resend.com (free: 100 emails/day, 3000/month)
2. Get API Key from dashboard
3. For production: Verify your Gmail in Resend → Settings → Verified Emails
   (They send a verification email, click the link)
4. Set environment variables:
   - RESEND_API_KEY=re_xxxxxxxxxxxx
   - RESEND_FROM_EMAIL=your-email@gmail.com (must be verified)
"""
from flask import current_app
import logging
import resend

logger = logging.getLogger(__name__)


def is_email_configured():
    """Check if Resend is properly configured"""
    api_key = current_app.config.get('RESEND_API_KEY')
    from_email = current_app.config.get('RESEND_FROM_EMAIL')
    return bool(api_key and from_email)


def send_email(to_email, subject, html_content):
    """Send email using Resend API
    
    Returns:
        bool: True always (never blocks workflow)
    """
    if not is_email_configured():
        logger.warning(f"Resend not configured. Skipping email to {to_email}")
        return True
    
    try:
        resend.api_key = current_app.config['RESEND_API_KEY']
        from_email = current_app.config['RESEND_FROM_EMAIL']
        from_name = current_app.config.get('CLUB_NAME', 'Tech Club')
        
        params = {
            "from": f"{from_name} <{from_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        
        email = resend.Emails.send(params)
        logger.info(f"Email sent to {to_email} (ID: {email.get('id', 'unknown')})")
        return True
        
    except Exception as e:
        logger.warning(f"Email failed to {to_email}: {str(e)}")
        return True  # Never block workflow


def send_credentials_email(user, temp_password):
    """Send login credentials with beautiful professional design"""
    club_name = current_app.config.get('CLUB_NAME', 'Tech Club')
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    support_email = current_app.config.get('SUPPORT_EMAIL', 'support@techclub.com')
    login_url = f"{base_url}/auth/login"
    
    subject = f"Welcome to {club_name} Recruitment Portal"
    
    html = f"""
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
    
    return send_email(user.email, subject, html)


def send_slot_confirmation_email(user, slot):
    """Send slot booking confirmation with professional design"""
    club_name = current_app.config.get('CLUB_NAME', 'Tech Club')
    support_email = current_app.config.get('SUPPORT_EMAIL', 'support@techclub.com')
    
    subject = f"Interview Slot Confirmed - {club_name}"
    
    slot_time = slot.start_time.strftime('%B %d, %Y at %I:%M %p')
    
    html = f"""
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
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">✓ Interview Confirmed</h1>
                                <p style="color: #d1fae5; margin: 10px 0 0 0; font-size: 16px;">Your slot has been booked</p>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px;">
                                <p style="color: #334155; font-size: 16px; margin: 0 0 20px 0;">Hi <strong>{user.name}</strong>,</p>
                                
                                <p style="color: #475569; font-size: 15px; line-height: 1.6; margin: 0 0 30px 0;">
                                    Your interview slot has been successfully confirmed!
                                </p>
                                
                                <!-- Interview Details Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border-radius: 12px; border-left: 4px solid #10b981; margin: 0 0 30px 0;">
                                    <tr>
                                        <td style="padding: 24px;">
                                            <h3 style="margin: 0 0 15px 0; color: #065f46; font-size: 18px;">📅 Interview Details</h3>
                                            <p style="margin: 0 0 12px 0; color: #047857; font-size: 14px;">
                                                <strong>Date & Time:</strong><br>
                                                <span style="color: #065f46; font-size: 16px;">{slot_time}</span>
                                            </p>
                                            <p style="margin: 0 0 12px 0; color: #047857; font-size: 14px;">
                                                <strong>Duration:</strong><br>
                                                <span style="color: #065f46;">{slot.duration} minutes</span>
                                            </p>
                                            {f'<p style="margin: 0; color: #047857; font-size: 14px;"><strong>Location:</strong><br><span style="color: #065f46;">{slot.location}</span></p>' if slot.location else ''}
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Tips Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #eff6ff; border-radius: 8px; margin: 0 0 30px 0;">
                                    <tr>
                                        <td style="padding: 16px;">
                                            <p style="margin: 0; color: #1e40af; font-size: 14px;">
                                                💡 <strong>Tip:</strong> Please arrive 5-10 minutes early. Good luck!
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #64748b; font-size: 14px; margin: 0;">
                                    We look forward to meeting you!
                                </p>
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
    
    return send_email(user.email, subject, html)


def send_password_reset_email(user, reset_token):
    """Send password reset link with professional design"""
    club_name = current_app.config.get('CLUB_NAME', 'Tech Club')
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    support_email = current_app.config.get('SUPPORT_EMAIL', 'support@techclub.com')
    reset_url = f"{base_url}/auth/reset-password/{reset_token}"
    
    subject = f"Password Reset Request - {club_name}"
    
    html = f"""
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
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">Password Reset</h1>
                                <p style="color: #94a3b8; margin: 10px 0 0 0; font-size: 16px;">{club_name}</p>
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
                                
                                <!-- Info Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fef3c7; border-radius: 8px; margin: 0 0 30px 0;">
                                    <tr>
                                        <td style="padding: 16px;">
                                            <p style="margin: 0; color: #92400e; font-size: 14px;">
                                                ⏰ This link will expire in 1 hour for security reasons.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #64748b; font-size: 14px; margin: 0 0 10px 0;">
                                    If you didn't request a password reset, please ignore this email or contact support if you have concerns.
                                </p>
                                
                                <p style="color: #94a3b8; font-size: 13px; margin: 0;">
                                    Or copy and paste this URL into your browser:<br>
                                    <a href="{reset_url}" style="color: #0d9488; word-break: break-all;">{reset_url}</a>
                                </p>
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
    
    return send_email(user.email, subject, html)


def send_announcement_email(announcement, candidates):
    """Send announcement to multiple candidates with professional design"""
    club_name = current_app.config.get('CLUB_NAME', 'Tech Club')
    support_email = current_app.config.get('SUPPORT_EMAIL', 'support@techclub.com')
    
    subject = f"[{club_name}] {announcement.title}"
    
    success = 0
    failed = 0
    
    for candidate in candidates:
        html = f"""
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
                                    <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600;">📢 {announcement.title}</h1>
                                    <p style="color: #94a3b8; margin: 10px 0 0 0; font-size: 16px;">{club_name}</p>
                                </td>
                            </tr>
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px;">
                                    <p style="color: #334155; font-size: 16px; margin: 0 0 20px 0;">Hi <strong>{candidate.name}</strong>,</p>
                                    
                                    <!-- Announcement Box -->
                                    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f8fafc; border-radius: 12px; border-left: 4px solid #14b8a6; margin: 0 0 30px 0;">
                                        <tr>
                                            <td style="padding: 24px;">
                                                <div style="color: #334155; font-size: 15px; line-height: 1.6;">
                                                    {announcement.content}
                                                </div>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="color: #64748b; font-size: 14px; margin: 0;">
                                        Stay tuned for more updates!
                                    </p>
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
        
        if send_email(candidate.email, subject, html):
            success += 1
        else:
            failed += 1
    
    return success, failed
