import sys
import redis_om
from .pydantic_generator import generate_model

import logging
_logger = logging.getLogger(__name__)

class OMRecord():
    def __init__(self, model_name):
        self.model_name = model_name
        self.cls_model = getattr(sys.modules[__name__], model_name)
        _logger.info("OMRecord -----------")
        _logger.info(self.cls_model)
        _logger.info(vars(self.cls_model))
        _logger.info("-0------- -----------")

    def __len__(self):
        return self.cls_model.find().count()

    async def list(self, offset=0, limit=60, sort_fields=None):
        return self.cls_model.find().page(offset, limit)

    async def get(self, pk):
        return self.cls_model.get(pk)
    
    async def create(self, data):
        new_record = self.cls_model(**data)
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
