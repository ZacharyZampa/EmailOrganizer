"""
Example: Custom minimal HTML digest renderer

Note example was AI Generated so take with a grain of salt

This shows how to create your own digest template
while using the same data structure.
"""

from lib.domain.digest_renderer import DigestRenderer
from lib.domain.digest_data import DigestData


class MinimalHTMLRenderer(DigestRenderer):
    """A minimal, text-focused HTML renderer."""

    def render(self, data: DigestData) -> str:
        """Render digest as minimal HTML."""
        
        email_list = ""
        for email in sorted(data.emails, key=lambda e: -e.priority):
            email_list += f"""
            <div style="margin-bottom: 20px; padding: 10px; border-left: 3px solid #333;">
                <strong>{email.title}</strong><br>
                <small>{email.sender} | Priority: {email.priority}</small><br>
                <p>{email.summary}</p>
                <a href="{data.thread_base}{email.gmail_id}">View Email →</a>
            </div>
            """
        
        volume_list = ""
        for sender in data.high_volume_senders:
            volume_list += f"""
            <li><strong>{sender.sender}</strong>: {sender.total} emails</li>
            """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }}
        h1 {{ font-size: 24px; }}
        h2 {{ font-size: 18px; margin-top: 30px; }}
    </style>
</head>
<body>
    <h1>📬 Email Digest</h1>
    <p>{len(data.emails)} new emails</p>
    
    <h2>Recent Emails</h2>
    {email_list if email_list else "<p>No new emails</p>"}
    
    {f"<h2>High Volume Senders</h2><ul>{volume_list}</ul>" if volume_list else ""}
    
    <hr>
    <small>Generated locally with AI</small>
</body>
</html>
"""
        return html


# Example usage
if __name__ == "__main__":
    from lib.domain.digest_data import DigestData, DigestEmail, HighVolumeSender
    
    # Create sample data
    data = DigestData(
        emails=[
            DigestEmail(
                gmail_id="123",
                type="work",
                title="Project Update",
                sender="boss@company.com",
                summary="Q1 goals need review by Friday",
                priority=5
            )
        ],
        stale_emails=[],
        high_volume_senders=[
            HighVolumeSender(
                sender="newsletter@tech.com",
                total=25,
                categories={"newsletter": 25},
                is_newsletter=True
            )
        ],
        thread_base="https://mail.google.com/mail/u/0/#inbox/"
    )
    
    # Render with custom template
    renderer = MinimalHTMLRenderer()
    html = renderer.render(data)
    print(html)
