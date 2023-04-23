import sys
import redis_om
from .pydantic_generator import generate_model

import logging
_logger = logging.getLogger(__name__)

def register_om_model(model_name, model_yml_dict):
    """
        model_name: res_partner, stock_code
    """
    dynamic_cls_name = model_name
    cls_ref = type(model_name, (eval(model_yml_dict.get("_inherit", "redis_om.JsonModel")), generate_model(name="%sPydantic"%model_name, _inherit=None, _fields=model_yml_dict.get("_fields", {}))), {})
    setattr(sys.modules[__name__], dynamic_cls_name, cls_ref)
    pass
