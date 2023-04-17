import os
import sys
import pydantic
import redis_om
from typing import Optional
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

def main():
    customer = generate_pydantic_model(
        name="Customer",
        attrs=["a", "b", "c"]
    )
    _logger.info("Customer class: %s", str(customer))
    # _logger.info("customer.__classes__: %s", str(customer.__classes__))

    # Before running queries, we need to run migrations to set up the
    # indexes that Redis OM will use. You can also use the `migrate`
    # CLI tool for this!
    redis_om.Migrator().run()

    pass

if __name__ == "__main__":
    main()
