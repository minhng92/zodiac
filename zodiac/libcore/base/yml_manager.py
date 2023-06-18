from omegaconf import OmegaConf

class YmlManager():
    def __init__(self, yml_file_path):
        self.yml_file_path = yml_file_path
        self.data_conf = OmegaConf.load(self.yml_file_path) if self.yml_file_path else False
        self.data_dict = OmegaConf.to_container(self.data_conf) if self.data_conf else False
        pass

    def get_conf(self):
        return self.data_conf

    def get_dict(self):
        return self.data_dict

    def _convert_flatten_dict(self, data_dict, key_prefix=""):
        result = {}
        for k, v in data_dict.items():
            if isinstance(v, dict):
                result.update(self._convert_flatten_dict(data_dict=v, key_prefix="%s.%s" % (key_prefix, k) if key_prefix else k))
            else:
                result["%s.%s" % (key_prefix, k) if key_prefix else k] = v
            pass
        return result

    def get_flatten_dict(self):
        # convert dictionary to flatten dict, only one level of key
        return self._convert_flatten_dict(data_dict=self.data_dict, key_prefix="")
