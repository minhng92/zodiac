import sys
import redis_om
from .pydantic_generator import generate_model

import logging
_logger = logging.getLogger(__name__)
# _logger.setLevel(logging.DEBUG)

gen_cls = generate_model(name="PosOrderDynamic", _inherit=None, _fields={
    "product": "type=str required=True index=True",
    "qty": "type=float required=False index=True",
    "price_unit": "type=float required=False index=True",
    "total_amount": "type=float required=False index=True",
})

class PosOrder(redis_om.JsonModel, gen_cls):
    pass

def main():
    dynamic_cls_name = "PosOrder2"
    posorder2 = type("PosOrder2", (redis_om.JsonModel, generate_model(name="PosOrderDynamic", _inherit=None, _fields={
        "product2": "type=str required=True index=True",
        "qty2": "type=float required=False index=True",
        "price_unit2": "type=float required=False index=True",
        "total_amount2": "type=float required=False index=True",
    })), {})
    setattr(sys.modules[__name__], dynamic_cls_name, posorder2)
    pass

main()
