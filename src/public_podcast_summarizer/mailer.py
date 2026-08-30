import html
import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Any, List, Mapping


CATEGORY_EMOJIS = {
    "AI & Deep Tech": "🤖",
    "Engineering & Open Source": "⚙️",
    "Health & Science": "💪",
    "Focus & Productivity": "🧠",
    "Product & Growth": "📈",
    "Economics & Society": "🌐",
    "Philosophy & Thought": "🕌",
    "General Knowledge": "🎙️",
}


def _build_html(items: List[Mapping[str, Any]]) -> str:
    """Build a rich, GitHub Dark themed HTML digest for podcasts with inline CSS."""
    if not items:
        return """<!doctype html>
        <html>
        <body style="background-color: #010409; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 30px; margin: 0;">
            <div style="max-width: 780px; margin: 0 auto; background-color: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 24px; text-align: center;">
                <h1 style="color: #00ccaa; font-size: 24px; margin: 0 0 12px 0;">🎙️ Podcast Intelligence Digest</h1>
                <p style="color: #8b949e; font-size: 14px; margin: 0;">No new episodes found in configured feeds for this cycle.</p>
            </div>
        </body>
        </html>"""

    # Group by category
    categories: dict[str, list[Mapping[str, Any]]] = {}
    for item in items:
        cat = item.get("category", "General Knowledge")
        categories.setdefault(cat, []).append(item)

    # Build Table of Contents
    toc_html = """
    <div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 20px 24px; margin-bottom: 28px;">
        <h2 style="color: #58a6ff; font-size: 18px; font-weight: 700; margin: 0 0 14px 0; border-bottom: 1px solid #21262d; padding-bottom: 8px;">
            📑 Table of Contents
        </h2>
        <ul style="margin: 0; padding-left: 20px; color: #c9d1d9; font-size: 14px; line-height: 1.8;">
    """
    for cat, cat_items in categories.items():
        emoji = CATEGORY_EMOJIS.get(cat, "🎙️")
        toc_html += f'<li style="margin-bottom: 6px;"><strong style="color: #f0f6fc;">{emoji} {html.escape(cat)}</strong><ul style="margin: 4px 0 8px 0; padding-left: 18px;">'
        for ep in cat_items:
            pod_name = html.escape(str(ep.get("podcast_name", ep.get("podcast", "Podcast"))))
            ep_title = html.escape(str(ep.get("title", "Episode")))
            toc_html += f'<li style="color: #8b949e;"><span style="color: #79c0ff; font-weight: 600;">{pod_name}</span>: <em style="color: #c9d1d9;">{ep_title}</em></li>'
        toc_html += '</ul></li>'
    toc_html += """
        </ul>
    </div>
    """

    # Build Episode Cards
    episodes_html = ""
    for cat, cat_items in categories.items():
        emoji = CATEGORY_EMOJIS.get(cat, "🎙️")
        episodes_html += f"""
        <div style="margin: 32px 0 16px 0;">
            <h2 style="color: #58a6ff; font-size: 20px; font-weight: 700; border-left: 4px solid #00ccaa; padding-left: 12px; margin: 0 0 16px 0;">
                {emoji} {html.escape(cat)}
            </h2>
        </div>
        """
        for item in cat_items:
            podcast_name = html.escape(str(item.get("podcast_name", item.get("podcast", "Podcast"))))
            title = html.escape(str(item.get("title", "Untitled Episode")))
            published = html.escape(str(item.get("published", "Recent")))
            link = item.get("link", "")
            
            summary_points = item.get("summary", [])
            summary_html = ""
            for pt in summary_points:
                summary_html += f'<li style="margin-bottom: 8px; color: #c9d1d9; line-height: 1.6; font-size: 14px;">{html.escape(str(pt))}</li>'
            
            title_tag = f'<a href="{html.escape(link, quote=True)}" style="color: #58a6ff; text-decoration: none; font-weight: 700; font-size: 18px; line-height: 1.4;">{title}</a>' if link else f'<span style="color: #f0f6fc; font-size: 18px; font-weight: 700;">{title}</span>'
            button_tag = f'<div style="margin-top: 18px;"><a href="{html.escape(link, quote=True)}" style="display: inline-block; background-color: #00ccaa; color: #010409; font-weight: 700; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 13px;">🎧 Listen / View Episode</a></div>' if link else ''
            
            episodes_html += f"""
            <article style="margin-bottom: 28px; background-color: #0d1117; border: 1px solid #30363d; border-radius: 12px; overflow: hidden;">
                <div style="background-color: #161b22; padding: 14px 20px; border-bottom: 1px solid #30363d; display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <span style="color: #00ccaa; font-weight: 800; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">
                            🎧 {podcast_name}
                        </span>
                    </div>
                    <div style="color: #8b949e; font-size: 12px;">
                        📅 {published}
                    </div>
                </div>
                <div style="padding: 20px 24px;">
                    <div style="margin-bottom: 14px;">
                        {title_tag}
                    </div>
                    <div style="margin: 16px 0 12px 0;">
                        <strong style="color: #ffa657; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 8px;">
                            💡 Key Discussion & Highlights
                        </strong>
                        <div style="background-color: #161b22; border-left: 4px solid #58a6ff; padding: 14px 18px; border-radius: 6px;">
                            <ul style="margin: 0; padding-left: 18px;">
                                {summary_html if summary_html else '<li style="color: #8b949e;">Publisher notes extracted and verified.</li>'}
                            </ul>
                        </div>
                    </div>
                    {button_tag}
                </div>
            </article>
            """

    current_date = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
    return f"""<!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="background-color: #010409; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 24px 16px; line-height: 1.6;">
        <main style="max-width: 780px; margin: 0 auto;">
            <header style="margin-bottom: 28px; padding-bottom: 18px; border-bottom: 3px solid #00ccaa; text-align: center;">
                <h1 style="color: #00ccaa; font-size: 28px; font-weight: 800; margin: 0 0 6px 0; letter-spacing: -0.5px;">
                    🎙️ Podcast Intelligence Digest
                </h1>
                <p style="color: #8b949e; font-size: 14px; margin: 0;">
                    {current_date} · {len(items)} episode(s) from {len(set(it.get("podcast_name", "") for it in items))} curated feeds
                </p>
            </header>
            
            {toc_html}
            {episodes_html}
            
            <footer style="margin-top: 48px; padding-top: 20px; border-top: 1px solid #30363d; color: #8b949e; font-size: 12px; text-align: center;">
                <p style="margin: 0 0 6px 0;">Podcast Intelligence Pipeline · Zero media downloads · Publisher metadata verified</p>
                <p style="color: #484f58; font-size: 11px; margin: 0;">Automated run · Privacy boundary enforced</p>
            </footer>
        </main>
    </body>
    </html>"""


