from abc import ABC, abstractmethod
from collections.abc import Iterable
import tkinter as tk


class TkinterGraphComponent(ABC):
    def __init__(self, canvas, origin, visible):
        self._canvas = canvas
        self._visible = bool(visible)
        self._origin = origin
        
    @abstractmethod
    def update_visible(): raise NotImplementedError
    @abstractmethod
    def update_origin(): raise NotImplementedError

    @abstractmethod
    def head_element(): raise NotImplementedError
    @abstractmethod
    def tail_element(): raise NotImplementedError
    @abstractmethod
    def raise_component(): raise NotImplementedError
    @abstractmethod
    def lower_component(): raise NotImplementedError
    
    @property
    def canvas(self): return self._canvas
    @property
    def canvas_width(self): return self._canvas.winfo_width()
    @property
    def canvas_height(self): return self._canvas.winfo_height()
    @property
    def visible(self): return self._visible
    @visible.setter
    def visible(self, state): self.set_visible(state)
    @property
    def origin(self): return tuple(self._origin)
    @origin.setter
    def origin(self, origin): self.set_origin(*origin)
    @property
    def origin_reference(self): return self._origin
    @property
    def horizontal_origin(self): return self._origin[0]
    @horizontal_origin.setter
    def horiztonal_origin(self, coord): 
        self.set_origin(coord, self.vertical_origin)
    @property
    def vertical_origin(self): return self._origin[1]
    @vertical_origin.setter
    def vertical_origin(self, coord): 
        self.set_origin(selfr.horizontal_origin, coord)
    
    def set_visible(self, state):
        self._visible = bool(state)
        return self
    def set_origin(self, horizontal, vertical):
        self._origin[0] = horizontal
        self._origin[1] = vertical
        return self
    def shift_origin(self, horizontal, vertical):
        self.set_origin(
            self.horizontal_origin + horizontal,
            self.vertical_origin + vertical,
        )
        return self

    def element_configuration(self, element, *args):
        return self._canvas.itemcget(element, *args)
    def element_coordinates(self, element):
        return self._canvas.coords(element)

    def reconfigure(self, *, origin=None, visible=None, color=None):
        self.set_visible(visible) if visible is not None else None
        self.set_origin(*origin) if origin else None
        return self

    def reconfigure_element(self, element, *args, **kwargs):
        self._canvas.itemconfigure(element, *args, **kwargs)
        return self
    def reconfigure_elements(self, elements, *args, **kwargs):
        [self.reconfigure_element(i, *args, **kwargs) for i in elements]
        return self
    def move_element(self, element, *coordinates):
        self._canvas.coords(element, *coordinates)
        return self

    def update(self):
        self.update_visible()
        self.update_origin()
        return self


class SingleElementTkinterGraphComponent(TkinterGraphComponent):
    def __init__(self, canvas, origin, visible, color, element_function, 
                    element_args):
        super().__init__(canvas, origin, visible)
        self._element_function = element_function
        self._color = color
        self._element = self.create_element(*element_args)

    @abstractmethod
    def create_element(): raise NotImplementedError

    @property
    def element(self): return self._element
    head_element = tail_element = element

    @property
    def color(self): return self._color
    @color.setter
    def color(self, color): self.set_color(color)

    def set_color(self, color):
        self._color = color
        return self

    def reconfigure(self, *, color=None, **kwargs):
        super().reconfigure(**kwargs)
        self.set_color(color) if color else None
        return self

    def raise_component(self, component, *args, **kwargs):
        component = component.head_element \
            if isinstance(component, TkinterGraphComponent) else component
        self._canvas.tag_raise(self._element, component, *args, **kwargs)
        return self
    def lower_component(self, component, *args, **kwargs):
        component = component.tail_element \
            if isinstance(component, TkinterGraphComponent) else component
        self._canvas.tag_lower(self._element, component, *args, **kwargs)
        return self

    def update_color(self):
        return self.reconfigure_element(self._element, fill=self._color)
    def update_visible(self):
        return self.reconfigure_element(
            self._element, state=tk.NORMAL if self._visible else tk.HIDDEN
        )

    def update_origin(self, *args, **kwargs):
        self.move_element(
            self._element,  *self._element_function(self, *args, **kwargs)
        )
        return self

    def update(self):
        super().update()
        self.update_color()
        return self  


