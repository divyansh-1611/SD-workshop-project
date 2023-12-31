from abc import abstractmethod

import numpy as np
from PyQt5 import QtGui
from scipy.optimize import fsolve

from cad import pen
from cad.figures import *


class System(object):

    def __init__(self, sketch):
        self.sketch = sketch
        self.constraints = []

    @property
    def points(self) -> list:
        points = []
        for line in self.sketch.lines:
            points.extend(line.points)
        for point in self.sketch.points:
            points.append(point)
        return points

    def addConstraint(self, constraint):
        self.constraints.append(constraint)

    def recount(self):
        if len(self.x0):
            result = self.solve()
            if result[2] == 1:
                y = [round(y, 1) for y in result[0]]
                for i, point in enumerate(self.points):
                    for j, prop in enumerate(('x', 'y')):
                        n = i * 2 + j
                        setattr(point, prop, y[n])

    def solve(self):
        result = fsolve(self.system, self.x0, full_output=True, xtol=1e-2)
        return result

    def system(self, x: np.ndarray) -> np.ndarray:
        y = np.zeros(shape=x.shape, dtype=x.dtype)

        for i, point in enumerate(self.points):
            for j, coordinate in enumerate(point.coordinates):
                n = i * 2 + j
                y[n] = 2 * (x[n] - coordinate)

        for i, constraint in enumerate(self.constraints):
            n = len(self.points) * 2 + i
            constraint.apply(self, x, y, n)

        return y

    @property
    def x0(self) -> np.ndarray:
        size = len(self.points) * 2 + len(self.constraints)
        y = np.zeros(shape=(size, ), dtype=float)
        return y


class Handler:

    def mouseMoved(self, sketch):
        pass

    def mousePressed(self, sketch):
        pass

    def mouseReleased(self, sketch):
        pass


class DisableHandler(Handler):
    pass


class LineDrawing(Handler):

    def mousePressed(self, sketch):
        p1 = sketch.getPressedPosition()
        p2 = sketch.getCurrentPosition()

        sketch.addLine(Line(p1, p2))
        sketch.update()

    def mouseMoved(self, sketch):
        if sketch.isMousePressed():
            sketch.lines[-1].p2 = sketch.getCurrentPosition()


class PointDrawing(Handler):

    def mousePressed(self, sketch):
        point = sketch.getPressedPosition()
        sketch.addPoint(point)
        sketch.update()


class Constraint(object):

    @abstractmethod
    def apply(self, system: System, x: np.ndarray, y: np.ndarray, n: int):
        pass


class Parallel(Constraint):

    def __init__(self, l1: Line, l2: Line):
        self.l1 = l1
        self.l2 = l2

    @property
    def p1(self) -> Point:
        return self.l1.p1

    @property
    def p2(self) -> Point:
        return self.l1.p2

    @property
    def p3(self) -> Point:
        return self.l2.p1

    @property
    def p4(self) -> Point:
        return self.l2.p2

    def apply(self, system: System, x: np.ndarray, y: np.ndarray, n: int):
        i1 = system.points.index(self.p1) * 2
        i2 = system.points.index(self.p2) * 2
        i3 = system.points.index(self.p3) * 2
        i4 = system.points.index(self.p4) * 2

        y[i1] -= (x[i4 + 1] - x[i3 + 1]) * x[n]
        y[i2] += (x[i4 + 1] - x[i3 + 1]) * x[n]
        y[i3] += (x[i2 + 1] - x[i1 + 1]) * x[n]
        y[i4] -= (x[i2 + 1] - x[i1 + 1]) * x[n]

        y[i1 + 1] += (x[i4] - x[i3]) * x[n]
        y[i2 + 1] -= (x[i4] - x[i3]) * x[n]
        y[i3 + 1] -= (x[i2] - x[i1]) * x[n]
        y[i4 + 1] += (x[i2] - x[i1]) * x[n]

        y[n] = (x[i2] - x[i1]) * (x[i4 + 1] - x[i3 + 1]) - (x[i2 + 1] - x[i1 + 1]) * (x[i4] - x[i3])


class ParallelHandler(Handler):

    def __init__(self):
        self.l1 = None

    def mousePressed(self, sketch):
        if not self.l1:
            line = sketch.getActiveLine()
            if line:
                self.l1 = line
        else:
            l2 = sketch.getActiveLine()
            if l2:
                constraint = Parallel(self.l1, l2)
                self.l1 = None

                sketch.system.addConstraint(constraint)
                sketch.update()


