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
cli_params = sys.argv[1:]   # additional config files: [] or ["app.yml", ...]
for config_path in cli_params:
    conf_manager += config_path

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

    module_dirs = base_conf["module_dirs"]
    install_modules = base_conf["install_modules"]

    available_module_paths = []
    for mod_dir in module_dirs:
        available_module_paths += [os.path.join(mod_dir, item) for item in os.listdir(mod_dir) if os.path.isdir(os.path.join(mod_dir, item)) and not item.startswith(".")]

    install_module_paths = install_modules
    # for mod_dir in module_dirs:
    #     for inst_mod in install_modules:
    #         if os.path.isdir(os.path.join(mod_dir, inst_mod)):
    #             install_module_paths.append(os.path.join(mod_dir, inst_mod))

    env.load_modules(
        modules_from_config=available_module_paths, 
        install_from_config=install_module_paths,
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
