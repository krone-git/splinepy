from collections.abc import Iterable, Sized

from tensor import Tensor, TensorType
from vector import Vector


class Matrix(Tensor):
    @classmethod
    def _determinant_recursion(cls, tensor):
        if tensor.width < 3:
            a, b, c, d = tensor._elements
            return a * d - b * c
        else:
            determinant = 0
            for i in range(tensor.width):
                determinant += tensor._elements[i] \
                    * cls._determinant_recursion(
                        tensor.cofactor(i, 0)
                    ) * (-1)**i
            return determinant

    @classmethod
    def new_tensor(cls, width, height=None, elements=None, **kwargs):
        return cls(
            elements, dimension=width, **kwargs
        )
    @classmethod
    def identity(self, dimension):
        elements = [0] * dimension**2
        for i in range(dimension):
            elements[i * dimension + i] = 1
        return self.new_tensor(dimension, elements=elements)
    @classmethod
    def empty(cls, dimension, **kwargs):
        return cls.fill(dimension, 0, **kwargs)
    @classmethod
    def fill(cls, dimension, fill, **kwargs):
        kwargs.update(dimension=dimension, fill=fill)
        return cls.new(
            (), **kwargs
        )

    def __init__(self, elements, dimension=None, link=False, **kwargs):
        elements = elements if isinstance(elements, Sized) \
            else elements._elements if isinstance(elements, Tensor) and link \
            else list(elements.elements) if isinstance(elements, TensorType) \
            else list(elements) if isinstance(elements, Iterable) \
            else [elements] if elements is not None else []
        dimension = int(
            len(elements)**0.5 if dimension is None else dimension
        )
        super().__init__(
            dimension, 
            height=dimension, 
            elements=elements, 
            **kwargs
            )

    @property
    def dimension(self): return self.width
        
    @property
    def determinant(self): 
        return self._determinant_recursion(self)
    det = determinant
    @property
    def inverse(self):
        return self.adjoint / self.determinant


    