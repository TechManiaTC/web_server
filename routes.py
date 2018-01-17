from models.session import Session
from utils import log
from models.message import Message
from models.user import User

import random

def random_string():
    """
    生成一个随机的字符串
    """
    seed = 'dfsdfsadffsdafasfsxcvsfdfdasdf'
    s = ''
    for i in range(16):
        # 这里 len(seed) - 2 是因为我懒得去翻文档来确定边界了
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


def template(name):
    """
    根据名字读取 templates 文件夹里的一个文件并返回
    """
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def current_user(request):
    # cookie 版本
    # username = request.cookies.get('user', '【游客】')
    # session 版本
    session_id = request.cookies.get('session_id', None)
    s = Session.find_by(session_id=session_id)
    if s is None:
        return '【游客】'
    else:
        return s.username


def route_index(request):
    """
    主页的处理函数, 返回主页的响应
    """
    header = 'HTTP/1.x 210 VERY OK\r\nContent-Type: text/html\r\n'
    body = template('index.html')
    username = current_user(request)
    body = body.replace('{{username}}', username)
    r = header + '\r\n' + body
    return r.encode()


def response_with_headers(headers):
    """
    Content-Type: text/html
    Set-Cookie: user=test
    """
    header = 'HTTP/1.x 210 VERY OK\r\n'
    header += ''.join([
        '{}: {}\r\n'.format(k, v) for k, v in headers.items()
    ])
    return header


def route_login(request):
    """
    登录页面的路由函数
    """
    headers = {
        'Content-Type': 'text/html',
    }
    log('login, headers', request.headers)
    log('login, cookies', request.cookies)
    username = current_user(request)
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_login():
            # 下面是把用户名存入 cookie 中
            # session 会话
            # token 令牌
            # cookie 版本
            # headers['Set-Cookie'] = 'user={}'.format(u.username)
            # session 版本
            # 设置一个随机字符串来当令牌使用
            session_id = random_string()
            headers['Set-Cookie'] = 'session_id={}'.format(session_id)
            # session[session_id] = u.username
            s = Session.new(dict(
                session_id=session_id,
                username=u.username,
            ))
            s.save()
            result = '登录成功'
        else:
            result = '用户名或者密码错误'
    else:
        result = ''
    body = template('login.html')
    body = body.replace('{{result}}', result)
    body = body.replace('{{username}}', username)
    header = response_with_headers(headers)
    r = '{}\r\n{}'.format(header, body)
    log('login 的响应', r)
    return r.encode()


def route_register(request):
    """
    注册页面的路由函数
    """
    header = 'HTTP/1.x 210 VERY OK\r\nContent-Type: text/html\r\n'
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_register():
            u.save()
            result = '注册成功<br> <pre>{}</pre>'.format(User.all())
        else:
            result = '用户名或者密码长度必须大于2'
    else:
        result = ''
    body = template('register.html')
    body = body.replace('{{result}}', result)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def route_message(request):
    """
    主页的处理函数, 返回主页的响应
    GET /messages?message=123&author=test HTTP/1.1
    Host: localhost:3000
    """
    log('本次请求的 method', request.method)
    username = current_user(request)
    if username == '【游客】':
        return error(request)
    else:
        form = request.query
        if len(form) > 0:
            m = Message.new(form)
            log('get', form)
            m.save()

        header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
        body = template('messages.html')
        ms = '<br>'.join([str(m) for m in Message.all()])
        body = body.replace('{{messages}}', ms)
        r = header + '\r\n' + body
        return r.encode()


def route_message_add(request):
    """
    主页的处理函数, 返回主页的响应
    POST /messages HTTP/1.1
    Host: localhost:3000
    Content-Type: application/x-www-form-urlencoded

    message=123&author=test
    """
    log('本次请求的 method', request.method)
    form = request.form()
    m = Message.new(form)
    log('post', form)
    # 应该在这里保存 message_list
    m.save()

    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    body = template('messages.html')
    ms = '<br>'.join([str(m) for m in Message.all()])

    body = body.replace('{{messages}}', ms)
    r = header + '\r\n' + body
    return r.encode()


def route_static(request):
    """
    静态资源的处理函数, 读取图片并生成响应返回
    """
    filename = request.query.get('file', 'doge.gif')
    path = 'static/' + filename
    with open(path, 'rb') as f:
        header = b'HTTP/1.x 200 OK\r\nContent-Type: image/gif\r\n\r\n'
        img = header + f.read()
        return img


def route_profile(request):
    headers = {
        'Content-Type': 'text/html',
    }
    session_id = request.cookies.get('session_id', None)
    s = Session.find_by(session_id=session_id)
    if s is None:
        header = 'HTTP/1.x 302 redirect\r\nLocation:/login\r\n'
        header += ''.join([
            '{}: {}\r\n'.format(k, v) for k, v in headers.items()
        ])
        r = '{}\r\n'.format(header)
        return r.encode()
    else:
        headers = 'HTTP/1.x 210 VERY OK\r\nContent-Type: text/html\r\n'
        body = template('profile.html')
        username = s.username
        u = User.find_by(username=username)
        id = u.id
        note = u.note
        body = body.replace('{{username}}', username)
        body = body.replace('{{id}}', str(id))
        body = body.replace('{{note}}', note)
        r = headers + '\r\n' + body
        return r.encode()


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    d = {
        '/': route_index,
        '/login': route_login,
        '/register': route_register,
        '/messages': route_message,
        '/messages/add': route_message_add,
        '/profile': route_profile,
    }
    return d


def error(request, code=404):
    """
    根据 code 返回不同的错误响应
    目前只有 404
    """
    e = {
        404: b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
        302: b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>REDIRECT</h1>',
    }
    return e.get(code, b'')
