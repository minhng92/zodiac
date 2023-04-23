import sys
import asyncio
import tornado
from tornado.options import define, options
from libcore.base.env_manager import EnvManager

import logging
_logger = logging.getLogger(__name__)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s@%(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

define("port", default=7777, help="port to listen on")
define("num_workers", default=1, help="number of processes")
define("redis_url", default="redis://@redis_stack:6380?decode_responses=True", help="Redis URL connection string")

define("modules", default="modules/_root", help="app config file")
define("extra_modules", default="modules/btc_chart", help="extra app config file")
define("install", default="stock_chart", help="Install modules")

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, config):
        self.config = config

    def get(self):
        self.write("Hello, world; config = %s" % self.config)

def make_app():
    controllers = []
    controllers.append(
        (r"/", MainHandler, {"config": options.config})
    )
    return tornado.web.Application(controllers)
    
def main():
    tornado.options.parse_command_line()

    ## TODO: pass yml config to model manager to migrate data structure -> Redis OM
    env = EnvManager()
    env.load_modules(
        modules_from_config=[options.modules, options.extra_modules], 
        install_from_config=options.install
    )

    raise Exception("Dev env stop here")

    # BUILD TORNADO APPLICATION
    sockets = tornado.netutil.bind_sockets(options.port)
    tornado.process.fork_processes(options.num_workers)
    async def post_fork_main():
        # server = TCPServer()
        # server.add_sockets(sockets)
        server = tornado.httpserver.HTTPServer(make_app())
        server.add_sockets(sockets)
        await asyncio.Event().wait()
    asyncio.run(post_fork_main())

if __name__ == "__main__":
    main()
