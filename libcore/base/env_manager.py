import os
from omegaconf import OmegaConf
from redis.commands.graph.node import Node
from redis.commands.graph.edge import Edge
from .redis_manager import RedisManager
from .singleton_class import SingletonClass

class EnvManager(SingletonClass):
    def __init__(self):
        self.conn = RedisManager().get_conn()
        print("env manager ping", self.conn.ping())
        self.conf_graph = self.conn.graph()
        pass

    def build_graph_conf(self, config):
        if not config: # early quit
            return False

        print("config", config)
        print("is tupe list", isinstance(config, (tuple, list)), type(config))

        if isinstance(config, (tuple, list)):
            result = []
            for cf in config:
                result.append(self.build_graph_conf(cf))
            return result
        elif isinstance(config, str):
            if os.path.isdir(config):
                config = os.path.join(config, "__conf__.yml")
            
            config_dict = OmegaConf.to_container(OmegaConf.load(config))
            addon_name = os.path.basename(os.path.dirname(os.path.abspath(config)))
            result = Node(node_id=addon_name, label=addon_name, properties=config_dict)
            self.conf_graph.add_node(result)

            depend_nodes = self.build_graph_conf(config_dict.get("DEPENDS", False))
            if depend_nodes:
                for dnode in depend_nodes:
                    print(result, "->", dnode)
                    # self.conf_graph.add_edge(Edge(result, 'depends', dnode, properties={}))
        print("No if elif", config)
        return result

    # Load config recursively
    def load_config(self, config_paths=[]):
        self.build_graph_conf(config_paths)
        self.conf_graph.commit()
        graph_keys = self.conf_graph.list_keys()
        print("graph_keys", graph_keys)
        pass
    