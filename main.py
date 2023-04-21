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
define("config", default="addons/_root/__conf__.yml", help="app config file")
define("num_workers", default=1, help="number of processes")
define("redis_url", default="redis://@redis_stack:6380?decode_responses=True", help="Redis URL connection string")

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
    env.load_config(config_paths=[options.config,])

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
