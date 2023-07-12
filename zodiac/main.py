import os
import sys
import asyncio
import tornado
from libcore.base.controller_manager import ControllerManagerListCreate, ControllerManagerGetUpdateDelete, MainHandler
from libcore.base.conf_manager import conf_manager

import logging
_logger = logging.getLogger(__name__)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s@%(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

conf_manager += "conf.yml"

os.environ["REDIS_OM_URL"] = conf_manager[conf_manager.base]["redis_url"]
from libcore.base.env_manager import EnvManager

def make_app(env):
    MODEL_LISTCREATE_ENDPOINT = r'/rest/(?P<model_name>[a-zA-Z0-9-_]+)/?'
    MODEL_GETUPDATEDELETE_ENDPOINT = r'/rest/(?P<model_name>[a-zA-Z0-9-_]+)/(?P<id>[a-zA-Z0-9-]+)/?'
    controllers = []
    controllers += [
        (r"/", MainHandler, {"app_info": "Welcome to Zodiac"}),
        (MODEL_LISTCREATE_ENDPOINT, ControllerManagerListCreate, {"env": env}),
        (MODEL_GETUPDATEDELETE_ENDPOINT, ControllerManagerGetUpdateDelete, {"env": env}),
    ]
    return tornado.web.Application(controllers, serve_traceback=True)
    
def main():
    env = EnvManager()
    base_conf = conf_manager[conf_manager.base]
    env.load_modules(
        modules_from_config=[base_conf["modules"], base_conf["extra_modules"]], 
        install_from_config=base_conf["install"],
    )
    
    # BUILD TORNADO APPLICATION
    sockets = tornado.netutil.bind_sockets(base_conf["port"])
    tornado.process.fork_processes(base_conf["num_workers"])
    async def post_fork_main():
        # server = TCPServer()
        # server.add_sockets(sockets)
        server = tornado.httpserver.HTTPServer(make_app(env))
        server.add_sockets(sockets)
        await asyncio.Event().wait()
    asyncio.run(post_fork_main())

if __name__ == "__main__":
    main()
