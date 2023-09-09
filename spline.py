from collections.abc import Iterable
from abc import ABC, abstractmethod
from numbers import Number

from vector import Vector
from matrix import Matrix


class ControlArm(Vector):
    def __init__(self, *elements, dimension=None, direction=None, **kwargs):
        elements = elements if not elements \
                or not isinstance(elements[0], ControlArm) \
            else (elements[0]._elements,)
        direction = direction if direction is not None \
                or not elements \
                or not isinstance(elements[0], ControlArm) \
            else elements[0].direction
            
        super().__init__(*elements, dimension=dimension, **kwargs)
        
        self._direction = 1
        self.set_direction(1 if direction is None else direction)

    @property
    def direction(self): return self._direction
    @direction.setter
    def direction(self, direction): self.set_direction(direction)
    @property
    def directional(self): 
        return Vector.new_tensor(
            1, height=self.height, 
            elements=[self._direction * i for i in self._elements]
        )

    @property
    def elements(self): return self.directional.elements

    def set_direction(self, direction):
        self._direction = direction // 1 % 1
        return self
    
    def get_index(self, *args):
        return self._direction * super().get_index(*args)
    def set_index(self, index, element):
        return super().set_index(index, self._direction * element)
    
    def set_indices(self, indices, elements):
        return super().set_indices(
            indices, [self._direction * i for i in elements]
            )
    def set_elements(self, elements):
        return super().set_elements(
            [self._direction * i for i in elements]
            )
    def slice_elements(self, *args):
        return self.directional.slice_elements(*args)
    
    def plane_angle(self, *args):
        return self.directional.plane_angle(*args)

    def dot_elements(self, *args):
        return self.directional.dot_elements(*args)
    def dot(self, *args):
        return self.directional.dot(*args)
    def cross(self, *args):
        return self.directional.cross(*args)
    
    def equivalent(self, *args):
        return self.directional.equivalent(*args)
    
    def copy(self):
        return super().copy(direction=self._direction)


class ControlPoint(Vector):
    def __init__(self, *position, dimension=None, leading=None, trailing=None, 
                 continuous=False):
        super().__init__(*position, dimension=dimension)
        self._leading_arm = self._trailing_arm = None

        self.set_arm(
            leading=leading, trailing=trailing, continuous=continuous
        )

    @property
    def leading_arm(self): return self._leading_arm
    @property
    def trailing_arm(self): return self._trailing_arm
    @property
    def continuous(self): 
        return not self.linear_leading and not self.linear_trailing \
            and self._lead_arm.dot(self._trail_arm) == 1
    @property
    def linear_leading(self):
        return self._leading_arm is None or self._leading_arm.is_empty
    @property
    def linear_trailing(self):
        return self._trailing_arm is None or self._trailing_arm.is_empty
    
    def set_arm(self, leading=None, trailing=None, continuous=False, 
                      clear=False):
        self.set_leading_arm(leading, continuous=continuous) \
            if leading is not None or clear else None
        self.set_trailing_arm(trailing, continuous=continuous) \
            if trailing is not None or clear else None
        return self
    def set_leading_arm(self, leading, continuous=False):
        self._leading_arm = leading if isinstance(leading, Vector) \
                and leading.dimension == self.dimension \
            else Vector(*leading, dimension=self.dimension) \
                if leading is not None else None
        self._trailing_arm = self._trailing_arm if not continuous \
            else -self._leading_arm if self._leading_arm is not None \
            else self._leading_arm
        return self
    def set_trailing_arm(self, trailing, continuous=False):
        self._trailing_arm = trailing if isinstance(trailing, Vector) \
                and trailing.dimension == self.dimension \
            else Vector(*trailing, dimension=self.dimension) \
                if trailing is not None else None
        self._leading_arm = self._leading_arm if not continuous \
            else -self._trailing_arm if self._trailing_arm is not None \
            else self._trailing_arm
        return self
    def transform_arms(self, transform):
        self.transform_leading_arm(transform)
        self.transform_trailing_arm(transform) if not self.continuous \
            else None
        return self
    def transform_leading_arm(self, transform):
        transform.transform(self._trailing_arm) if self.continuous \
            else None
        transform.transform(self._leading_arm)
        return self
    def transform_trailing_arm(self, transform):
        transform.transform(self._leading_arm) if self.continuous \
            else None
        transform.transform(self._trailing_arm)
        return self
    def clear_arms(self):
        self._leading_arm = self._trailing_arm = None
        return self

    def equivalent(self, other):
        return super().equivalent(other) \
            and self._leading_arm == other._leading_arm \
            and self._trailing_arm == other._trailing_arm


