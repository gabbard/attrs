import pytest

from attr import attrs, evolve


@attrs(auto_attribs=True, frozen=True, hash=True, cache_hash=True)
class DefaultEquality:
    a: str
    b: str



@attrs(auto_attribs=True, frozen=True, cmp=False, hash=True, cache_hash=True)
class HashShortCircuitEquality:
    a: str
    b: str

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        
        # if hash(other) != hash(self):
        #     return False
        if (
            self._attrs_cached_hash is not None
            and other._attrs_cached_hash is not None
            and self._attrs_cached_hash != other._attrs_cached_hash
        ):
            return False

        return self.a == other.a and self.b == other.b


def check_equality(x, y):
    x == y


approaches = (
    ("default", DefaultEquality),
    ("hash", HashShortCircuitEquality),
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
    unused = hash(item)

    benchmark(check_equality, item, item)


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("inputs", inputs)
def test_self_inequality(clazz, inputs, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Equality miss ({inputs[0]})"

    item = clazz[1](*inputs[1])
    # unused = hash(item)

    benchmark(check_equality, item, evolve(item, a="oedkk" * 300))


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("inputs", inputs)
def test_self_inequality_full_prehashing(clazz, inputs, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Equality miss with full prehashing ({inputs[0]})"

    item = clazz[1](*inputs[1])
    other = evolve(item, a="oedkk" * 300)
    unused = hash(item)
    unused = hash(other)

    benchmark(check_equality, item, other)


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("inputs", inputs)
def test_self_similar_inequality(clazz, inputs, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Equality near miss ({inputs[0]})"

    item = clazz[1](*inputs[1])
    item_modified = evolve(item, a=item.a + "hello" * 300)
    unused = hash(item_modified)

    benchmark(check_equality, item_modified, evolve(item, a=item.a + "oedkk" * 300))


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("inputs", inputs)
def test_self_similar_inequality_full_prehashing(clazz, inputs, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Equality near miss with full prehashing ({inputs[0]})"

    item = clazz[1](*inputs[1])
    item = evolve(item, a=item.a + "hello" * 300)
    other = evolve(item, a=item.a + "oedkk" * 300)
    unused1 = hash(item)
    unused2 = hash(other)

    benchmark(check_equality, item, other)


def containment_check(item, collection):
    item in collection

# My big added test
components = (
    (
        ("hi" * 10000, "lo" * 10000),
        ("hi" * 10000, "lo" * 5000 + "fi" * 5000),
        ("hi" * 10000, "lofi" * 5000),
        ("hi" * 10000, "bye" * 10000),
        ("hi" * 10000, "yes" * 10000),
        ("hi" * 10000, "no" * 10000),
        ("hi" * 10000, "bruiser" * 10000),
        ("hi" * 10000, "breaker" * 1000),
        ("hi" * 10000, "brute" * 10000),
        ("hi" * 10000, "shaker" * 10000),
    ),
)

@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("components", components)
def test_pair_set_membership_hit(clazz, components, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Class pair set membership hit"

    classified = [clazz[1](*component) for component in components]
    pairs = {
        (component1, component2)
        for idx, component1 in enumerate(classified)
        for component2 in classified[idx+1:]
    }
    assert all(vtx._attrs_cached_hash is not None for vtx in classified)

    def big_check(classified, pairs):
        for idx, component1 in enumerate(classified):
            for component2 in classified[idx+1:]:
                (component1, component2) in pairs
    benchmark(big_check, classified, pairs)
    

@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("components", components)
def test_pair_set_membership_miss(clazz, components, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Class pair set membership miss"

    classified = [clazz[1](*component) for component in components]
    pairs = {
        (component1, component2)
        for idx, component1 in enumerate(classified)
        for component2 in classified[idx+1:]
    }
    assert all(vtx._attrs_cached_hash is not None for vtx in classified)

    def big_check(classified, pairs):
        for idx, component2 in enumerate(classified):
            for component1 in classified[idx+1:]:
                (component1, component2) in pairs
    benchmark(big_check, classified, pairs)