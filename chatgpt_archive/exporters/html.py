"""HTML exporter for conversation export with CSS styling."""

from typing import List
from html import escape

from .base import BaseExporter


class HTMLExporter(BaseExporter):
    """Export conversations to HTML format with CSS styling.

    Produces a self-contained HTML document with:
    - Embedded CSS for professional appearance
    - Responsive design for various screen sizes
    - Styled message bubbles for user/assistant roles
    - Proper escaping of content
    """

    format_name = "html"
    file_extension = ".html"

    CSS_STYLES = """
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
                         Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .header h1 {
            margin: 0 0 15px 0;
            font-size: 1.8em;
            font-weight: 600;
        }
        
        .header-meta {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .header-meta span {
            margin-right: 20px;
        }
        
        .conversation {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .message {
            margin-bottom: 20px;
            padding: 15px 20px;
            border-radius: 12px;
            position: relative;
        }
        
        .message:last-child {
            margin-bottom: 0;
        }
        
        .message-user {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        
        .message-assistant {
            background-color: #f3e5f5;
            border-left: 4px solid #9c27b0;
        }
        
        .message-system {
            background-color: #fff3e0;
            border-left: 4px solid #ff9800;
            font-style: italic;
        }
        
        .message-tool {
            background-color: #e8f5e9;
            border-left: 4px solid #4caf50;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
        }
        
        .message-header {
            font-weight: 600;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .message-role {
            text-transform: capitalize;
        }
        
        .message-user .message-role { color: #1565c0; }
        .message-assistant .message-role { color: #7b1fa2; }
        .message-system .message-role { color: #e65100; }
        .message-tool .message-role { color: #2e7d32; }
        
        .message-time {
            font-size: 0.8em;
            color: #666;
            font-weight: normal;
        }
        
        .message-content {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .message-content code {
            background-color: rgba(0, 0, 0, 0.05);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
        }
        
        .message-content pre {
            background-color: #282c34;
            color: #abb2bf;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
        }
        
        .message-content pre code {
            background: none;
            padding: 0;
            color: inherit;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 15px;
            color: #666;
            font-size: 0.85em;
        }
        
        @media (max-width: 600px) {
            body {
                padding: 10px;
            }
            
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 1.4em;
            }
            
            .header-meta span {
                display: block;
                margin-bottom: 5px;
            }
        }
    """

    def export(self, conversation: dict, messages: List[dict]) -> str:
        """Export conversation to HTML format.

        Args:
            conversation: Conversation metadata dictionary
            messages: List of message dictionaries

        Returns:
            HTML formatted string (complete document)
        """
        title = escape(self.get_display_title(conversation))
        created = self.format_timestamp(conversation.get("create_time"))
        model = escape(conversation.get("model") or "unknown")
        msg_count = conversation.get("message_count", len(messages))
        conv_id = escape(conversation.get("id", ""))

        # Build messages HTML
        messages_html = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content") or ""
            time_str = self.format_time(msg.get("create_time"))

            # Skip empty system messages
            if not content.strip() and role == "system":
                continue

            role_class = f"message-{role}"
            time_html = (
                f'<span class="message-time">{escape(time_str)}</span>'
                if time_str
                else ""
            )

            messages_html.append(
                f"""
                <div class="message {role_class}">
                    <div class="message-header">
                        <span class="message-role">{escape(role)}</span>
                        {time_html}
                    </div>
                    <div class="message-content">{escape(content)}</div>
                </div>
            """
            )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - ChatGPT Export</title>
    <style>
        {self.CSS_STYLES}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="header-meta">
            <span><strong>Created:</strong> {escape(created)}</span>
            <span><strong>Model:</strong> {model}</span>
            <span><strong>Messages:</strong> {msg_count}</span>
        </div>
        <div class="header-meta" style="margin-top: 10px; font-size: 0.8em; opacity: 0.7;">
            <span><strong>ID:</strong> {conv_id}</span>
        </div>
    </div>
    
    <div class="conversation">
        {"".join(messages_html)}
    </div>
    
    <div class="footer">
        Exported from ChatGPT Archive
    </div>
</body>
</html>"""

        return html
