# web_server
#### 基于MVC架构，采用Python Socket包和HTTP协议实现了一个完整的Web Server
models文件夹下为自己实现的基于txt文件的ORM框架

static存放静态文件

template存放前端html文件

routes.py存放路由函数

server.py为服务启动文件，也包含了url解析函数与用字典实现的路由分发函数
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
