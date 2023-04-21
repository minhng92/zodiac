import sys
import redis_om
import libcore.om.om_model
from libcore.om.om_model import PosOrder

import redis

import logging
_logger = logging.getLogger(__name__)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s@%(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def main():
    user_connection = redis.Redis(host='redis_stack', port=6380, decode_responses=True)
    libcore.om.om_model.PosOrder2._db = user_connection

    # Before running queries, we need to run migrations to set up the
    # indexes that Redis OM will use. You can also use the `migrate`
    # CLI tool for this!
    redis_om.Migrator().run()

    print(dir(sys.modules["libcore"]))
    print("path, om", sys.modules["libcore"].__path__, sys.modules["libcore"].om)
    print("dir om", dir(sys.modules["libcore"].om))
    print("dir om om_model", dir(sys.modules["libcore"].om.om_model))
    # raise Exception()

    # pos_order = PosOrder(
    #     product="Water",
    #     qty=2,
    #     price_unit=10,
    #     total_amount=2*10,
    # )
    # pos_order.save()
    # _logger.info(pos_order.key())

    pos_order2 = libcore.om.om_model.PosOrder2(
        product2="Cake",
        qty2=3,
        price_unit2=15,
        total_amount2=3*15,
    )
    pos_order2.save()
    _logger.info(pos_order2.key())

    # res = PosOrder.find(PosOrder.qty > 0).all()
    # print(res)
    
    res2 = libcore.om.om_model.PosOrder2.find(libcore.om.om_model.PosOrder2.qty2 > 3).all()
    print("res2 (n=%d):" % len(res2), res2)
    pass

if __name__ == "__main__":
    main()
    print("Done om2.py")
