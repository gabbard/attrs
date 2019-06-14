import pytest

from attr import attrs, evolve


@attrs(auto_attribs=True, hash=True)
class DefaultEquality:
    a: int
    b: int


@attrs(auto_attribs=True, cmp=False, hash=True)
class IdentityShortCircuitEquality:
    a: int
    b: int

    def __eq__(self, other):
        if other is self:
            return True

        if self.__class__ != other.__class__:
            return False

        return self.a == other.a and self.b == other.b


@attrs(auto_attribs=True, cmp=False, hash=True, cache_hash=True)
class HashShortCircuitEquality:
    a: int
    b: int

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        if (
            self._attrs_cached_hash is not None
            and other._attrs_cached_hash is not None
        ):
            if self._attrs_cached_hash != other._attrs_cached_hash:
                return False

        return self.a == other.a and self.b == other.b


@attrs(auto_attribs=True, cmp=False, hash=True)
class BothShortCircuitEquality:
    a: int
    b: int

    def __eq__(self, other):
        if other is self:
            return True

        if self.__class__ != other.__class__:
            return False

        if hash(other) != hash(self):
            return False

        return self.a == other.a and self.b == other.b


def check_equality(x, y):
    x == y


approaches = (
    ("default", DefaultEquality),
    ("identity", IdentityShortCircuitEquality),
    ("hash", HashShortCircuitEquality),
    ("both", BothShortCircuitEquality),
)

inputs = (
    ("small", ("hello", "world")),
    ("big", ("hello" * 10000, "world" * 10000)),
)


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("inputs", inputs)
def test_self_equality(clazz, inputs, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Equality hit ({inputs[0]})"

    item = clazz[1](*inputs[1])

    benchmark(check_equality, item, item)


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("inputs", inputs)
def test_self_inequality(clazz, inputs, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Equality miss ({inputs[0]})"

    item = clazz[1](*inputs[1])

    benchmark(check_equality, item, evolve(item, a="oedkk" * 300))


def containment_check(item, collection):
    item in collection


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("inputs", inputs)
def test_set_membership_hit(clazz, inputs, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Set membership hit ({inputs[0]})"

    item = clazz[1](*inputs[1])

    set_containing = {"ljdjpje", 123, frozenset([1, 2, 3, 4]), item}

    benchmark(containment_check, item, set_containing)


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("inputs", inputs)
def test_set_membership_miss(clazz, inputs, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Set membership miss ({inputs[0]})"

    item = clazz[1](*inputs[1])

    set_not_containing = {"ljdjpje", 123, frozenset([1, 2, 3, 4])}

    benchmark(containment_check, item, set_not_containing)
