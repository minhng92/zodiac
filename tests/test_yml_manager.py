from zodiac.libcore.base.yml_manager import YmlManager
from hypothesis import example, given, strategies as st

# https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.dictionaries
@given(st.dictionaries(keys=st.sampled_from(["zodiac", "stock"]), values=st.sampled_from([{"a": 1, "b": 2}, {"c": 3, "d": 4}])))
def test_yml_manager_get_flatten_dict_1(data_dict):
    yml_manager = YmlManager(False)
    yml_manager.data_dict = data_dict
    result = yml_manager.get_flatten_dict()    
    data_keys = list(data_dict.keys())
    for k, v in result.items():     # "zodiac.a", 1
        assert k.count(".") > 0
        assert len(k.split(".")) == 2
        assert k.split(".")[0] in data_keys
        pass
    pass

# https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.dictionaries
@given(st.dictionaries(keys=st.sampled_from(["zodiac"]), values=st.sampled_from([{"a": {"x": 10, "y": 20}, "b": {"m": 30, "n": 40}}])))
def test_yml_manager_get_flatten_dict_2(data_dict):
    yml_manager = YmlManager(False)
    yml_manager.data_dict = data_dict
    result = yml_manager.get_flatten_dict()
    for k, v in result.items():     # "zodiac.a", 1
        assert k.count(".") > 0
        assert len(k.split(".")) == 3
        pass
    pass
