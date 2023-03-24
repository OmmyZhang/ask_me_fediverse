from flask import (
    Flask, request, render_template, send_from_directory, abort, redirect)
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# from flask_migrate import Migrate
from mastodon import Mastodon
import re
import random
import string
import datetime
from dateutil.tz import tzlocal
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

BOT_NAME = Config.BOT_NAME
MAST_URL = Config.MAST_URL
WORK_URL = Config.WORK_URL
TOKEN = Config.TOKEN
CLIENT_ID = Config.CLIENT_ID
CLIENT_SEC = Config.CLIENT_SEC

MENTION_BOT_TEMP = re.compile(
    r'<span class=\"h-card\">'
    '<a [^>]*href=\"{}/{}\"[^>]*>'
    '@<span>.*?</span>'
    '</a></span>'.format(MAST_URL, BOT_NAME)
)
DELETE_TEMP = re.compile(r'<p>\s*删除\s*</p>')

REDIRECT_URI = WORK_URL + '/askMe/auth'

th = Mastodon(
    access_token=TOKEN,
    api_base_url=MAST_URL
)


limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["50 / minute"],
)

db = SQLAlchemy(app)
# migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    acct = db.Column(db.String(64))
    disp = db.Column(db.String(64))
    avat = db.Column(db.String(256))
    url = db.Column(db.String(128))
    secr = db.Column(db.String(16))
    root = db.Column(db.BigInteger)

    def __init__(self, acct):
        self.acct = acct

    def __repr__(self):
        return f"@{self.acct}[{self.disp}]"


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    acct = db.Column(db.String(64))
    content = db.Column(db.String(400))
    time = db.Column(db.DateTime)
    toot = db.Column(db.BigInteger)

    def __init__(self, acct, content, toot):
        self.acct = acct
        self.content = content
        self.toot = toot
        self.time = datetime.datetime.now()

    def __repr__(self):
        return f"[{self.acct}]{self.content}({self.toot})"


@app.route('/askMe/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/askMe/img/<path:path>')
def send_img(path):
    return send_from_directory('static/img', path)


@app.route('/askMe/')
def root():
    return app.send_static_file('index.html')


@app.route('/askMe/footer.html')
def root_footer():
    return app.send_static_file('footer.html')


@app.route('/askMe/auth')
@limiter.limit("10 / minute")
def set_inbox_auth():
    code = request.args.get('code')
    autoSend = request.args.get('autoSend', '')
    secr = request.args.get('secr', '')

    if secr and not re.match('[a-z]{0,16}', secr):
        abort(422)

    client = Mastodon(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SEC,
        api_base_url=MAST_URL
    )
    client.log_in(
        code=code,
        redirect_uri=(
            '{}?autoSend={}&secr={}'
        ).format(REDIRECT_URI, autoSend, secr),
        scopes=[
            'read:accounts',
            'write:statuses'
        ] if autoSend else ['read:accounts']
    )

    info = client.account_verify_credentials()

    acct = info.acct
    u = User.query.filter_by(acct=acct).first()
    if not u:
        u = User(acct)
        db.session.add(u)

    u.secr = secr or u.secr or ''.join(random.choice(
        string.ascii_lowercase) for i in range(16))

    u.disp = info.display_name
    u.url = info.url
    u.avat = info.avatar

    if autoSend:
        client.status_post(
            f"[自动发送] 我创建了一个匿名提问箱，欢迎提问~\n"
            f"{WORK_URL}/askMe/{acct}/{u.secr}",
            visibility='public')

    db.session.commit()

    return redirect(f"/askMe/{acct}/{u.secr}")


@app.route('/askMe/inbox', methods=['POST'])
@limiter.limit("10 / minute")
def set_inbox():
    acct = request.form.get('username')
    if not re.match('[A-Za-z0-9_]{1,30}(@[a-z\\.-_]+)?', acct):
        return 'id', 422

    r = th.conversations()
    for conv in r:
        status = conv.last_status
        account = status.account
        if acct == account.acct:
            pt = status.content.strip()

            x = re.findall(r'新建(\[[a-z]{1,32}\])?', pt)
            if not x:
                return '私信格式无效，请检查并重新发送', 422

            secr = x[0][1:-1] if x[0] else ''.join(
                random.choice(string.ascii_lowercase) for i in range(16))

            u = User.query.filter_by(acct=acct).first()
            if not u:
                u = User(acct)
                db.session.add(u)

            u.disp = account.display_name
            u.url = account.url
            u.avat = account.avatar
            u.secr = secr
            db.session.commit()

            th.status_post(
                f"@{acct} 设置成功! 当前提问箱链接 "
                f"{WORK_URL}/askMe/{acct}/{secr}\n"
                f"(如需在微信等无链接预览的平台分享，建议先发给自己，"
                "点开，再点击分享到朋友圈等)",
                in_reply_to_id=status.id,
                visibility='direct'
            )

            return acct + '/' + secr

    return '未找到私信，请确认已发送且是最近发送', 404


@app.route('/askMe/<acct>/<secr>/')
def inbox(acct, secr):
    u = User.query.filter_by(acct=acct, secr=secr).first_or_404()

    qs = [{
        'content': q.content,
        'toot': q.toot,
        'time': q.time.replace(tzinfo=tzlocal())
    } for q in Question.query.filter_by(acct=acct).all()
    ]

    return render_template('inbox.html', acct=u.acct, disp=(
        u.disp or u.acct), url=u.url, avat=u.avat, qs=qs)


@app.route('/askMe/<acct>/<secr>/new', methods=['POST'])
@limiter.limit("50 / hour; 1 / 2 second")
def new_question(acct, secr):
    u = User.query.filter_by(acct=acct, secr=secr).first()
    if not u:
        abort(404)

    content = request.form.get('question')
    if not content or len(content) > 400:
        abort(422)

    if not Question.query.filter_by(acct=acct, content=content).first():

        if not u.root:
            toot = th.status_post(
                f"@{acct} 欢迎使用匿名提问箱。"
                "未来的新提问会集中显示在这里，方便管理。",
                visibility='direct')
            u.root = toot.id

        toot = th.status_post(
            f"@{acct} 叮~ 有新提问：\n\n{content}",
            in_reply_to_id=u.root,
            visibility='direct'
        )

        q = Question(acct, content, toot.id)
        db.session.add(q)
        db.session.commit()

    return redirect(".")


def render_content(text, emojis):
    text = MENTION_BOT_TEMP.sub('', text)
    for emoji in emojis:
        text = text.replace(
            ':%s:' % emoji.shortcode,
            '<img class="emoji" src="%s">' % emoji.url
        )

    return text


@app.route('/askMe/<acct>/<secr>/<int:toot>')
def question_info(acct, secr, toot):
    q = Question.query.filter_by(acct=acct, toot=toot).first()
    if not q or not User.query.filter_by(acct=acct, secr=secr).first():
        abort(404)

    context = th.status_context(toot)
    replies = [
        {
            'disp': (t.account.display_name or t.account.acct),
            'url': t.account.url,
            'content': render_content(t.content, t.emojis),
            'time': str(t.created_at),
            'media': t.media_attachments,
        }
        for t in context.descendants
    ]

    if replies and DELETE_TEMP.match(replies[-1].get('content')):
        db.session.delete(q)
        db.session.commit()
        th.status_delete(toot)
        return '该提问已被删除', 404

    return {'replies': replies}


if __name__ == '__main__':
    app.run(debug=True)
