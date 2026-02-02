import random
import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone

load_dotenv()

# Global list to avoid immediate OTP collisions (as per user's logic)
prev_otps = []

# OTP In-memory store: {email: {"otp": str, "expires": datetime}}
otp_store = {}

def generate_otp():
    """Generates a 6-digit OTP and avoids collisions with recent ones."""
    otp = random.randint(100000, 999999)
    if otp in prev_otps:
        return generate_otp()
    
    if len(prev_otps) >= 10:
        prev_otps.pop(0)
    
    prev_otps.append(otp)
    return otp

def send_otp_email(target_email: str, otp: int):
    """Sends an OTP email using the provided HTML template."""
    sender_email = "crypsimmails@gmail.com"
    app_password = os.getenv("CRYP_SIM_KEY")
    
    if not app_password:
        print("WARNING: CRYP_SIM_KEY not found in environment variables.")
        return False

    body = f"""
    <!DOCTYPE html>
    <html lang="en">
      <body style="margin: 0; padding: 0; background-color: #171515; font-family: Arial, sans-serif;">
        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="background-color: #171515; padding: 40px 20px;">
          <tr>
            <td align="center">
              <div style="max-width: 400px; margin: 0 auto;">
                <h1 style="color: aliceblue; margin-bottom: 20px;">Cryp<span style="color:aqua">Sim</span></h1>
                <table align="center" cellpadding="0" cellspacing="0" style="background-color: #202626; border-radius: 12px; padding: 30px; width: 100%; border: 1px solid #333;">
                  <tr>
                    <td align="center">
                      <h2 style="color: aliceblue; margin-top: 0; margin-bottom: 10px;">Verify your login</h2>
                      <p style="color: #888; margin-bottom: 25px;">Below is your verification code</p>
                      
                      <table align="center" cellpadding="0" cellspacing="0" style="border: 2px dashed #444; border-radius: 8px; width: 200px; background-color: #171515;">
                        <tr>
                          <td align="center" style="padding: 15px;">
                            <h1 style="color: crimson; font-size: 32px; letter-spacing: 5px; margin: 0;">{otp}</h1>
                          </td>
                        </tr>
                      </table>
                      
                      <p style="color: #666; font-size: 12px; margin-top: 25px;">This code will expire in 5 minutes.</p>
                    </td>
                  </tr>
                </table>
              </div>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Login Verification Code"
    msg["From"] = f"CrypSim <{sender_email}>"
    msg["To"] = target_email
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, target_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def verify_otp_logic(email: str, otp: str):
    """Verifies the OTP against the stored value."""
    if email not in otp_store:
        return False
    
    stored_data = otp_store[email]
    if datetime.now(timezone.utc) > stored_data["expires"]:
        del otp_store[email]
        return False
    
    if stored_data["otp"] == otp:
        # To avoid circular imports, we'll import get_user locally
        from app.login_back.LoginFunctions import get_user
        user = get_user(email=email)
        if user:
            del otp_store[email]
            return user
        
    return False
