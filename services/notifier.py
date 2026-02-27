import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

def send_summary_email(to_email: str, alerts: list):
    subject = f"🔔 Stock Monitor: {len(alerts)} Alerts Triggered"
    
    rows = ""
    for item in alerts:
        cond_text = "Target Met (>=)" if item['condition'] == 'gte' else "Target Met (<=)"
        color = "#d9534f" if item['condition'] == 'lte' else "#28a745"
        rows += f"""
        <tr>
            <td style="padding:8px; border-bottom:1px solid #ddd;">
                <b>{item['name']}</b><br><small>{item['symbol']}</small>
            </td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{item['current_price']}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd; color:{color};">
                {item['target_price']} <br><small>{cond_text}</small>
            </td>
        </tr>"""

    html = f"""
    <html><body>
        <h3>Daily Stock Report</h3>
        <table style="width:100%; max-width:600px; border-collapse:collapse;">
            <thead><tr style="background:#f8f9fa;">
                <th style="padding:8px; text-align:left;">Stock</th>
                <th style="padding:8px; text-align:left;">Current</th>
                <th style="padding:8px; text-align:left;">Target</th>
            </tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </body></html>
    """
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email failed: {e}")