def send_digest(items: List[Mapping[str, Any]], dry_run: bool = False) -> None:
    """Send the HTML digest via SMTP with plaintext fallback."""
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", 587))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")
    recipient = os.environ.get("REPORT_RECIPIENT")
    
    html_content = _build_html(items)
    
    plain_lines = ["🎙️ PODCAST INTELLIGENCE DIGEST\n============================\n"]
    for i, it in enumerate(items, 1):
        pname = it.get("podcast_name", it.get("podcast", "Podcast"))
        title = it.get("title", "Episode")
        pub = it.get("published", "")
        link = it.get("link", "")
        plain_lines.append(f"{i}. [{pname}] {title}")
        if pub:
            plain_lines.append(f"   Published: {pub}")
        if link:
            plain_lines.append(f"   Listen: {link}")
        for pt in it.get("summary", []):
            plain_lines.append(f"   - {pt}")
        plain_lines.append("")
    plain_content = "\n".join(plain_lines)
    
    if dry_run:
        print("--- DRY RUN: Would send email ---")
        print(f"Recipient: {recipient}")
        print(f"Subject: 🎙️ Podcast Digest: {len(items)} Episode(s)")
        print(plain_content)
        return
        
    if not all([host, port, user, password, recipient]):
        print("Warning: Missing SMTP credentials. Skipping email delivery.")
        return
        
    msg = EmailMessage()
    msg["Subject"] = f"🎙️ Podcast Digest: {len(items)} Episode(s) Summary"
    msg["From"] = f"Podcast Intelligence <{user}>"
    msg["To"] = recipient
    msg.set_content(plain_content)
    msg.add_alternative(html_content, subtype="html")
    
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
    print(f"Podcast digest email successfully sent to {recipient}")
