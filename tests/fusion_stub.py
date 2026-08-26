"""A fake `adsk` package, so the Fusion scripts can be exercised outside Fusion.

Not a mock of Fusion. It implements only the handful of API surfaces
`fusion_scripts/` actually touches, and it records what was asked of it.

What this catches: import errors, payload keys that do not exist, format-string
mistakes, unit-conversion slips, and logic bugs in the pure-Python parts
(`shelf_pack`, `bolt_circle`, `centre_of_mass_mm`).

What it cannot catch: whether Fusion's real API behaves the way we assume. A
green test here means the script will *run*; it does not mean the model will be
right. That still wants one careful pass in Fusion on a throwaway design.
"""
from __future__ import annotations

import sys
import types

CM_PER_MM = 0.1


# --- geometry primitives --------------------------------------------------
class Point3D:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = x, y, z

    @classmethod
    def create(cls, x, y, z=0.0):
        return cls(x, y, z)

    def __repr__(self):
        return f"Point3D({self.x:.4f}, {self.y:.4f}, {self.z:.4f})"


class BoundingBox:
    def __init__(self, min_point, max_point):
        self.minPoint, self.maxPoint = min_point, max_point


class ValueInput:
    def __init__(self, text):
        self.text = text

    @classmethod
    def createByString(cls, text):
        return cls(text)

    @classmethod
    def createByReal(cls, value):
        return cls(value)


# --- sketch entities ------------------------------------------------------
class _Collection(list):
    """A Fusion ObjectCollection is list-like; the scripts only iterate it."""


class SketchCircles(_Collection):
    def addByCenterRadius(self, centre, radius):
        entity = types.SimpleNamespace(kind="circle", centre=centre, radius=radius)
        self.append(entity)
        return entity


class SketchArcs(_Collection):
    def addByCenterStartSweep(self, centre, start, sweep):
        entity = types.SimpleNamespace(kind="arc", centre=centre, start=start, sweep=sweep)
        self.append(entity)
        return entity


class SketchLines(_Collection):
    def addByTwoPoints(self, a, b):
        entity = types.SimpleNamespace(kind="line", a=a, b=b)
        self.append(entity)
        return entity

    def addTwoPointRectangle(self, a, b):
        entity = types.SimpleNamespace(kind="rect", a=a, b=b)
        self.append(entity)
        return entity


class SketchCurves:
    def __init__(self):
        self.sketchCircles = SketchCircles()
        self.sketchArcs = SketchArcs()
        self.sketchLines = SketchLines()

    def __len__(self):
        return len(self.sketchCircles) + len(self.sketchArcs) + len(self.sketchLines)


class Sketch:
    def __init__(self, name="Sketch1", extent_mm=None):
        self.name = name
        self.isComputeDeferred = False
        self.sketchCurves = SketchCurves()
        self.exported_to = []
        self._extent_mm = extent_mm

    @property
    def boundingBox(self):
        if self._extent_mm is None:
            return None
        w, h = self._extent_mm
        return BoundingBox(Point3D(0.0, 0.0, 0.0), Point3D(w * CM_PER_MM, h * CM_PER_MM, 0.0))

    def saveAsDXF(self, filename):
        self.exported_to.append(filename)
        return True


class Sketches(_Collection):
    def __init__(self, component):
        super().__init__()
        self._component = component

    def add(self, _plane):
        sketch = Sketch(name=f"Sketch{len(self) + 1}")
        self.append(sketch)
        return sketch


# --- bodies ---------------------------------------------------------------
class PhysicalProperties:
    def __init__(self, volume_cm3, centre_cm):
        self.volume = volume_cm3
        self.centerOfMass = centre_cm


class BRepBody:
    def __init__(self, name, volume_cm3, centre_cm=None, visible=True):
        self.name = name
        self.isVisible = visible
        self.physicalProperties = PhysicalProperties(volume_cm3, centre_cm or Point3D())


# --- parameters -----------------------------------------------------------
class UserParameter:
    def __init__(self, name, expression, unit, comment):
        self.name, self.expression, self.unit, self.comment = name, expression, unit, comment


class UserParameters(_Collection):
    def itemByName(self, name):
        for param in self:
            if param.name == name:
                return param
        return None

    def add(self, name, value_input, unit, comment):
        param = UserParameter(name, value_input.text, unit, comment)
        self.append(param)
        return param


# --- document -------------------------------------------------------------
class Component:
    def __init__(self, name="root"):
        self.name = name
        self.sketches = Sketches(self)
        self.bRepBodies = _Collection()
        self.xYConstructionPlane = object()


class Design:
    def __init__(self):
        self.rootComponent = Component()
        self.userParameters = UserParameters()

    @property
    def allComponents(self):
        return [self.rootComponent]

    @classmethod
    def cast(cls, obj):
        return obj if isinstance(obj, Design) else None


class UserInterface:
    def __init__(self):
        self.messages = []

    def messageBox(self, text, title=""):
        self.messages.append((title, text))
        return 0

    @property
    def last(self):
        return self.messages[-1][1] if self.messages else ""


class Application:
    _instance = None

    def __init__(self):
        self.userInterface = UserInterface()
        self.activeProduct = Design()

    @classmethod
    def get(cls):
        return cls._instance


def install(design=None):
    """Put a fake `adsk` on sys.path. Returns the Application.

    Call before importing anything from fusion_scripts/, and call `remove()`
    afterwards -- leaving a fake adsk behind would mask a real import error in
    another test.
    """
    app = Application()
    if design is not None:
        app.activeProduct = design
    Application._instance = app

    adsk = types.ModuleType("adsk")
    core = types.ModuleType("adsk.core")
    fusion = types.ModuleType("adsk.fusion")

    core.Application = Application
    core.Point3D = Point3D
    core.ValueInput = ValueInput
    core.ObjectCollection = _Collection
    fusion.Design = Design
    fusion.BRepBody = BRepBody
    fusion.FeatureOperations = types.SimpleNamespace(NewBodyFeatureOperation=0)

    adsk.core, adsk.fusion = core, fusion
    sys.modules["adsk"] = adsk
    sys.modules["adsk.core"] = core
    sys.modules["adsk.fusion"] = fusion
    return app


def remove():
    """Drop the fake adsk and every fusion_scripts module that imported it."""
    for name in ("adsk.core", "adsk.fusion", "adsk"):
        sys.modules.pop(name, None)
    for name in ("_common", "sync_params", "hole_pattern", "nest_parts",
                 "mass_check", "export_dxf"):
        sys.modules.pop(name, None)
    Application._instance = None