class TkinterGraphPoint(SingleElementTkinterGraphComponent):
    def __init__(self, canvas, origin, visible, color, position, diameter):
        self._diameter = diameter
        self._position = position if isinstance(position, list) \
            else list(position)

        super().__init__(
            canvas, 
            origin, 
            visible, 
            color,
            lambda self: (
                self.horizontal_canvas_position - self._diameter // 2,
                self.vertical_canvas_position - self._diameter // 2,
                self.horizontal_canvas_position + self._diameter // 2 + self._diameter % 2,
                self.vertical_canvas_position + self._diameter // 2 + self._diameter % 2,
            ),
            ()
        )

    def create_element(self, *args):
        return self._canvas.create_oval(
            *self._element_function(self),
            fill=self._color, outline=""
        )

    @property
    def position(self): return tuple(self._position)
    @position.setter
    def position(self, postion): self.set_position(*position)
    @property
    def position_reference(self): return self._position
    @property
    def horizontal_position(self): return self._position[0]
    @horizontal_position.setter
    def horizontal_position(self, position): 
        self.set_position(position, self.vertical_position)
    @property
    def vertical_position(self): return self._position[1]
    @vertical_position.setter
    def vertical_position(self, position): 
        self.set_position(self.horizontal_position, position)

    @property
    def canvas_position(self): 
        return self.horizontal_canvas_position, self.vertical_canvas_position
    @property
    def horizontal_canvas_position(self):
        return self.horizontal_origin + self.horizontal_position
    @property
    def vertical_canvas_position(self):
        return self.vertical_origin + self.vertical_position

    @property
    def diameter(self): return self._diameter
    @diameter.setter
    def diameter(self, diameter): self.set_diameter(diameter)

    def set_position(self, horizontal, vertical):
        self._position[0] = horizontal
        self._position[1] = vertical
        return self

    def set_diameter(self, diameter):
        self._diameter = diameter
        return self
    
    def reconfigure(self, *, position=None, diameter=None, **kwargs):
        super().reconfigure(**kwargs)
        self.set_position(*position) if position else None
        self.set_diameter(diameter) if diameter else None
        return self

    def update_diameter(self):
        super().update_origin()
        return self
    def update_origin(self):
        self.update_diameter()
        return self


class TkinterGraphLine(SingleElementTkinterGraphComponent):
    @classmethod
    def vertical(cls, *args): 
        return cls(
            *args, lambda self: (
                self.horizontal_origin, 0,
                self.horizontal_origin, 
                self.canvas_height + self.vertical_origin
            ), ()
        )
    @classmethod
    def horizontal(cls, *args):
        return cls(
            *args, lambda self: (
                0, self.vertical_origin, 
                self.canvas_width + self.horizontal_origin,
                self.vertical_origin,
            ), ()
        )

    def create_element(self, *args, **kwargs):
        return self._canvas.create_line(
            *self._element_function(self, *args, **kwargs),
            fill=self._color
        )


class TkinterGraphAxes(TkinterGraphComponent):
    def __init__(self, canvas, origin, visible, horizontal_axis_color, 
                    vertical_axis_color):

        origin = origin if isinstance(origin, list) else list(origin)
        super().__init__(canvas, origin, visible)
        self._vertical_axis = TkinterGraphLine.vertical(
            self._canvas, self._origin, self._visible, vertical_axis_color
        )
        self._horizontal_axis = TkinterGraphLine.horizontal(
            self._canvas, self._origin, self._visible, horizontal_axis_color
        )

    @property
    def horizontal_axis(self): return self._horizontal_axis
    @property
    def vertical_axis(self): return self._vertical_axis
    @property
    def head_element(self): return self._horizontal_axis.element
    @property
    def tail_element(self): return self._vertical_axis.element

    def set_visible(self, state):
        super().set_visible(state)
        self._horizontal_axis.set_visible(self._visible)
        self._vertical_axis.set_visible(self._visible)
        return self

    def raise_component(self, component, *args, **kwargs):
        component = component.head_element \
            if isinstance(component, TkinterGraphComponent) else component
        self._horizontal_axis.raise_component(component, *args, **kwargs)
        self._vertical_axis.lower_component(self._horizontal_axis.element)
        return self
    def lower_component(self, component, *args, **kwargs):
        component = component.tail_element \
            if isinstance(component, TkinterGraphComponent) else component
        self._horizontal_axis.lower_component(component, *args, **kwargs)
        self._vertical_axis.lower_component(self._horizontal_axis.element)
        return self

    def update_visible(self):
        self._horizontal_axis.update_visible()
        self._vertical_axis.update_visible()
        return self
    def update_origin(self):
        self._horizontal_axis.update_origin()
        self._vertical_axis.update_origin()
        return self
    def update(self):
        super().update()
        self._horizontal_axis.update_color()
        self._vertical_axis.update_color()
        return self


