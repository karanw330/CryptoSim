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
    sender_email = "simstock206@gmail.com"
    app_password = os.getenv("CRYPTO_SIM_KEY")
    
    if not app_password:
        print("WARNING: CRYPTO_SIM_KEY not found in environment variables.")
        return False

    body = f"""
    <!DOCTYPE html>
    <html lang="en">
      <body style="margin: 0; padding: 0; background-color: #171515;">
        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="background-color: #171515; padding: 20px;">
          <tr>
            <td align="center">
            <h1 style="color: aliceblue; font-family: Arial, sans-serif">Trade<span style="color:aqua">Snap</span></h1>
              <h2 style="color: aliceblue; font-family: Arial, sans-serif;">Verify your login</h2>
              <table cellpadding="0" cellspacing="0" style="background-color: #202626; border-radius: 10px; padding: 10px; width: 300px;">
                <tr>
                  <td>
                    <p style="color: grey; font-family: Arial, sans-serif;">Below is your verification code</p>
                    <table cellpadding="10" cellspacing="0" width="100%" style="border: 1px dashed grey; border-radius: 5px; text-align: center;">
                      <tr>
                        <td>
                          <h1 style="color: crimson; font-family: Arial, sans-serif; margin: 0;">{otp}</h1>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Login Verification Code"
    msg["From"] = f"TradeSnap <{sender_email}>"
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