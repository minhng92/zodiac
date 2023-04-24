import sys
import redis_om
from .pydantic_generator import generate_model

import logging
_logger = logging.getLogger(__name__)

class OMRecord():
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = getattr(sys.modules[__name__], model_name)

    async def get(self, pk):
        return self.model.get(pk)
    
    async def create(self, data):
        new_record = self.model(**data)
        new_record.save()
        return new_record

def register_om_model(model_name, model_yml_dict):
    """
        model_name: res_partner, stock_code
    """
    dynamic_cls_name = model_name
    cls_ref = type(model_name, (eval(model_yml_dict.get("_inherit", "redis_om.JsonModel")), generate_model(name="%sPydantic"%model_name, _inherit=None, _fields=model_yml_dict.get("_fields", {}))), {})
    setattr(sys.modules[__name__], dynamic_cls_name, cls_ref)
    pass