class TkinterGraphGrid(TkinterGraphComponent):
    def __init__(self, canvas, origin, visible, color, resolution):
        super().__init__(canvas, origin, visible)
        self._resolution = resolution
        self._color = color

        self._vertical_bars = [
            self.new_vertical_bar(i) for i in range(self.vertical_bars)
        ]
        self._horizontal_bars = [
            self.new_horizontal_bar(i) for i in range(self.vertical_bars)
        ]
        self.update()

    @property
    def color(self): return self._color
    @color.setter
    def color(self, color): self.set_color(color)
    @property
    def resolution(self): return self._resolution
    @resolution.setter
    def resolution(self, resolution): self.set_resolution(resolution)
    @property
    def vertical_bars(self): return self.canvas_width // self._resolution + 1
    @property
    def horizontal_bars(self): return self.canvas_height // self._resolution + 1
    @property
    def head_element(self): return self._horizontal_bars[0].element
    @property
    def tail_element(self): return self._vertical_bars[-1].element
        
    def set_resolution(self, resolution):
        self._resolution = resolution
        return self
    def set_visible(self, visible):
        super().set_visible(visible)
        [i.set_visible(self._visible) for i in self._horizontal_bars]
        [i.set_visible(self._visible) for i in self._vertical_bars]
        return self
    def set_color(self, color):
        self._color = color
        [i.set_color(self._color) for i in self._horizontal_bars]
        [i.set_color(self._color) for i in self._vertical_bars]
        return self

    def reconfigure(self, *, resolution=None, color=None, **kwargs):
        super().reconfigure(**kwargs)
        self.set_resolution(resolution) if resolution else None
        self.set_color(color) if color else None
        return self

    def raise_component(self, component,*args, **kwargs):
        component = component.head_element \
            if isinstance(component, TkinterGraphComponent) else component
        [
            i.raise_component(component, *args, **kwargs) 
            for i in self._horizontal_bars
        ]
        [
            i.lower_component(self._horizontal_bars[-1].element) 
            for i in self._vertical_bars[::-1]
        ]
        return self
    def lower_component(self, component, *args, **kwargs):
        component = component.tail_element \
            if isinstance(component, TkinterGraphComponent) else component
        [
            i.lower_component(component, *args, **kwargs) 
            for i in self._horizontal_bars[::-1]
        ]
        [
            i.lower_component(self._horizontal_bars[-1].element) 
            for i in self._vertical_bars[::-1]
        ]
        return self

    def new_bar(self, index, element_function):
        return TkinterGraphLine(
            self._canvas, 
            self._origin, 
            self._visible, 
            self._color, 
            element_function, 
            (self, index) 
        )

    def new_horizontal_bar(self, index):
        return self.new_bar(
            index,
            lambda bar, grid, i: (
            0, 
            grid.vertical_origin % grid._resolution + grid._resolution * i, 
            grid.canvas_width + grid.horizontal_origin,
            grid.vertical_origin % grid._resolution + grid._resolution * i,
            )
        )
        
    def new_vertical_bar(self, index):
        return self.new_bar(
            index, 
            lambda bar, grid, i: ( 
            grid.horizontal_origin % grid._resolution + grid._resolution * i, 
            0, 
            grid.horizontal_origin % grid._resolution + grid._resolution * i,
            grid.canvas_height + grid.vertical_origin
            ) 
        )
    def add_horizontal_bar(self, index):
        self._horizontal_bars.append(
            self.new_horizontal_bar(index)
        )
        return self
    def add_vertical_bar(self, index):
        self._vertical_bars.append(
            self.new_vertical_bar(index)
        )
        return self

    def update_horizontal_resolution(self):
        [
            self.add_horizontal_bar(i) for i in range(
                len(self._horizontal_bars), self.horizontal_bars
            )
        ]
        [
            v.update_origin(self, i) 
            for i, v in enumerate(self._horizontal_bars)
        ]
        return self
    def update_vertical_resolution(self):
        [
            self.add_vertical_bar(i) for i in range(
                len(self._vertical_bars), self.vertical_bars
            )
        ]
        [
            v.update_origin(self, i) 
            for i, v in enumerate(self._vertical_bars)
        ]
        return self
    
    def update_resolution(self):
        self.update_horizontal_resolution()
        self.update_vertical_resolution()
        return self

    def update_color(self):
        [i.update_color() for i in self._horizontal_bars]
        [i.update_color() for i in self._vertical_bars]
        return self
    def update_origin(self):
        self.update_resolution()
        return self
    def update_visible(self):
        [i.update_visible() for i in self._horizontal_bars]
        [i.update_visible() for i in self._vertical_bars]
        return self
    def update(self):
        super().update()
        self.update_color()
        return self