class Length(Constraint):

    def __init__(self, line: Line, length: float):
        self.line = line
        self.length = length

    @property
    def p1(self) -> Point:
        return self.line.p1

    @property
    def p2(self) -> Point:
        return self.line.p2

    def apply(self, system: System, x: np.ndarray, y: np.ndarray, n: int):
        i1 = system.points.index(self.p1) * 2
        i2 = system.points.index(self.p2) * 2

        dx = x[i2] - x[i1]
        dy = x[i2 + 1] - x[i1 + 1]

        y[i2] += 2 * x[n] * dx
        y[i1] -= 2 * x[n] * dx

        y[i2 + 1] += 2 * x[n] * dy
        y[i1 + 1] -= 2 * x[n] * dy

        y[n] = dx ** 2 + dy ** 2 - self.length ** 2


class LengthHandler(Handler):

    def __init__(self, length: float):
        self.length = length

    def mousePressed(self, sketch):
        line = sketch.getActiveLine()
        if line:
            constraint = Length(line, self.length)
            sketch.system.addConstraint(constraint)
            sketch.update()


class AngleHandler(Handler):

    def __init__(self, angle: float):
        self.angle = angle

    def mousePressed(self, sketch):
        line = sketch.getActiveLine()
        if line:
            constraint = Angle(line, self.angle)
            sketch.system.addConstraint(constraint)
            sketch.update()


class FixingX(Constraint):

    def __init__(self, point: Point, value: float):
        self.point = point
        self.value = value

    def apply(self, system: System, x: np.ndarray, y: np.ndarray, n: int):
        i = system.points.index(self.point) * 2

        y[i] += x[n]

        y[n] = x[i] - self.value


class FixingY(Constraint):

    def __init__(self, point: Point, value: float):
        self.point = point
        self.value = value

    def apply(self, system: System, x: np.ndarray, y: np.ndarray, n: int):
        i = system.points.index(self.point) * 2 + 1

        y[i] += x[n]

        y[n] = x[i] - self.value


class FixingHandler(Handler):

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def mousePressed(self, sketch):
        point = sketch.getActivePoint()
        if point:
            sketch.system.addConstraint(FixingX(point, self.x))
            sketch.system.addConstraint(FixingY(point, self.y))


class Angle(Constraint):

    def __init__(self, line: Line, angle: float):
        self.line = line
        self.tan = np.tan(angle * np.pi / 180)

    @property
    def p1(self) -> Point:
        return self.line.p1

    @property
    def p2(self) -> Point:
        return self.line.p2

    def apply(self, system: System, x: np.ndarray, y: np.ndarray, n: int):
        i1 = system.points.index(self.p1) * 2
        i2 = system.points.index(self.p2) * 2

        y[i2] += x[n]
        y[i1] -= x[n]

        y[i2 + 1] += x[n] * self.tan
        y[i1 + 1] -= x[n] * self.tan

        y[n] = x[i2 + 1] - x[i1 + 1] - (x[i2] - x[i1]) * self.tan


class VerticalHandler(Handler):

    def mousePressed(self, sketch):
        line = sketch.getActiveLine()
        if line:
            sketch.system.addConstraint(Vertical(line))
            sketch.update()

class VerticalLineHandler(Handler):

    def __init__(self):
        self.p1 = None

    def mousePressed(self, sketch):
        if not self.p1:
            self.p1 = Point(sketch.getPressedPosition().x, 0)  # Set the first point to the top of the canvas

    def mouseReleased(self, sketch):
        if self.p1:
            p2 = Point(self.p1.x, sketch.height())  # Set the second point to the bottom of the canvas
            sketch.addLine(Line(self.p1, p2))
            sketch.update()
            self.p1 = None

class HorizontalHandler(Handler):

    def mousePressed(self, sketch):
        line = sketch.getActiveLine()
        if line:
            constraint = Horizontal(line)
            sketch.system.addConstraint(constraint)
            sketch.update()

class HorizontalLineHandler(Handler):

    def __init__(self):
        self.p1 = None

    def mousePressed(self, sketch):
        if not self.p1:
            self.p1 = Point(0, sketch.getPressedPosition().y)  # Set the first point to the left edge of the canvas

    def mouseReleased(self, sketch):
        if self.p1:
            p2 = Point(sketch.width(), self.p1.y)  # Set the second point to the right edge of the canvas
            sketch.addLine(Line(self.p1, p2))
            sketch.update()
            self.p1 = None

