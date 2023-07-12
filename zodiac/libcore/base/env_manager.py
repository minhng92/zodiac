import os
from typing import Any
# from omegaconf import OmegaConf
# from redis.commands.graph.node import Node
# from redis.commands.graph.edge import Edge
from .app_singleton import AppSingleton
from .redis_manager import redis_manager
from .module_manager import module_manager
from .conf_manager import conf_manager
from .om_model import OMModel

import logging
_logger = logging.getLogger(__name__)

class ModelOM(dict):
    def __getitem__(self, __key: Any) -> Any:
        if __key not in self:
            self[__key] = OMModel(__key)
        return super().__getitem__(__key)

class EnvManager(AppSingleton):
    def __init__(self):
        self.redis_manager = redis_manager
        self.module_manager = module_manager
        self.conf_manager =conf_manager
        self.modules_from_config = []
        self.install_from_config = ""
        self.model_om = ModelOM()    # dict like instance

        self.env_attr_mapping = {
            conf_manager.const: self.conf_manager[self.conf_manager.const], # env.const
            "conf": self.conf_manager, # env.conf
            "model": self.model_om,
        }
        pass

    def __getitem__(self, model_name):
        # if model_name not in self.model_om:   # => handled in "ModelOM"
        #     self.model_om[model_name] = OMModel(model_name)
        return self.model_om[model_name]

    def __getattr__(self, attr):
        if attr in self.env_attr_mapping.keys():
            return self.env_attr_mapping[attr]

    # Load module recursively
    def load_modules(self, modules_from_config=[], install_from_config=""):
        self.modules_from_config = modules_from_config
        self.install_from_config = install_from_config
        self.module_manager.load_modules(module_paths=modules_from_config, install_modules=install_from_config)
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

env_manager = EnvManager()