class TkinterCurveComponent(ABC):
    pass


class TkinterCurvePoint(TkinterCurveComponent, TkinterGraphPoint):
    pass


class TkinterCurveSegment(TkinterCurveComponent, TkinterGraphLine):
    def __init__(self, canvas, origin, visible, color, leading_point, 
                    trailing_point):
        self._curve_points = [leading_point, trailing_point]
        super().__init__(
            canvas, 
            origin, 
            visible, 
            color,
            lambda self: (
                self.leading_point.horizontal_canvas_position,
                self.leading_point.vertical_canvas_position,
                self.trailing_point.horizontal_canvas_position,
                self.trailing_point.vertical_canvas_position,
            ), ()
            )
    @property
    def curve_points(self): return tuple(self._curve_points)
    @curve_points.setter
    def curve_points(self, points): self.set_curve_points(*points)
    @property
    def leading_point(self): return self._curve_points[0]
    @leading_point.setter
    def leading_point(self, point): 
        self.set_curve_points(point, self.trailing_point)
    @property
    def trailing_point(self): return self._curve_points[1]
    @trailing_point.setter
    def trailing_point(self, point): 
        self.set_curve_points(self.leading_point, point)
    
    def set_curve_points(self, leading_point, trailing_point):
        self._curve_points[0] = leading_point
        self._curve_points[1] = trailing_point
        return self


