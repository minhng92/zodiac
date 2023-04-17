import os
import sys
import re
import pydantic
import redis_om
from typing import Optional
from omegaconf import OmegaConf
from aredis_om.model.model import model_registry

import logging
_logger = logging.getLogger(__name__)
# _logger.setLevel(logging.DEBUG)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s@%(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

redis = redis_om.get_redis_connection(url=os.getenv("REDIS_OM_URL", "redis://@redis_stack:6380")) # "redis://your-username:your-password@localhost:6379"

os.environ["REDIS_OM_URL"] = "redis://@redis_stack:6380"

# Meta = type('Meta', (object, ), {'index_name': 'abc', 'database': redis})

# class Meta(redis_om.ModelMeta):
#     database = redis

FIELD_ATTRIBUTES = {
    "type": str,
    "required": bool,
    "index": bool
}

def get_fval(fkey, attr_val):
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

def generate_pydantic_model(name, attrs, attr_type=Optional[float], attr_val=redis_om.Field(index=True)):
    attr_dict = {}
    for attr_name in attrs:
        if attr_val is None:
            attr_dict[attr_name] = (attr_type, ...)
        else:
            attr_dict[attr_name] = (attr_type, attr_val)
    result = pydantic.create_model(
        name, 
        **attr_dict,
        __base__=redis_om.JsonModel
    )
    # setattr(result, "_meta", Meta)
    return result

def generate_model(name, _inherit=None, _fields={}):
    attr_dict = {}
    print("generate_model(%s, %s, %s)" % (name, str(_inherit), str(_fields)))
    for attr_name, attr_val in _fields.items():
        if not attr_val:
            attr_dict[attr_name] = (str, ...)
        else: # type=str required=True index=True
            fattr = {}
            for fkey, ftype in FIELD_ATTRIBUTES.items():
                fval = get_fval(fkey, attr_val)
                if fval:
                    if ftype is str:
                        fval = str(fval)
                    elif ftype is float:
                        fval = float(fval)
                    elif ftype is bool:
                        fval = eval(fval.lower().title())   # True / False
                fattr[fkey] = fval
                print("- ", attr_name, fkey, str(fval))
            
            print("fattr", fattr)

            attr_type = eval(fattr.get("type", "str"))
            attr_field = redis_om.Field(index=fattr.get("index", True))
            attr_dict[attr_name] = (attr_type, attr_field)

            print("attr_dict", attr_dict)
    # return pydantic.create_model(
    #     name, 
    #     **attr_dict,
    #     __base__=eval(_inherit)
    # )
    return pydantic.create_model(
        name, 
        **attr_dict
    )

gen_cls = generate_model(name="CustomerDynamic", _inherit="object", _fields={
    "name": "type=str required=True index=True",
    "age": "type=float required=False index=True",
    # "is_male": "type=bool required=True index=True default=True",
})

class Customer3(redis_om.JsonModel, gen_cls):
    pass

def main():
    model_config = OmegaConf.load("models.yml")
    _logger.info("model_config: %s", str(model_config))

    models = {}
    for model_name in model_config.keys():
        models[model_name] = type("%s123"%model_name, (redis_om.JsonModel, generate_model(
            name=model_name,
            **model_config[model_name]
        )), {})

        setattr(sys.modules[__name__], model_name, models[model_name])  # add class to current module
        # globals()[model_name] = models[model_name]
        print(models[model_name], dir(models[model_name]))
        # models[model_name].__new__(models[model_name])

        # register new class
        model_registry["%s123"%model_name] = models[model_name]
        print("Register model registry")
        print("model_registry", model_registry)

    # customer = generate_pydantic_model(
    #     name="Customer",
    #     attrs=["a", "b", "c"]
    # )
    # _logger.info("Customer class: %s", str(customer))
    # _logger.info("customer.__classes__: %s", str(customer.__classes__))

    print("sys.modules[__name__]", sys.modules[__name__])

    print("models", models)

    customer = models["Customer"]
    andrew = customer(
        name="Minh",
        age=31,
        is_male=True,
    )

    # Before running queries, we need to run migrations to set up the
    # indexes that Redis OM will use. You can also use the `migrate`
    # CLI tool for this!
    redis_om.Migrator().run()
    
    

    print(andrew.pk)
    x = andrew.save()
    print("x", x)

    result = customer.find(customer.name == "Minh").all()
    print(result)

    # result2 = customer.find(customer.age == 10).all()
    # print(result2)

    # peter = Customer3(name="hai", age=33)
    # print("peter.pk", peter.pk)
    # print(peter.save())
    # result = Customer3.find(Customer3.name == "hai").all()
    # print("Customer3: ", result)
    pass

if __name__ == "__main__":
    main()

    # print("__module__", __module__)
    # print("sys.modules", sys.modules)
    # print("sys.modules[__name__]", sys.modules[__name__])
