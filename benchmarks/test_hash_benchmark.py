import pytest

from typing import FrozenSet, Tuple

from attr import attrs, attrib


@attrs(auto_attribs=True, frozen=True, slots=True, cache_hash=True, repr=True)
class Entity:
    mentions: FrozenSet[str] = attrib(converter=frozenset)


@attrs(auto_attribs=True, frozen=True, slots=True, hash=True, cache_hash=True)
class Cluster:
    prototype: Entity
    children: Tuple[Tuple["Cluster", float], ...]


@attrs(
    auto_attribs=True,
    frozen=True,
    slots=True,
    cmp=False,
    hash=True,
    cache_hash=True,
)
class HashShortCircuitEquality(Cluster):
    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        # noinspection PyArgumentList
        if (
            self._attrs_cached_hash is not None
            and other._attrs_cached_hash is not None
            and self._attrs_cached_hash != other._attrs_cached_hash
        ):
            return False

        return (
            self.prototype == other.prototype
            and self.children == other.children
        )


def check_equality(x, y):
    x == y


approaches = (("default", Cluster), ("hash", HashShortCircuitEquality))

inputs = (
    (('scourge' * 50,),
     [((('scourge' * 50,),
        [((('scream' * 50,), []), 7.335484504699707),
         ((('scourge' * 50,), []), 7.335484504699707)]),
       37.01687788963318),
      ((('scuz' * 50,),
        [((('scuz' * 50,),
           [((('scuz' * 50,),
              [((('scuz' * 50,), []), 7.436905860900879),
               ((('scuz' * 50,), []), 7.436905860900879)]),
             11.418097972869873),
            ((('sludge' * 50,), []), 11.418097972869873)]),
          11.36484432220459),
         ((('scuz' * 50,), []), 11.36484432220459)]),
       37.01687788963318)]),
    (('sleek' * 50,),
     [((('sleek' * 50,), []), 6.118027687072754),
      ((('sleek' * 50,), []), 6.118027687072754)]),
    (('rad' * 50,),
     [((('rad' * 50,),
        [((('rad' * 50,), []), 5.02443265914917),
         ((('rad' * 50,), []), 5.02443265914917)]),
       4.159373760223389),
      ((('rad' * 50,), []), 4.159373760223389)]),
    (('october' * 50,),
     [((('last month' * 50,),
        [((('last month' * 50,),
           [((('october' * 50,),
              [((('october' * 50,), []), -4.086095333099365),
               ((('october' * 50,), []), -4.086095333099365)]),
             -14.481067180633545),
            ((('last month' * 50,), []), -14.481067180633545)]),
          -17.800762176513672),
         ((('october' * 50,),
           [((('october' * 50,), []), -11.944441795349121),
            ((('october' * 50,), []), -11.944441795349121)]),
          -17.800762176513672)]),
       -12.85853385925293),
      ((('brockton bay' * 50,),
        [((('that awful city' * 50,), []), -6.8193039894104),
         ((('brockton bay' * 50,), []), -6.8193039894104)]),
       -12.85853385925293)]),
)

non_input = \
    (('october' * 50,),
     [((('last month' * 50,),
        [((('last month' * 50,),
           [((('october' * 50,),
              [((('october' * 50,), []), -4.086095333099365),
               ((('october' * 50,), []), -4.086095333099365)]),
             -14.481067180633545),
            ((('last month' * 50,), []), -14.481067180633545)]),
          -17.800762176513672),
         ((('october' * 50,),
           [((('october' * 50,), []), -11.944441795349121),
            ((('septober' * 50,), []), -11.944441795349121)]),
          -17.800762176513672)]),
       -12.85853385925293),
      ((('brockton bay' * 50,),
        [((('that awful city' * 50,), []), -6.8193039894104),
         ((('brockton bay' * 50,), []), -6.8193039894104)]),
       -12.85853385925293)])


def make_cluster_from_tuple_tree(clazz, tree) -> Cluster:
    prototype_mentions, raw_children = tree
    prototype = Entity(prototype_mentions)
    children = tuple(
        (make_cluster_from_tuple_tree(clazz, child), score)
        for child, score in raw_children
    )
    return clazz(prototype, children)


def clusterized(clazz, inputs):
    return tuple(make_cluster_from_tuple_tree(clazz, tree) for tree in inputs)


def get_input_identifier(input_) -> str:
    return input_[0][0][:10]


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("input_", inputs)
def test_self_equality(clazz, input_, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Equality hit ({get_input_identifier(input_)})"

    item = make_cluster_from_tuple_tree(clazz[1], input_)

    benchmark(check_equality, item, item)


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("input_", inputs)
def test_self_equality_prehashing(clazz, input_, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = (
        f"Equality hit with prehashing ({get_input_identifier(input_)})"
    )

    item = make_cluster_from_tuple_tree(clazz[1], input_)
    hash(item)

    benchmark(check_equality, item, item)


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("input_", inputs)
def test_equality_miss(clazz, input_, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Equality miss ({get_input_identifier(input_)})"

    item = make_cluster_from_tuple_tree(clazz[1], input_)
    other = make_cluster_from_tuple_tree(clazz[1], non_input)

    benchmark(check_equality, item, other)


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("input_", inputs)
def test_equality_miss_prehash(clazz, input_, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = (
        f"Equality miss with prehashing ({get_input_identifier(input_)})"
    )

    item = make_cluster_from_tuple_tree(clazz[1], input_)
    other = make_cluster_from_tuple_tree(clazz[1], non_input)
    hash(item)
    hash(other)

    benchmark(check_equality, item, other)
