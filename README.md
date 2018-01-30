# web_server
#### 基于MVC架构，采用Python Socket包和HTTP协议实现了一个完整的Web Server
models文件夹下为自己实现的基于txt文件的ORM框架

static存放静态文件

template存放前端html文件

routes.py存放路由函数, 包含了用字典实现的路由分发函数, 以下是文件中的部分代码:
```python
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
```

server.py为服务启动文件, 定义了一个保存请求的类与url解析函数, 以下是文件中的部分代码:
```python
class Request(object):
    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''
        self.raw_data = ''
        self.headers = {}
        self.cookies = {}

    def add_cookies(self):
        cookies = self.headers.get('Cookie', '')
        kvs = cookies.split('; ')
        log('cookie', kvs)
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def add_headers(self, header):
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v
        self.cookies = {}
        self.add_cookies()

    def form(self):
        body = urllib.parse.unquote(self.body)
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        return f
```       

