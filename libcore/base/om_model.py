import sys
import json
import redis_om
from .pydantic_generator import generate_model

import logging
_logger = logging.getLogger(__name__)

class OMRecordSet(object):
    def __init__(self, obj):
        print("Init OMRecordSet", obj)
        if not isinstance(obj, (list, tuple)):
            self.items = [obj,]
        else:
            self.items = obj

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self.items, attr)
    
    def json(self):
        return json.dumps([x.__dict__ for x in self.items])

    async def update(self, data):
        # can optimize if do it in pipeline!?
        for item in self.items:
            item.update(**data)
            item.save()
        pass
    
    async def delete(self):
        print("self.items", self.items)
        for item in self.items:
            print("item", item)
            item.delete(item.key())
            item.save()
            pass
        pass

class OMModel():
    def __init__(self, model_name):
        self.model_name = model_name
        self.cls_model = getattr(sys.modules[__name__], model_name)
        _logger.info("OMModel -----------")
        _logger.info(self.cls_model)
        _logger.info(vars(self.cls_model))
        _logger.info("-0------- -----------")

    def __len__(self):
        return self.cls_model.find().count()

    async def list(self, offset=0, limit=60, sort_fields=None):
        return OMRecordSet(self.cls_model.find().page(offset, limit))

    async def get(self, pk):
        return OMRecordSet(self.cls_model.get(pk))
    
    async def create(self, data):
        new_record = self.cls_model(**data)
        new_record.save()
        return OMRecordSet(new_record)

def register_om_model(model_name, model_yml_dict):
    """
        model_name: res_partner, stock_code
    """
    dynamic_cls_name = model_name
    conf_cls_name = model_yml_dict.get("_inherit", "JsonModel")
    cls_ref = type(model_name, (getattr(redis_om, conf_cls_name), generate_model(name="%sPydantic"%model_name, _inherit=None, _fields=model_yml_dict.get("_fields", {}))), {})
    setattr(sys.modules[__name__], dynamic_cls_name, cls_ref)
    pass
