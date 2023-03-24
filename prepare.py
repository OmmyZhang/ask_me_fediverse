from ask import db, app
from config import Config


with open('static/ask.html', 'r') as f1:
    html = f1.read()

html = html.replace('{{MAST_URL}}', Config.MAST_URL)
html = html.replace('{{MAST_DOMAIN}}', Config.MAST_DOMAIN)
html = html.replace('{{CLIENT_ID}}', Config.CLIENT_ID)
html = html.replace('{{BOT_NAME}}', Config.BOT_NAME)

if not Config.ENABLE_DIRECT:
    html = html.replace('DIRECT_START -->', '').replace('<!-- DIRECT_END', '')
if not Config.ENABLE_OAUTH:
    html = html.replace('OAUTH_START -->', '').replace('<!-- OAUTH_END', '')

with open('static/index.html', 'w') as f2:
    f2.write(html)

with app.app_context():
    db.create_all()