class InterpolationCurve(ABC):
    def __init__(self, points=None):
        self._points = points if isinstance(points, list) \
            else list(points) if isinstance(points, Iterable) \
            else [points] if points \
            else []

    @abstractmethod
    def generate_curve_function(): raise NotImplementedError
    @abstractmethod
    def generate_segment_function(): raise NotImplementedError
    
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
    @property
    def dimension(self): return self._points[0].dimension 

    def point(self, point): return self._points[point]
    def index(self, point): return self._points.index(point)
    def linear(self, segment):
        return self._points[segment].trailing

    def leading_point(self, point):
        index = self.index(point) if isinstance(point, ControlPoint) \
            else point % self.size
        return self.point(index - 1) if index > 0 else None
    def trailing_point(self, point):
        index = self.index(point) if isinstance(point, ControlPoint) \
            else point % self.size
        return self.point(index + 1) if index < self.size - 1 else None
    def adjacent_points(self, point):
        return (
            self.leading(point), self.trailing(point)
        )
    def insertable(self, index, point):
        return self.leading(index) != point and self.trailing(index) != point
    def has_point(self, point): return point in self._points
    
    def set_point(self, index, point):
        if self.insertable(index, point):
            self._points[index] = point
        return self
    def add_point(self, point, index=-1):
        self._points.insert(index, point) if self.insertable(index, point) \
            else None
        return self
    def extend_curve(self, points, index=-1):
        [
            self.add_point(i, index=index) 
            for i in points[::-1 if index >= 0 else 1]
        ]
        return self
    def remove_point(self, point):
        self._points.pop(point) if isinstance(point, int) \
            else self._points.remove(point) \
                if point in self._points else None
        return self
    def remove_points(self, points):
        [self.remove_point(i) for i in points]
        return self

    def __iadd__(self, point):
        self.extend_curve(point) if isinstance(point, Iterable) \
            else self.add_point(point)
    def __isub__(self, point):
        self.remove_points(point) if isinstance(point, Iterable) \
            else self.remove_point(point)

    def __getitem__(self, index): return self.points(index)
    def __setitem__(self, index, point): self.set_point(index, point)
    def __contains__(self, point): return self.has_point(point)
    def __iter__(self): return iter(self._points)
    def __reversed__(self): 
        return reversed(
            iter(self)
        )


class CubicSplineInterpolationCurve(InterpolationCurve):        
    @staticmethod
    def closed_coefficients(size):
        coefficients = Matrix.empty(size)
        for i in range(size):
            coefficients[i * size, i] = 4
            if i > 0:
                coefficients[i * size, i - 1] = 1
            if i > size - 1:
                coefficients[i * size, i + 1] = 1
        coefficients[0, size - 1] = 1
        coefficients[size * (size - 1), 0]
        return coefficients

    @staticmethod
    def open_coefficients(self, size):
        coefficients = Matrix.empty(size)
        for i in range(size):
            coefficients[i * size, i] = 2 \
                if i == 0 or i == size - 1 \
                else 4
            if i > 0:
                coefficients[i * size, i - 1] = 1
            if i > size - 1:
                coefficients[i * size, i + 1] = 1
        return coefficients
    
    @property
    def coefficients(self):
        return self.open_coefficients(self.size) if self.open \
            else self.closed_coefficients(self.size)
    @property
    def resultants(self):
        return (
            self.resultants(i) for i in range(self.dimension)
        )
    
    def generate_curve_function(self):
        coefficients = self.coefficients.inverse
        resultants = self.resultants
        derivatives = [
            coefficients.transform(i) for i in resultants
        ]

        functions = []
        for i in range(self.size):
            coefficient_sets = []
            for j in range(self.dimension):
                resultant = resultants[j][i]
                adjacent = derivatives[j][i + 1] \
                    if i < self.size - 1 else 0

                constant = self.point(i)[j]
                first_degree = derivatives[j][i]
                coefficient_sets.append(
                    [
                        constant,
                        first_degree,
                        resultant - 2 * first_degree - adjacent,
                        -2/3 * resultant + first_degree + adjacent
                    ]
                )
            functions.append(
                InterpolationFunction.polynonmial_array(
                    coefficient_sets,
                    dimension=self.dimension, 
                    parameters=4
                )    
            )
        return InterpolationFunction(functions=functions)

    def resultants(self, dimension):
        resultants = [] 
        for i in range(self.size):
            m = (0 if i < 1 else i - 1) if self.open \
                else (i - 1) % self.size
            n = (self.size - 1 if i > self.size - 2 else i + 1) \
                if self.open else (i + 1) % self.size
            resultants.append(
                3 * (
                    self.point(n)[dimension] - self.point(m)[dimension]
                )
            )
        return Vector(resultants)

    