class CircleDrawingHandler(Handler):
    def __init__(self):
        self.center = None
        self.radius = None

    def mousePressed(self, sketch):
        if not self.center:
            self.center = sketch.getPressedPosition()

    def mouseReleased(self, sketch):
        if self.center:
            radius = self.center.distToPoint(sketch.currentPos)
            sketch.addCircle(Circle(self.center, radius))
            sketch.update()
            self.center = None

    def mouseMoved(self, sketch):
        if self.center:
            self.radius = self.center.distToPoint(sketch.currentPos)
            sketch.update()

    def draw(self, painter):
        if self.center:
            painter.setPen(pen.line)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))  # Transparent fill
            painter.drawEllipse(self.center.toQtPoint(), int(self.radius), int(self.radius))

class Vertical(Constraint, Handler):

    def __init__(self, line: Line):
        self.line = line

    @property
    def p1(self) -> Point:
        return self.line.p1

    @property
    def p2(self) -> Point:
        return self.line.p2

    def apply(self, system: System, x: np.ndarray, y: np.ndarray, n: int):
        i1 = system.points.index(self.p1) * 2
        i2 = system.points.index(self.p2) * 2

        y[i2] += x[n]
        y[i1] -= x[n]

        y[n] = x[i2] - x[i1]


class Horizontal(Constraint):

    def __init__(self, line: Line):
        self.line = line

    @property
    def p1(self) -> Point:
        return self.line.p1

    @property
    def p2(self) -> Point:
        return self.line.p2

    def apply(self, system: System, x: np.ndarray, y: np.ndarray, n: int):
        i1 = system.points.index(self.p1) * 2 + 1
        i2 = system.points.index(self.p2) * 2 + 1

        y[i2] += x[n]
        y[i1] -= x[n]

        y[n] = x[i2] - x[i1]

class EraserHandler(Handler):

    def __init__(self):
        self.selected_object = None

    def getActiveLine(self, sketch):
        for line in sketch.lines:
            if line.hasPoint(sketch.currentPos, 4):
                return line
        return None

    def mousePressed(self, sketch):
        self.selected_object = self.getActiveLine(sketch)

    def mouseReleased(self, sketch):
        if self.selected_object:
            sketch.lines.remove(self.selected_object)
            self.selected_object = None

    def mouseMoved(self, sketch):
        pass  # Implement this if needed
class MoveObjectHandler(Handler):
    def __init__(self):
        self.selected_object = None
        self.offset = Point(0, 0)

    def mousePressed(self, sketch):
        if not self.selected_object:
            for line in sketch.lines:
                if line.hasPoint(sketch.currentPos, 4):
                    self.selected_object = line
                    self.offset = Point(sketch.currentPos.x - line.p1.x, sketch.currentPos.y - line.p1.y)
                    break
            for point in sketch.points:
                if point.distToPoint(sketch.currentPos) < 4:
                    self.selected_object = point
                    self.offset = Point(0, 0)
                    break

    def mouseReleased(self, sketch):
        self.selected_object = None

    def mouseMoved(self, sketch):
        if self.selected_object:
            new_pos = Point(sketch.currentPos.x - self.offset.x, sketch.currentPos.y - self.offset.y)
            if isinstance(self.selected_object, Line):
                delta_x = new_pos.x - self.selected_object.p1.x
                delta_y = new_pos.y - self.selected_object.p1.y
                self.selected_object.p1 = new_pos
                self.selected_object.p2 = Point(self.selected_object.p2.x + delta_x, self.selected_object.p2.y + delta_y)
            elif isinstance(self.selected_object, Point):
                self.selected_object.x = new_pos.x
                self.selected_object.y = new_pos.y
            sketch.update()

class CoincidentHandler(Handler):

    def __init__(self):
        self.p1 = None

    def mousePressed(self, sketch):
        point = sketch.getActivePoint()
        if point:
            if not self.p1:
                self.p1 = point
                return True
            else:
                sketch.system.addConstraint(CoincidentX(self.p1, point))
                sketch.system.addConstraint(CoincidentY(self.p1, point))

                self.p1 = None
                sketch.update()


class CoincidentX(Constraint):

    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def apply(self, system: System, x: np.ndarray, y: np.ndarray, n: int):
        i1 = system.points.index(self.p1) * 2
        i2 = system.points.index(self.p2) * 2

        y[i2] += x[n]
        y[i1] -= x[n]

        y[n] = x[i2] - x[i1]


class CoincidentY(Constraint):

    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def apply(self, system: System, x: np.ndarray, y: np.ndarray, n: int):
        i1 = system.points.index(self.p1) * 2 + 1
        i2 = system.points.index(self.p2) * 2 + 1

        y[i2] += x[n]
        y[i1] -= x[n]

        y[n] = x[i2] - x[i1]
