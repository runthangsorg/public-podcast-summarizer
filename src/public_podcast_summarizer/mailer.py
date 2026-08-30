"""Email delivery for podcast digest."""
import os
import smtplib
from email.message import EmailMessage
from typing import Any, List, Mapping

def _build_html(items: List[Mapping[str, Any]]) -> str:
    """Build an HTML digest for podcasts."""
    items_html = ""
    for item in items:
        summary_html = ""
        for line in item.get('summary', []):
            summary_html += f"<li>{line}</li>"
            
        items_html += f"""
        <div style="margin-bottom: 25px; padding: 15px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 8px;">
            <h3 style="margin-top: 0; margin-bottom: 10px; font-size: 18px; color: #333;">
                {item.get('title', 'Unknown')}
            </h3>
            <p style="margin: 0 0 10px 0; font-size: 14px; color: #666;">
                Published: {item.get('published', 'Unknown')} | Duration: {item.get('duration_seconds', 0)}s
            </p>
            <ul style="margin: 0; padding-left: 20px; color: #444; font-size: 15px;">
                {summary_html}
            </ul>
        </div>
        """
        
    return f"""
    <html>
    <body style="background-color: #ffffff; color: #333333; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 20px;">
        <div style="max-width: 650px; margin: 0 auto;">
            <h2 style="color: #222; border-bottom: 2px solid #eee; padding-bottom: 10px;">Podcast Digest</h2>
            {items_html if items_html else "<p>No new episodes found.</p>"}
        </div>
    </body>
    </html>
    """

def send_digest(items: List[Mapping[str, Any]], dry_run: bool = False) -> None:
    """Send the HTML digest via SMTP."""
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", 587))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")
    recipient = os.environ.get("REPORT_RECIPIENT")
    
    html_content = _build_html(items)
    
    if dry_run:
        print("--- DRY RUN: Would send email ---")
        print(f"Recipient: {recipient}")
        print(html_content)
        return
        
    if not all([host, port, user, password, recipient]):
        print("Warning: Missing SMTP credentials. Skipping email delivery.")
        return
        
    msg = EmailMessage()
    msg["Subject"] = f"Podcast Digest ({len(items)} episodes)"
    msg["From"] = user
    msg["To"] = recipient
    msg.set_content("Please view this email in an HTML-compatible client.")
    msg.add_alternative(html_content, subtype="html")
    
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
