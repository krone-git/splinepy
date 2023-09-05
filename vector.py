from collections.abc import Sized, Iterable
from itertools import combinations
from math import acos

from tensor import Tensor, TensorType


class Vector(Tensor):
    @classmethod
    def new_tensor(cls, width, height=None, elements=None, **kwargs):
        return cls(elements, dimension=height)

    @classmethod
    def axis(cls, index, dimension, scale=1):
        return cls.new(
            [1 if i == index else 0 for i in range(dimension)], dimension
        )
    @classmethod
    def empty(cls, dimension):
        return super().empty(1, dimension)
    @classmethod
    def fill(cls, dimension, fill):
        return super().fill(1, dimension, fill)

    def __init__(self, *elements, dimension=None, **kwargs):
        elements = elements[0] if isinstance(elements[0], Sized) \
            else tuple(elements[0]) if isinstance(elements[0], Iterable) \
            else tuple(elements.elements) if isinstance(elements, TensorType) \
            else [] if elements[0] is None else elements
        dimension = len(elements) if dimension is None else dimension
        super().__init__(
            1, height=dimension, elements=elements, **kwargs
        )
    @property
    def dimension(self): return self.height
    @property
    def magnitude(self):
        return sum(
            (i**2 for i in self._elements)
        )**0.5
    @property
    def unit(self): return self / self.magnitude
    @property
    def axial(self): 
        return len(
            [i for i in self._elements if i != 0]
        ) == 1
    @property
    def axis_angles(self):
        return (
            self.axis_angle(i) for i in range(self.dimension)
        )
    @property
    def plane_angles(self):
        return (
            self.plane_angle(i, j)
            for i, j in combinations(
                range(self.dimension), 2
            )
        )

    def cosine(self, other):
        return self.dot(other) / (self.magnitude * other.magnitude)
    def angle(self, other):
        return acos(
            self.cosine(other)
        )
    def axis_angle(self, axis):
        return self.angle(
            self.axis(axis)
        )
    def plane_angle(self, basis, orthogonal):
        plane_vector = self.empty(self.dimension)
        plane_vector[basis] = self[basis] 
        plane_vector[orthogonal] = self[orthogonal] 
        return plane_vector.angle(
            self.axis(basis)
        )
    
    def distance_vector(self, other):
        return other - self
    def distance(self, other):
        return self.distance_vector(other).magnitude

    def projection(self, other):
        return other.unit * self.dot(other.unit)
    def rejection(self, other):
        return self - self.projection(other)

    def dot(self, other):
        return sum(
            i * j for i, j in zip(self._elements, other._elements)
        )
    def triple_scalar(self, vector, other):
        return self.cross(vector).dot(other)

    def cross(self, other):
        if self.dimension == 2:
            return self[0] * other[1] - self[1] * other[0]
        elif self.dimension == 3:
            return self.new(
                [
                    self[1] * other[2] - self[2] * other[1],
                    self[2] * other[0] - self[0] * other[2],
                    self[0] * other[1] - self[1] * other[0]
                ], 
                dimension=self.dimension
            )

    def __getitem__(self, index): return self._elements[index]
    def __iter__(self): return iter(self._elements)