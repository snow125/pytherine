from BaseHTTPServer import *
import urllib
from wsgiref.handlers import SimpleHandler
from wsgiref.simple_server import *
import sys

__version__ = '0.1'
server_version = "WSGIServer/" + __version__
sys_version = "Python/" + sys.version.split()[0]
software_version = server_version + ' ' + sys_version

func_views = {}

class DEVServer(HTTPServer):

    def server_bind(self):
        """Override server_bind to store the server name."""
        HTTPServer.server_bind(self)
        self.setup_environ()

    def setup_environ(self):
        # Set up base environment
        env = self.base_environ = {}
        env['SERVER_NAME'] = self.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PORT'] = str(self.server_port)
        env['REMOTE_HOST']=''
        env['CONTENT_LENGTH']=''
        env['SCRIPT_NAME'] = ''



class DEVRequestHandler(BaseHTTPRequestHandler):
    server_version = "WSGIServer/" + __version__


    def get_environ(self):
        env = self.server.base_environ.copy()
        env['SERVER_PROTOCOL'] = self.request_version
        env['REQUEST_METHOD'] = self.command
        if '?' in self.path:
            path,query = self.path.split('?',1)
        else:
            path,query = self.path,''

        env['PATH_INFO'] = urllib.unquote(path)
        env['QUERY_STRING'] = query

        host = self.address_string()
        if host != self.client_address[0]:
            env['REMOTE_HOST'] = host
        env['REMOTE_ADDR'] = self.client_address[0]

        if self.headers.typeheader is None:
            env['CONTENT_TYPE'] = self.headers.type
        else:
            env['CONTENT_TYPE'] = self.headers.typeheader

        length = self.headers.getheader('content-length')
        if length:
            env['CONTENT_LENGTH'] = length

        for h in self.headers.headers:
            k,v = h.split(':',1)
            k=k.replace('-','_').upper(); v=v.strip()
            if k in env:
                continue                    # skip content length, type,etc.
            if 'HTTP_'+k in env:
                env['HTTP_'+k] += ','+v     # comma-separate multiple headers
            else:
                env['HTTP_'+k] = v
        return env

    def get_stderr(self):
        return sys.stderr

    def handle(self):
        """Handle a single HTTP request"""

        self.raw_requestline = self.rfile.readline()
        if not self.parse_request(): # An error code has been sent, just exit
            return

        handler = SimpleHandler(
            self.rfile, self.wfile, self.get_stderr(), self.get_environ()
        )
        handler.request_handler = self      # backpointer for logging
        view_func = self.check_path(self.get_environ()['PATH_INFO'])
        handler.run(view_func)


    def check_path(self, path_info):
        if path_info == '/':
            return self.make_app_by_view_result(index())
        else:
            path_info = path_info[1:]
            return self.make_app_by_path(path_info)

    def make_app_by_path(self, path_info):
        result = func_views[path_info]()
        return self.make_app_by_view_result(result)

    def make_app_by_view_result(self, result):
        def application(environ, start_response):
            start_response('200 OK', [('Content-Type', 'text/html')])
            return result
        return application


def add_rule(f):
    func_views[f.__name__] = f
    return f

def index():
    return '<h1>Welcome to the pytherine!</h1>'

@add_rule
def hello():
    return 'hi pytherine'

if __name__ == '__main__':
    HOST, PORT = 'localhost', 9999
    server = DEVServer((HOST, PORT), DEVRequestHandler)
    # server.set_app(make_app('hello'))
    server.serve_forever()
