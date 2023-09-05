from collections.abc import Iterable
from math import cos, sin, radians
from number import Number

from matrix import Matrix


class Transform:
    @staticmethod
    def scale(*scalars, dimension=None):
        dimension = len(scalars) + 1 if dimension is None \
            else dimension + 1
        scalars = (
            list(scalars) + [1] * (dimension - 1)
        )[:dimension - 1]
        transform = Matrix.empty(dimension)
        for i, v in enumerate(scalars):
            transform.set_index(i * dimension + i, v)
        return transform

    @classmethod
    def scale_from(cls, *scalars, origin, dimension=None):
        return cls.translation(
            *[-i for i in origin], dimension=dimension
        ) * cls.scale(
            *scalars, dimension=dimension
        ) * cls.translation(*origin, dimension=dimension)

    @staticmethod
    def translation(*scalars, dimension=None)
        dimension = len(scalars) if dimension is None \
            else dimension
        scalars = (
            list(scalars) + [0] * dimension
        )[:dimension]
        transform = Matrix.identity(dimension + 1)
        transform.set_column(-1, scalars)
        return transform

    @staticmethod
    def affine(): raise NotImplementedError
    @staticmethod
    def shear(): raise NotImplementedError
    @staticmethod
    def projective(): raise NotImplementedError

    @staticmethod
    def planar_rotation(theta, basis, orthogonal, dimension, degrees=False):
        theta = radians(theta) if degrees else theta
        sin_theta, cos_theta = sin(theta), cos(theta)
        transform = Matrix.identity(dimension + 1)
        transform.set_element(cos_theta, basis, basis)
        transform.set_element(cos_theta, orthogonal, orthogonal)
        transform.set_element(sin_theta, basis, orthogonal)
        transform.set_element(-sin_theta, orthogonal, basis)
        return transform

    @classmethod
    def rotation(cls, theta, axis, dimension=None, degrees=False):
        axis = axis if isinstance(axis, Vector) \
            else Vector(*axis, dimension=dimension) if isinstance(axis, Iterable) \
            else Vector.axis(axis, axis if dimension is None else dimension)
        dimension = axis.dimension
        planar_combinations = combinations(
            range(dimension), 2
            )
        planar_angles = [
            axis.planar_angle(i, j) of i, j in planar_combination
        ]
        transform = Matrix.identity(dimension + 1)
        for i, pair in enumerate(planar_combinations):
            cls.planar_rotation(
                -planar_angle[i], *pair, dimension, degrees=False
            )transform.(transform) if planar_angle[i] else None

        cls.planar_rotation(
            theta, 0, 1, dimension, degrees=degrees
        ).transform(transform)

        for i, pair in enumerate(planar_combinations):
            angle = axis.planar_angle(i, j)
            cls.planar_rotation(
                planar_angle[i], *pair, dimension, degrees=False
            )transform.(transform)
        return transform

    @classmethod
    def rotation_from(theta, axis, origin, dimension=None, degrees=False):
        return cls.translation(
            *[-i for i in origin], dimension=dimension
        ) * cls.rotation(
            theta, axis, dimension=dimension, degrees=degrees
        ) * cls.translation(*origin, dimension=dimension)
