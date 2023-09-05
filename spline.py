from collections.abc import Iterable
from abc import ABC, abstractmethod

from vector import Vector
from matrix import Matrix


class ControlPoint:
    def __init__(self, position, lead, trail=None):
        self._position = position if isinstance(position, Vector) \
            else Vector(position)
        self._lead_direction = lead if isinstance(lead, Vector) \
                and lead.dimension == position.dimension \
            else Vector(lead, dimension=position.dimension)
        self._trail_direction = self._lead_direction if trail is None \
            else trail if isinstance(trail, Vector) \
                and trail.dimension == position.dimension \
            else Vector(trail, dimension=position.dimension)

    @property
    def position(self): return self._position
    @property
    def lead_direction(self): return self._lead_direction
    @property
    def trail_direction(self): return self._trail_direction
    @property
    def continuous(self): 
        return self._lead_direction == self._trail_direction

    def __eq__(self, other):
        return self._position == other._position \
            and self._lead_direction == other._lead_direction \
            and self._trail_direction == other._trail_direction


class Spline(ABC):
    def __init__(self, points=None):
        self._points = points if isinstance(points, list) \
            else list(points) if isinstance(points, Iterable) \
            else [points] if points \
            else []
    
    @property
    def open(self): 
        return self.head != self.tail \
            or len(self._points) < 2
    @property
    def closed(self): return not self.open
    @property
    def points(self): return tuple(self._points)
    @property
    def size(self): return len(self._points)
    @property
    def head(self): return self._points[0]
    @property
    def tail(self): return self._points[-1]
    @property
    def empty(self): return self.size == 0
    @property
    def interpolatable(self): return self.size > 1

    def point(self, point): return self._points[point]
    def index(self, point): return self._points.indeX(point)

    def leading(self, point):
        index = self.index(point) if isinstance(point, ControlPoint) \
            else point % self.size
        return self.point(index - 1) if index > 0 else None
    def trailing(self, point):
        index = self.index(point) if isinstance(point, ControlPoint) \
            else point % self.size
        return self.point(index + 1) if index < self.size - 1 else None
    def adjacent(self, point):
        return (
            self.leading(point), self.trailing(point)
        )
    def insertable(self, index, point):
        return self.leading(index) != point and self.trailing(index) != point
    
    def set_point(self, index, point):
        if self.insertable(index, point):
            self._points[index] = point
        return self
    def add_point(self, point, index=-1):
        self._points.insert(index, point) if self.insertable(index, point) \
            else None
        return self

    def remove_point(self, point):
        self._points.remove(point) if isinstance(point, ControlPoint) \
            else self._points.pop(point)
        return self

    @abstractmethod
    def interpolate(self, start=None, stop=None, resolution=None):
        raise NotImplementedError

    def __iadd__(self, point):
        [self.add_point(i) for i in point] if isinstance(point, Iterable) \
            else self.add_point(point)
    def __isub__(self, point):
        [self.remove_point(i) for i in point] if isinstance(point, Iterable) \
            else self.add_point(point)

    def __getitem__(self, index): return self.points(index)
    def __setitem__(self, index, point): self.set_point(index, point)
    def __contains__(self, other): return other in self._points
    def __iter__(self): return iter(self._points)
    def __reversed__(self): 
        return reversed(
            iter(self)
        )


class CubicSpline(Spline):
    def interpolation(self):
        raise NotImplementedError