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


@attrs(auto_attribs=True, frozen=True, slots=True, cmp=False, hash=True, cache_hash=True)
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
                self.prototype == other.prototype and
                self.children == other.children
        )


def check_equality(x, y):
    x == y


def check_list_removal(xs, x):
    listified = list(xs)
    listified.remove(x)


approaches = (
    ("default", Cluster),
    ("hash", HashShortCircuitEquality),
)

inputs = (
    (
        (('doggo' * 50,), []),
        (('fried rice' * 50,), []),
        (('we go' * 50,), []),
        (('no' * 50,), []),
        (('stop' * 50,), []),
        (('rusty' * 50,), []),
        (('november' * 50,), []),
        (('railcar' * 50,), []),
        (('husk' * 50,), []),
        (('strider' * 50,), []),
        (('affine' * 50,), []),
        (('stranglehold' * 50,), []),
        (('cried' * 50,), []),
        (('furtive' * 50,), []),
        (('stern' * 50,), []),
        (('ape' * 50,), []),
        (('orange' * 50,), []),
        (('thirty' * 50,), []),
        (('fate' * 50,), []),
        (('stay' * 50,), []),
        (('burgeon' * 50,), []),
        (('hauberk' * 50,), []),
        (('placid' * 50,), []),
        (('remonstrance' * 50,), []),
        (('remorse' * 50,), []),
        (('atone' * 50,), []),
        (('banish' * 50,), []),
        (('repent' * 50,), []),
        (('scorn' * 50,), []),
        (('bees' * 50,), []),
        (('fikas' * 50,), []),
        (('tree' * 50,), []),
        (('school' * 50,), []),
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
         [((('sleek' * 50,), []), 6.118027687072754), ((('sleek' * 50,), []), 6.118027687072754)]),
        (('rad' * 50,),
         [((('rad' * 50,),
            [((('rad' * 50,), []), 5.02443265914917), ((('rad' * 50,), []), 5.02443265914917)]),
           4.159373760223389),
          ((('rad' * 50,), []), 4.159373760223389)]),
        (('hat' * 50,),
         [((('bowler hat' * 50,), []), -4.103216171264648),
          ((('hat' * 50,), []), -4.103216171264648)]),
        (('sprain' * 50,),
         [((('sprain' * 50,), []), -6.791292190551758),
          ((('sprain' * 50,), []), -6.791292190551758)]),
        (('soup' * 50,),
         [((('soup' * 50,), []), -10.618362426757812),
          ((('soup' * 50,), []), -10.618362426757812)]),
        (('neighbor' * 50,),
         [((('goblin' * 50,), []), -14.500961303710938),
          ((('neighbor' * 50,), []), -14.500961303710938)]),
        (('singer' * 50,),
         [((('singer' * 50,), []), -16.82286262512207),
          ((('singer' * 50,), []), -16.82286262512207)]),
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
        (('clyde' * 50,),
         [((('clyde' * 50,), []), -22.940263748168945),
          ((('clemson' * 50,), []), -22.940263748168945)]),
    ),
)


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


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("inputs", inputs)
def test_self_equality(clazz, inputs, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Collection equality hit"

    item = clusterized(clazz[1], inputs)
    hash(item)

    benchmark(check_equality, item, item)


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("inputs", inputs)
def test_equality_miss(clazz, inputs, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Collection equality miss"

    item = clusterized(clazz[1], inputs)
    other = item + (item[2],)
    item = item + (item[0],)

    benchmark(check_equality, item, other)


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("inputs", inputs)
def test_equality_miss_prehash(clazz, inputs, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"Collection equality miss with prehashing"

    item = clusterized(clazz[1], inputs)
    other = item + (item[2],)
    item = item + (item[0],)
    hash(item)
    hash(other)

    benchmark(check_equality, item, other)


@pytest.mark.parametrize("clazz", approaches)
@pytest.mark.parametrize("inputs", inputs)
def test_list_removal(clazz, inputs, benchmark):
    benchmark.name = clazz[0]
    benchmark.group = f"List removal"

    item = clusterized(clazz[1], inputs)
    hash(item)

    benchmark(check_list_removal, item, item[-1])
