"""Named exceptions for FusionControlCenter support code."""


class FccError(Exception):
    """Base class for FCC errors."""


class SpecError(FccError):
    """A field spec is invalid or inconsistent with project files."""


class UnsurgicalEdit(FccError):
    """A requested write cannot be made without reformatting a file."""


class LabelNotFound(FccError):
    """A measurements.md label could not be found."""


class PathRefused(FccError):
    """A path was outside the allowed project boundary."""
