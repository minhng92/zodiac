import os
import sys
import asyncio
import tornado
from tornado.options import define, options
from libcore.base.controller_manager import ControllerManagerListCreate, ControllerManagerGetUpdateDelete, MainHandler
from omegaconf import OmegaConf
from libcore.base.yml_manager import YmlManager

import logging
_logger = logging.getLogger(__name__)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s@%(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

yml_manager = YmlManager("config.yml")
config_key_flatten_dict = yml_manager.get_flatten_dict()
for ckey, cval in config_key_flatten_dict.items():
    define(ckey, default=cval)  # define("zodiac.port", 7777)

os.environ["REDIS_OM_URL"] = options["zodiac.redis_url"]
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
    tornado.options.parse_command_line()

    env = EnvManager()
    env.load_modules(
        modules_from_config=[options["zodiac.modules"], options["zodiac.extra_modules"]], 
        install_from_config=options["zodiac.install"],
    )
    
    # BUILD TORNADO APPLICATION
    sockets = tornado.netutil.bind_sockets(options["zodiac.port"])
    tornado.process.fork_processes(options["zodiac.num_workers"])
    async def post_fork_main():
        # server = TCPServer()
        # server.add_sockets(sockets)
        server = tornado.httpserver.HTTPServer(make_app(env))
        server.add_sockets(sockets)
        await asyncio.Event().wait()
    asyncio.run(post_fork_main())

if __name__ == "__main__":
    main()