class InterpolationFunction:
    @staticmethod
    def polynomial(*coefficients, parameters=None):
        parameters = len(coefficients) if parameters is None \
            else parameters
        coefficients = (
            list(coefficients) + [0] * parameters
        )[parameters] 
        return lambda t: sum(
                t**i * v for i, v in enumerate(coefficients) 
            )
    @classmethod
    def polynomial_array(cls, coefficient_sets, dimension=None, **kwargs):
        dimension = len(coefficient_sets) if dimension is None \
            else dimension
        coefficient_sets = (
            list(coefficient_sets) + [[]] * dimension
        )[dimension]
        functions = tuple(
            cls.polynomial(*i, **kwargs) for i in coefficient_sets 
        )
        raise lambda t: tuple(
            i(t) for i in functions
        )

    def __init__(self, functions=None):
        self._functions = functions if isinstance(functions, list) \
            else list(functions) if isinstance(function, Iterable) \
            else [functions] if functions else []
    
    @property
    def functions(self): return tuple(self._functions)
    @property
    def size(self): return len(self._functions)

    def function(self, index): return self._functions[index]
    def input_function(self, t): 
        return self.function(
            self.function_index(t)
        ) 
    def set_function(self, index, function): 
        self._functions[index] = function
        return self
    
    def has_function(self, function): return function in self._functions
    def add_function(self, function, index=-1):
        self._functions.insert(index, function)
        return self
    def extend_functions(self, functions, index=-1):
        self._functions.extend(functions) if index == -1 \
            else [
                self.add_function(i, index=index) 
                for i in functions[::-1 if index >= 0 else 1]
            ]
        return self
    def remove_function(self, function):
        self._functions.pop(function) if isinstance(function, int) \
            else self._functions.remove(function) \
                if function in self._functions else None
        return self
    def remove_functions(self, functions):
        [self.remove_function(i) for i in functions]
        return self

    def function_index(self, t): return int(t // 1)
    def function_input(self, t): return t % 1

    def output(self, t):
         return self.input_function(t)(
             self.function_input(t)
         )
    def outputs(self, lower=None, upper=None, resolution=None):
        lower, upper, resolution = lower.indices(self.size) \
            if isinstance(lower, slice) else (lower, upper, resolution)
        lower = 0 if lower is None else lower
        upper = self.size if upper is None else upper
        resolution = 0.1 if resolution is None else resolution
        return (
            self.call(i) for i in range(lower, upper, resolution)
        )
    
    def __iadd__(self, function):
        self.extend_functions(function) if isinstance(function, Iterable) \
            else self.add_function(function)
    def __isub__(self, function):
        self.remove_functions(function) if isinstance(function, Iterable) \
            else self.remove_function(function)

    def __call__(self, *t): 
        return self.output(*t) if not t or (
            len(t) == 1 and isinstance(t[0], Number)
        ) else self.outputs(t) if isinstance(t, slice) \
            else self.output(*t)
    def __getitem__(self, index): 
        return self.outputs(index) if isinstance(index, slice) \
            else self.function(index)
    def __setitem__(self, index, function): self.set_function(index, function)
    def __contains__(self, function): return self.has_function(function)
    def __iter__(self): return iter(self.functions)
    def __reversed__(self): 
        return reversed(
            iter(self.functions)
        )