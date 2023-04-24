import os
from omegaconf import OmegaConf
from redis.commands.graph.node import Node
from redis.commands.graph.edge import Edge
from .singleton_class import SingletonClass
from .redis_manager import RedisManager
from .module_manager import ModuleManager
from .om_model import OMRecord

import logging
_logger = logging.getLogger(__name__)

class EnvManager(SingletonClass):
    def __init__(self):
        self.redis_manager = RedisManager()
        self.module_manager = ModuleManager()
        self.modules_from_config = []
        self.install_from_config = ""
        self.model_omrecords = {}
        pass

    def __getitem__(self, model_name):
        if model_name not in self.model_omrecords:
            self.model_omrecords[model_name] = OMRecord(model_name)
        return self.model_omrecords[model_name]

    # Load module recursively
    def load_modules(self, modules_from_config=[], install_from_config=""):
        self.modules_from_config = modules_from_config
        self.install_from_config = install_from_config
        self.module_manager.load_modules(module_paths=modules_from_config, install_modules=[module_code.strip() for module_code in install_from_config.split(",")])
        pass
    
    # Add modules on-the-fly
    def add_modules(self, modules_from_config=[]):
        for module_config in modules_from_config:
            # add module config to db
            # TODO
            pass
        self.reload_modules()
        pass

    def install_modules(self, install_modules=[]):
        for module_code in install_modules:
            # set state to installed
            # TODO
            pass
        self.reload_modules()

    # Reload modules on-the-fly
    def reload_modules(self):
        self.load_modules(
            modules_from_config=self.modules_from_config,
            install_from_config=self.install_from_config,
        )
        pass
