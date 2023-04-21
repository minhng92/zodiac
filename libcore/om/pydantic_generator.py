import pydantic
import redis_om

import logging
_logger = logging.getLogger(__name__)

FIELD_ATTRIBUTES = {
    "type": str,
    "required": bool,
    "index": bool
}

def parse_field_value(fkey, attr_val):
    """
        attr_val: type=str required=True index=True
    """
    result = False
    kv = attr_val.split("%s="%fkey, 2)
    if kv:
        v_contains_fval = kv[1]
        if v_contains_fval.startswith('"'):
            result = v_contains_fval.split('" ')[0]
        elif v_contains_fval.startswith("'"):
            result = v_contains_fval.split("' ")[0]
        else:
            result = v_contains_fval.split(" ")[0]
    return result
    pass

def generate_model(name, _inherit=None, _fields={}):
    attr_dict = {}
    # print("generate_model(%s, %s, %s)" % (name, str(_inherit), str(_fields)))
    for attr_name, attr_val in _fields.items():
        if not attr_val:
            attr_dict[attr_name] = (str, ...)
        else: # type=str required=True index=True
            fattr = {}
            for fkey, ftype in FIELD_ATTRIBUTES.items():
                fval = parse_field_value(fkey, attr_val)
                if fval:
                    if ftype is str:
                        fval = str(fval)
                    elif ftype is float:
                        fval = float(fval)
                    elif ftype is bool:
                        fval = eval(fval.lower().title())   # True / False
                fattr[fkey] = fval
                # print("- ", attr_name, fkey, str(fval))
            
            # print("fattr", fattr)

            attr_type = eval(fattr.get("type", "str"))
            attr_field = redis_om.Field(index=fattr.get("index", True))
            attr_dict[attr_name] = (attr_type, attr_field)

            # print("attr_dict", attr_dict)
    if _inherit:
        return pydantic.create_model(
            name, 
            **attr_dict,
            __base__=eval(_inherit)
        )
    else:
        return pydantic.create_model(
            name, 
            **attr_dict
        )
