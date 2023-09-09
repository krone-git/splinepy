from abc import ABC, abstractmethod
from collections.abc import Iterable, Sized, Sequence
from numbers import Number
from math import prod


class TensorType(ABC):  
    @abstractmethod
    def get_index(): raise NotImplementedError
    @abstractmethod
    def set_index(): raise NotImplementedError
    @abstractmethod
    def dot(): raise NotImplementedError
    @abstractmethod
    def copy(): raise NotImplementedError

    @classmethod
    def new(cls, *args, **kwargs): return cls(*args, **kwargs)

    def __init__(self, width, height):
        self._shape = [
            abs(width), abs(height)
            ]

    @property
    def shape(self): return self._shape
    @property
    def width(self): return self._shape[0]
    @property
    def height(self): return self._shape[1]
    @property
    def size(self): return prod(self._shape)
    @property
    def degree(self): return len(self._shape)
    @property
    def is_empty(self): return set(self.elements) == {0}
    @property
    def columns(self):
        return (
            self.column(i) for i in range(self.width)
        )
    @property
    def rows(self):
        return (
            self.row(i) for i in range(self.height)
        )
    @property
    def elements(self):
        return (
            self.get_index(i) for i in range(self.size)
        )
    
    def element(self, column, row): 
        return self.get_index(
            self.index(column, row)
        )
    def set_element(self, element, column, row):
        self.set_index(
            self.index(column, row), element
        )
        return self
    def set_elements(self, elements):
        elements = elements.elements if isinstance(elements, TensorType) \
            else elements
        for i, v in enumerate(elements):
            self.set_index(i, v)
        return self
    
    def address(self, index):
        index %= self.size
        return index % self.width, index // self.width
    def index(self, column, row): 
        return (row % self.height) * self.width + (column % self.width)
    
    def sub_tensor_address(self, column, row, width=None, height=None):
        column = column + width if width is not None and width < 0 else column
        row = row + height if height is not None and height < 0 else row
        return (
            min(column % self.width, self.width - 1), 
            min(row % self.height, self.height - 1)
        )
    def sub_tensor_shape(self, column, row, width, height):
        column, row = self.sub_tensor_address(
            column, row, width=width, height=height
        )
        width, height = abs(width), abs(height)
        return (
            min(width, self.width - column), min(height, self.height - row)
        )

    def slice_elements(self, start, stop, step):
        return (
            self.get_index(i) for i in range(start, stop, step)
        )     
    def column(self, column, **kwargs):
        slice = self.column_slice(column, **kwargs)
        return self.slice_elements(
            *slice.indices(self.size)
        )
    def row(self, row, **kwargs):
        slice = self.row_slice(row, **kwargs)
        return self.slice_elements(
            *slice.indices(self.size)
        )
    def sub_tensor_elements(self, column, row, width, height):
        elements = []
        [
            elements.extend(
                self.slice_elements(
                    *i.indices(self.size)
                )
            )
            for i in self.element_slices(column, row, width, height)
        ]
        return iter(elements)
    def row_elements(self, row, height):
        slice = self.rows_slice(row, height)
        return self.slice_elements(
            *slice.indices(self.size)
            )
    
    def row_slice(self, row, column=None, width=None):
        column = 0 if column is None else column % self.width
        width = self.width - column if width is None else width
        row %= self.height
        return slice(
            self.width * row + column, self.width * row + column + width, 1
        )
    def rows_slice(self, row, height):
        row %= self.height
        return slice(
            self.width * row, self.width * (row + height), 1
        )
    def column_slice(self, column, row=None, height=None):
        row = 0 if row is None else row % self.height
        height = self.height - row if height is None else height
        column %= self.width
        return slice(row * self.width + column, self.size, self.width)
    def element_slices(self, column, row, width, height):
        return (
            self.row_slice(row + i, column=column, width=width)
            for i in range(height)
        )
    
    def column_indices(self, *args, **kwargs):
        slice = self.column_slice(*args, **kwargs)
        return range(
            *slice.indices(self.size)
        )
    def row_indices(self, *args, **kwargs):
        slice = self.row_slice(*args, **kwargs)
        return range(
            *slice.indices(self.size)
        )
    def rows_indices(self, *args, **kwargs):
        slice = self.rows_slice(*args, **kwargs)
        return range(
            *slice.indices(self.size)
        )
    def sub_tensor_indices(self, column, row, width, height):
        column, row = self.sub_tensor_address(
            column, row, width=width, height=height
        )
        width, height = self.sub_tensor_shape(column, row, width, height)
        indices = []
        for i in self.element_slices(column, row, width, height):
            indices.extend(
                range(
                    *i.indices(self.size)
                )
            )
        return iter(indices)

    def set_indices(self, indices, elements):
        elements = list(elements) if not isinstance(elements, Sequence) \
            else elements
        [
            self.set_index(index % self.size, elements[i])
            for i, index in enumerate(indices)
        ]
        return self
    def set_column(self, column, elements, *args, **kwargs):
        return self.set_indices(
            self.column_indices(column, *args, **kwargs), elements
        )
    def set_row(self, row, elements, *args, **kwargs):
        return self.set_indices(
            self.row_indices(row, *args, **kwargs), elements
        )
    def set_sub_tensor_indices(self, column, row, width, height, elements):
        self.set_indices(
            self.sub_tensor_indices(column, row, width, height), elements
        )
        return self
    def set_sub_tensor(self, column, rows, tensor):
        self.set_sub_tensor_indices(
            column, rows, tensor.width, tensor.height, tensor.elements
        )
        return self

    def move_row(self, from_index, to_index):
        if from_index != to_index:
            from_index = from_index % self.height
            to_index = to_index % self.height
            min_index = min(from_index, to_index)
            max_index = max(from_index, to_index)

            elements = list(
                self.row_elements(0, min_index)
            )
            elements.extend(
                self.row(from_index)
            ) if to_index < from_index else None
            elements.extend(
                self.row_elements(
                    min_index + (1 if to_index > from_index else 0),
                    max_index - min_index
                    )
            )
            elements.extend(
                self.row(from_index)
            ) if to_index > from_index else None
            elements.extend(
                self.row_elements(
                    max_index + 1, self.height - max_index
                    )
            )
            self.set_elements(elements)
        return self
    
    def shift_row(self, row, offset):
        row %= self.height
        return self.move_row(row, row + offset)
    
    def move_column(self, from_index, to_index):
        raise NotImplementedError
    def shift_column(self, column, offset):
        column %= self.width
        return self.move_column(column, column + offset)
    
    def add(self, other, *args, **kwargs): return self.copy().iadd(other)
    def iadd(self, other):
        other = [other] * self.size if isinstance(other, Number) \
            else other.elements
        [
            self.set_index(i, self.get_index(i) + v)
            for i, v in enumerate(other)
        ]
        return self
    def subtract(self, other, *args, **kwargs):
        return self.add(-other, *args, **kwargs)
    def isubtract(self, other): return self.iadd(-other)
    def scale(self, scalar, *args, **kwargs):
        return self.copy().iscale(scalar)
    def iscale(self, other):
        [
            self.set_index(i, v * other)
            for i, v in enumerate(self.elements)
        ]
        return self

    def equivalent(self, other): 
        return tuple(self.elements) == tuple(other.elements) \
            and self._shape == other._shape
    
    def display(self, truncate=3, pad=2, indent=2):
        elements = [
            str(round(i, truncate)) for i in self.elements
        ]
        max_len = max(
            len(i) for i in elements
        )
        string = "["
        for i, v in enumerate(elements):
            string += "\n" + " " * indent if i % self.width == 0 else ""
            string += v.rjust(max_len, " ")
            string += " " * pad if i % self.width < self.width - 1 else ""
        string += "\n]"
        return string

    def print(self, *args, **kwargs):
        print(
            self.display(*args, **kwargs)
        )
        return self

    def __getitem__(self, address): return self.element(*address)
    def __setitem__(self, address, element):
        self.set_element(element, *address) if isinstance(address, Iterable) \
            else self.set_index(address, element)
    def __neg__(self): return self.scale(-1)
    def __eq__(self, other): return self.equivalent(other)
    def __add__(self, other): return self.add(other)
    def __iadd__(self, other): return self.iadd(other)
    def __sub__(self, other): return self.subtract(other)
    def __isub__(self, other): return self.isubtract(other)
    def __mul__(self, other): return self.scale(other)
    def __imul__(self, other): return self.iscale(other)
    def __rmul__(self, other): return self.scale(other)
    def __truediv__(self, scalar): return self.scale(1 / scalar)
    def __itruediv__(self, scalar): return self.iscale(1 / scalar)
    def __len__(self): return self.size
    def __iter__(self): return self.rows()
    def __reversed__(self): 
        return reversed(
            iter(self)
        ) 
    def __str__(self): return f"%s (%i, %i) <%s>" % (
        self.__class__.__name__, self.width, self.height, id(self)
        )
    

