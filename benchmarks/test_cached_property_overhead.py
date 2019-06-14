import cached_property
import pytest


class UseCachedProperty:
    @cached_property.cached_property
    def val(self):
        return "foo"


class Derived:
    def __init__(self):
        self.val = "foo"


class DerivedSlots:
    __slots__ = ("val",)

    def __init__(self):
        self.val = "foo"


objs_to_test = [UseCachedProperty(), Derived(), DerivedSlots()]


def access(obj):
    obj.val


@pytest.mark.parametrize("obj", objs_to_test)
def test_set_membership_miss(obj, benchmark):
    benchmark.name = obj.__class__.__name__

    benchmark(access, obj)
