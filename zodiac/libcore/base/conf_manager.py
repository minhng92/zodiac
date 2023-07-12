from omegaconf import OmegaConf
from .app_singleton import AppSingleton

class ConfManager(AppSingleton):
    base = "zodiac"
    const = "const"

    def __init__(self):
        self.conf_omg = {}
        self.conf_dict = {}
        pass
    
    def load_module_conf(self, conf_path):
        new_conf = OmegaConf.load(conf_path)
        new_cfg_dict = OmegaConf.to_container(new_conf)

        for name in new_cfg_dict.keys():
            if name in self.conf_omg and self.conf_omg[name]:
                self.conf_omg[name] = OmegaConf.merge(self.conf_omg[name], new_conf[name])
            else:
                self.conf_omg[name] = new_conf[name]

        for name, omg_conf in self.conf_omg.items():
            self.conf_dict[name] = OmegaConf.to_container(omg_conf) if omg_conf else omg_conf
        return self

    def get(self, name=False, default=False, is_omg=False):
        result = self.conf_omg if is_omg else self.conf_dict
        result = result.get(name, default) if name else result
        return result

    def __iadd__(self, conf_path):
        return self.load_module_conf(conf_path)

    def __add__(self, conf_path):
        return self.load_module_conf(conf_path)

    def __getitem__(self, name):
        return self.get(name, is_omg=False)

    def __getattr__(self, attr):
        return self.get(attr, is_omg=False)

conf_manager = ConfManager()