class TensorReference(TensorType):
    def __init__(self, tensor, column, row, width, height):
        self._tensor = tensor
        self._address = [column, row]
        super().__init__(width, height)

    @property
    def reference_column(self): return self._address[0]
    @property
    def reference_row(self): return self._address[1]
    @property
    def reference_address(self): return tuple(self._address)
    @property
    def reference_index(self): return self._tensor.index(*self._address)
    @property
    def tensor(self): return self._tensor

    def get_index(self, index): 
        return self._tensor.get_index(
            self.tensor_index(index)
        )
    def set_index(self, index, element):
        self._tensor.set_index(
            self.tensor_index(index), element
        )
        return self
    def set_address(self, column, row):
        self._address[0] = column
        self._address[1] = row
        return self
    
    def lower_address(self, step=1):
        self._address[0] += step
        return self
    def raise_address(self, step=1):
        return self.lower_address(step=-step)
    def shift_address(self, step=1):
        self._address[1] += step
        return self

    def reference_index_address(self, index):
        return self.tensor_address(
            *self.address(index)    
        )
    def reference_address_index(self, column, row):
        return self.tensor_index(
            self.index(column, row)
        )
    def tensor_address(self, column, row):
        return (
            column % self.width + self.reference_column, 
            row % self.height + self.reference_row
        )
    def tensor_index(self, index):
         return self._tensor.index(
            *self.reference_index_address(index % self.size)
        )
    
    def tensor_indices(self, column=None, row=None, width=None, height=None):
        return self._tensor.sub_tensor_indices(    
            column=self.reference_column if column is None else column % self.width,
            row=self.reference_row if row is None else row % self.height,
            width=self.width if width is None else width,
            height=self.height if height is None else height
        )

    def dot(self, other, *args, type=None, **kwargs):
        type = Tensor if type is None else type
        return type.dot(self, other, *args, **kwargs)

    def copy(self):
        return self.new(self._tensor, *self.reference_address, *self.shape)

    def to_tensor(self, *args, type=None, **kwargs):
        type = self._tensor.__class__ if type is None else type
        return type.new_tensor(
            self.width, *args, height=self.height, elements=self.elements, **kwargs 
            )