class TkinterInterpolationCurve(TkinterGraphComponent):
    def __init__(self, canvas, origin, visible, function, resolution, 
                    point_color, segment_color, point_diameter):
        origin = origin.origin_reference \
            if isinstance(origin, TkinterGraphComponent) \
            else origin
        super().__init__(canvas, origin, visible)
        self._function = function
        self._resolution = resolution

        self._point_color = point_color
        self._segment_color = segment_color
        self._point_diameter = point_diameter

        self._curve_points = []
        [
            self.add_curve_point(i) for i in range(*self.function_bounds)
        ]
        self._curve_segments = []
        [
            self.add_curve_segment(i) for i in range(self.curve_segments)
        ]

    @property
    def head_element(self): return self._curve_points[0].element
    @property
    def tail_element(self): return self._curve_segments[-1].element

    @property
    def function(self): return self._function
    @property
    def resolution(self): return self._resolution
    @resolution.setter
    def resolution(self, resolution): self.set_resolution(resolution)
    @property
    def function_bounds(self): 
        return self.lower_function_bound, self.upper_function_bound
    @property
    def lower_function_bound(self): 
        return -int(self.horizontal_origin // self._resolution + 1)
    @property
    def upper_function_bound(self):
        return self.curve_points - self.lower_function_bound + 1

    @property
    def curve_points(self): return int(
        self.canvas_width // self._resolution + 2
    )
    @property
    def curve_segments(self): return self.curve_points - 1
    @property
    def point_color(self): return self._point_color
    @point_color.setter
    def point_color(self, color): self.set_point_color(color)
    @property
    def segment_color(self): return self._segment_color
    @segment_color.setter
    def segment_color(self, color): self.set_segment_color(color)
    @property
    def point_diameter(self): return self._point_diameter
    @point_diameter.setter
    def point_diameter(self, diameter): self.set_point_diameter(diameter)

    def set_resolution(self, resolution):
        self._resolution = resolution
        return self
    def set_point_color(self, color):
        self._point_color = color
        [i.set_color(self._point_color) for i in self._curve_points]
        return self
    def set_segment_color(self, color):
        self._segment_color = color
        [i.set_color(self._segment_color) for i in self._curve_segments]
        return self
    def set_point_diameter(self, diameter):
        self._point_diameter = diameter
        [i.set_diameter(self._point_diameter) for i in self._curve_points]
        return self

    def set_visible(self, state):
        super.set_visible(state)
        [i.set_visible(self._visible) for i in self._curve_points]
        [i.set_visible(self._visible) for i in self._curve_segment]
        return self

    def function_output(self, index):
        horizontal, vertical = self._function(index * self._resolution)
        return horizontal, -vertical 

    def raise_component(self, component,*args, **kwargs):
        component = component.head_element \
            if isinstance(component, TkinterGraphComponent) else component
        [
            i.raise_component(component, *args, **kwargs) 
            for i in self._curve_points
        ]
        [
            i.lower_component(self._curve_points[-1].element) 
            for i in self._curve_segments[::-1]
        ]
        return self
    def lower_component(self, component, *args, **kwargs):
        component = component.tail_element \
            if isinstance(component, TkinterGraphComponent) else component
        [
            i.lower_component(component, *args, **kwargs) 
            for i in self._curve_points[::-1]
        ]
        [
            i.lower_component(self._curve_points[-1].element) 
            for i in self._curve_segments[::-1]
        ]
        return self

    def add_curve_point(self, index):
        self._curve_points.append(
            TkinterCurvePoint(
                self._canvas,
                self._origin,
                self._visible,
                self._point_color,
                self.function_output(index),
                self._point_diameter
            )
        )
        return self

    def add_curve_segment(self, index):
        self._curve_segments.append(
            TkinterCurveSegment(
                self._canvas,
                self._origin,
                self._visible,
                self._segment_color,
                self._curve_points[index],
                self._curve_points[index + 1]
            )
        )
        return self

    def update_points(self):
        [
            self.add_curve_point(0)
            for i in range(
                len(self._curve_points), self.curve_points
            )
        ]
        [
            v.set_position(
                *self.function_output(i + self.lower_function_bound)
            ) for i, v in enumerate(self._curve_points) 
        ]
        
    def update_segments(self):
        [
            self.add_curve_segment(i)
            for i in range(
                len(self._curve_segments), self.curve_segments
            )
        ]
        [
            v.set_curve_points(
                self._curve_points[i], self._curve_points[i + 1]
                ) 
            for i, v in enumerate(self._curve_segments) 
        ]
        return self

    def update_resolution(self):
        self.update_points()
        self.update_segments()
        [i.update_origin() for i in self._curve_points]
        [i.update_origin() for i in self._curve_segments]
        return self
    def update_color(self):
        [i.update_color() for i in self._curve_points]
        [i.update_color() for i in self._curve_segments]
        return self
    def update_diameter(self):
        [i.update_diameter() for i in self._curve_points]
        return self

    def update_origin(self):
        self.update_resolution()
        return self
    def update_visible(self):
        [i.update_visible() for i in self._curve_points]
        [i.update_visible() for i in self._curve_segments]
        return self

    def update(self):
        super().update()
        self.update_color()
        self.update_diameter()
        return self


class TkinterCanvasDragHandler:
    def __init__(self):
        self._dragging = False
        self._mark = [0, 0]
        self._previous_mark = [0, 0]

    @property
    def dragging(self): return self._dragging
    @dragging.setter
    @property
    def dragging(self, state): self.set_dragging(state)
    @property
    def mark(self): 
        return self.horizontal_mark, self.vertical_mark
    @mark.setter
    def mark(self, mark): self.set_mark(*mark)
    @property
    def horizontal_mark(self): return self._mark[0]
    @property
    def vertical_mark(self): return self._mark[1]
    @property
    def previous_mark(self): 
        return (self.previous_horizontal_mark, self.previous_vertical_mark)
    @previous_mark.setter
    def previous_mark(self, mark): self.set_previous_mark(*mark)
    @property
    def previous_horizontal_mark(self): return self._previous_mark[0]
    @property
    def previous_vertical_mark(self): return self._previous_mark[1]

    def set_dragging(self, state):
        self._dragging = bool(state)
        return self
    def set_mark(self, horizontal, vertical):
        self._mark[0] = horizontal
        self._mark[1] = vertical
        return self
    def set_previous_mark(self, horizontal, vertical):
        self._previous_mark[0] = horizontal
        self._previous_mark[1] = vertical
        return self
    
    def start_dragging(self, horizontal, vertical):
        self.set_dragging(True)
        self.set_mark(horizontal, vertical)
        self.set_previous_mark(horizontal, vertical)
        return self
    def stop_dragging(self):
        self.set_dragging(False)
        return self     

    def mark_delta(self, horizontal, vertical):
        return (
            horizontal - self.horizontal_mark, vertical - self.vertical_mark
        )
    def previous_mark_delta(self, horizontal, vertical):
        return (
            horizontal - self.previous_horizontal_mark, 
            vertical - self.previous_vertical_mark
        )

    def update_previous_mark(self, horizontal, vertical):
        h_delta, v_delta = self.previous_mark_delta(horizontal, vertical)
        self.set_previous_mark(horizontal, vertical)
        return h_delta, v_delta
    def update(self, horizontal, vertical):
        self.update_previous_mark(horizontal, vertical)
        return self


class TkinterGraphPlotterCanvas(tk.Canvas):
    def __init__(self, *args, origin=None, resolution=50, curves=(),
                    origin_color="black", h_color="red", v_color="green", 
                    grid_color="light gray", origin_diameter=4, **kwargs):
        super().__init__(*args, **kwargs)
        self._drag = TkinterCanvasDragHandler()
        
        origin = origin if isinstance(origin, list) \
            else list(origin) if origin \
            else [0, 0]
        
        self._grid = TkinterGraphGrid(
            self, origin, True, grid_color, resolution
        )
        self._axes = TkinterGraphAxes(
            self, origin, True, h_color, v_color
        )
        self._origin = TkinterGraphPoint(
            self, origin, True, origin_color, (0, 0), origin_diameter
        )

        self._curves = curves if isinstance(curves, list) else list(curves)
        
        self.bind(
            "<Configure>", lambda e: self.update_components()
        )
        self.bind(
            "<Button-1>", lambda e: self._drag.start_dragging(e.x, e.y)
        )
        self.bind(
            "<ButtonRelease-1>", lambda e: self._drag.stop_dragging()
        )
        self.bind(
            "<Motion>", 
            lambda e: (
                self._origin.shift_origin(
                    *self._drag.update_previous_mark(e.x, e.y)
                ),
                self.update_components()
            ) if self._drag.dragging else None
        )

    @property
    def grid(self): return self._grid
    @property
    def axes(self): return self._axes
    @property
    def origin(self): return self._origin
    
    def update_components(self):
        self._grid.update()
        self._axes.update()
        self._origin.update()
        [i.update() for i in self._curves]

        top_level = 1
        for i in self._curves:
            i.lower_component(top_level)
            top_level = i.tail_element
        self._origin.lower_component(top_level)
        self._axes.lower_component(self._origin)
        self._grid.lower_component(self._axes.vertical_axis)
        return self

    def update(self, *args, **kwargs):
        val = super().update(*args, **kwargs)
        self.update_components()
        return val

    def pack(self, *args, **kwargs):
        val = super().pack(*args, **kwargs)
        self.update_components()
        return val

    def grid(self, *args, **kwargs):
        val = super().grid(*args, **kwargs)
        self.update_components()
        return val
