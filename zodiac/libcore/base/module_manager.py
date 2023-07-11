import os
from omegaconf import OmegaConf
import redis_om
from redis.commands.graph.node import Node
from redis.commands.graph.edge import Edge

from .redis_manager import RedisManager
from .singleton_class import SingletonClass
from .om_model import register_om_model
from . import om_model

import logging
_logger = logging.getLogger(__name__)

CONF_YML_NAME = "conf.yml"

class ModuleManager(SingletonClass):
    def __init__(self):
        self.conn = RedisManager().get_conn()
        self.module_graph = self.conn.graph()
        try:
            self.module_graph.delete()
        except:
            pass
        pass

    def build_graph_module(self, module_paths, current_path=False):
        if not module_paths: # early quit
            return False
        
        if isinstance(module_paths, (tuple, list)):
            result = []
            for mp in module_paths:
                result.append(self.build_graph_module(mp, current_path=current_path))
            return result
        elif isinstance(module_paths, str): # only path of module
            module_path = module_paths
            if current_path:
                module_path = os.path.join(current_path, module_path)

            if os.path.isdir(module_path):
                config_yml = os.path.join(module_path, CONF_YML_NAME)

            config_dict = OmegaConf.to_container(OmegaConf.load(config_yml))
            node_properties = dict(config_dict)
            module_name = os.path.basename(module_path)
            node_properties.update({
                "CODE": module_name,
                "MODULE_PATH": os.path.abspath(module_path)
            })
            result = Node(alias=module_name, label="MODULE", properties=node_properties)
            self.module_graph.add_node(result)

            depend_nodes = self.build_graph_module(config_dict.get("DEPENDS", False), current_path=module_path)
            if depend_nodes:
                for dnode in depend_nodes:
                    self.module_graph.add_edge(Edge(result, 'DEPENDS', dnode, properties={}))
        return result

    def parse_graph_query(self, query_result, prop_names=None):
        result = []
        for node_list in query_result.result_set:
            if len(node_list) == 1:
                elem = str(node_list[0]) if not prop_names else tuple([node_list[0].properties[pn] for pn in prop_names])
                result.append(elem)
            elif len(node_list) > 1:
                sub_result = []
                for node in node_list:
                    elem = str(node) if not prop_names else tuple([node.properties[pn] for pn in prop_names])
                    sub_result.append(elem)
                result.append(sub_result)
        return result

    # Load config recursively
    def load_modules(self, module_paths=[], install_modules=[]):
        self.build_graph_module(module_paths)
        self.module_graph.commit()        
        
        module_install_list = []
        graph_result = 1
        while graph_result:
            # leaf node (included single node)
            match_query = "MATCH (p) WHERE NOT (p)-[]->() RETURN p"
            graph_query_result = self.module_graph.query(match_query)
            graph_result = self.parse_graph_query(graph_query_result, prop_names=["CODE"]) # ['stock_chart', 'btc_chart']
            print(match_query, "=>", graph_result)
            print("--------------------------------")
            # resolve node leaf
            for module_code, node_list in zip(graph_result, graph_query_result.result_set):
                if module_code[0] in install_modules:
                    node_prop = node_list[0].properties
                    module_install_list.append((node_prop["MODULE_PATH"], node_prop))
                    pass
            # resolve and delete leaf node
            self.module_graph.query("MATCH (p) WHERE NOT (p)-[]->() DELETE p")
        
        install_models = []
        for module_path, node_prop in module_install_list:
            install_models += self.install_module(module_path, node_prop)
        # Before running queries, we need to run migrations to set up the
        # indexes that Redis OM will use. You can also use the `migrate`
        # CLI tool for this!
        redis_om.Migrator().run()

        # test new model
        # _logger.info("Debug dynamic redis model %s" % str(install_models))
        # for model_name in install_models:
        #     if model_name != "stock_code":
        #         continue
        #     model = getattr(om_model, model_name)
        #     new_code = model(
        #         name="FLC",
        #         code="flc",
        #     )
        #     new_code.save()
        #     _logger.info("%s -> created record %s", model_name, new_code.key())
        #     res2 = model.find(model.code == "flc").all()
        #     _logger.info("res2 (n=%d): %s" % (len(res2), str(res2)))
        pass
    
    def install_module(self, module_path, module_config_dict={}):
        print("INstall module:", module_path)
        print("module_config_dict", module_config_dict)
        install_models = []
        for c_model_path in module_config_dict.get("MODELS", []):
            model_path = os.path.join(module_path, c_model_path)
            model_path = c_model_path if not os.path.isfile(model_path) else model_path
            model_yml_dict = OmegaConf.to_container(OmegaConf.load(model_path))
            for model_name, model_yml_dict in model_yml_dict.items():
                register_om_model(model_name, model_yml_dict)                
                install_models.append(model_name)
                _logger.info("register_om_model: %s with %s", model_name, str(model_yml_dict))
        return install_models  
        pass