class Tensor(TensorType):
    @classmethod
    def _row_echelon_recursion(cls, tensor):
        if tensor.width > 1:
            indices = [
                i for i, v in enumerate(
                    tensor.column(0)
                ) if v != 0
            ]
            if len(indices) > 1:
                equation = list(
                    tensor.row(indices[0])
                )
                for i in indices[1:]:
                    coefficient = tensor.element(0, i) / equation[0]
                    tensor.set_row(
                        i, (
                            v - equation[j] * coefficient \
                            for j, v in enumerate(
                                tensor.row(i)
                            )
                        )
                    )
            tensor.set_sub_tensor(
                1, 1, cls._row_echelon_recursion(
                    tensor.sub_tensor(
                        1, 1, tensor.width - 1, tensor.height - 1
                    )
                )
            )
            tensor.move_row(indices[0], 0)
            return tensor
        else:
            return tensor
    
    @classmethod
    def new_tensor(cls, width, height=None, elements=None, fill=None, 
                   link=False):
        return cls(
            width, 
            height=height, 
            elements=elements, 
            fill=fill, 
            link=link
        )
    @classmethod
    def from_tensor(cls, tensor, **kwargs):
        return cls.new_tensor(
            tensor.width,
            height=tensor.height,
            elements=tensor.elements,
            **kwargs
        )
    @classmethod
    def from_rows(cls, rows, **kwargs):
        height = 0
        elements = []
        for i in rows:
            height += 1
            elements.extend(i)
        return cls.new_tensor(
            len(elements) // height, 
            height=height, 
            elements=elements, 
            **kwargs
        )
    @classmethod
    def from_columns(cls, columns, **kwargs):
        width = 0
        elements = []
        for c in columns:
            width += 1
            for i, v in enumerate(c):
                elements.insert(width * i + width - 1, v)
        return cls.new_tensor(
            width,
            height=len(elements) // width,
            elements=elements,
            **kwargs
        )
    @classmethod
    def empty(cls, width, height, **kwargs):
        return cls.fill(width, height, 0, **kwargs)
    @classmethod
    def fill(cls, width, height, fill, **kwargs):
        kwargs.update(height=height, elements=[], fill=fill)
        return cls.new(width, **kwargs)

    def __init__(self, width, height=None, elements=None, fill=None, link=False):
        self._elements = elements if isinstance(elements, list) and link \
            else elements._elements if isinstance(elements, Tensor) and link \
            else list(elements.elements) if isinstance(elements, TensorType) \
            else list(elements) if isinstance(elements, Iterable) \
            else [elements] if elements is not None \
            else []
        
        element_size = len(self._elements)
        height = height if height is not None \
            else element_size // width + (element_size % width) // 1
        super().__init__(width, height)
        
        fill = 0 if fill is None else fill
        temp = self._elements.copy()
        temp.extend([fill] * self.size)
        self._elements.clear()
        self._elements.extend(temp[:self.size])

    @property
    def is_empty(self): return set(self._elements) == {0}
    @property
    def elements(self): return iter(self._elements)
    @property
    def transpose(self):
        return self.from_rows(self.columns)
    @property
    def row_echelon(self): 
        return self._row_echelon_recursion(
            self.copy()
        )
    ref = row_echelon
    @property
    def adjoint(self):
        return self.new_tensor(
            self.width,
            height=self.height,
            elements=[
                self.cofactor(
                    *self.address(i)
                ).determinant * (-1)**sum(
                    self.address(i)
                )
                for i in range(self.size)
            ]
        ).transpose
    
    def get_index(self, index):
        return self._elements[index % self.size]
    def set_index(self, index, element):
        self._elements[index % self.size] = element
        return self

    def set_elements(self, elements):
        elements = list(elements) if not isinstance(elements, Sequence) \
            else elements
        temp = self._elements.copy()
        self._elements.clear()
        self._elements.extend(
            elements[:self.size] + temp[len(elements):]
        )
        return self

    def slice_elements(self, start, stop, step):
        return self._elements[start : stop : step]
    def cofactor_elements(self, column, row):
        return [
            v for i, v in enumerate(self.elements) \
            if i % self.width != column and i // self.width != row
        ]

    def sub_tensor(self, column, row, width, height, *args, **kwargs):
        return self.new_tensor(
            *self.sub_tensor_shape(column, row, width, height), *args, 
            elements=self.sub_tensor_elements(column, row, width, height), 
            **kwargs
        )
    def cofactor(self, column, row):
        return self.new_tensor(
            self.width - 1, height=self.height-1, 
            elements=self.cofactor_elements(column, row)
        )

    def column_reference(self, column):
        return self.sub_tensor_reference(column, 0, 1, self.height)
    def row_reference(self, row):
        return self.sub_tensor_reference(0, row, self.width, 1)
    def sub_tensor_reference(self, column, row, width, height):
        return TensorReference(
            self, 
            *self.sub_tensor_address(
                column, row, width=width, height=height
            ), 
            *self.sub_tensor_shape(column, row, width, height)
        )

    def dot_elements(self, other):
        elements = []
        for i, row in enumerate(self.rows):
            for j, column in enumerate(other.columns):
                elements.append(
                    sum(
                        i * j for i, j in zip(row, column)
                    )
                )
        return elements
    
    def dot(self, other):
        elements = self.dot_elements(other)
        return sum(elements) if len(elements) < 2 \
            else other.new_tensor(
                other.width, height=other.height, elements=elements
            )

    def idot(self, other):
        other.transform(self)
        return self

    def transform(self, other):
        other.set_elements(
            self.dot_elements(other)
        )
        return other

    def equivalent(self, other):
        return self._elements == other._elements \
            and self._shape == other._shape
    
    def copy(self, **kwargs):
        return self.new_tensor(
            *self.shape, elements=self._elements.copy(), **kwargs
            )
    
    def __getitem__(self, address): 
        return self.element(*address) if isinstance(address, Iterable) \
            else self.slice_elements(address) if isinstance(address, slice) \
            else self.row_reference(address)
    def __mul__(self, other):
        return self.scale(other) if isinstance(other, Number) \
            else self.scale(other._elements[0]) \
                if other.size == 1 else self.dot(other)
    def __imul__(self, other):
        return self.iscale(other) if isinstance(other, Number) \
            else self.iscale(other._elements[0]) \
                if other.size == 1 else self.idot(other)    