"""
This module initializes the core components of the beam analysis package.

It imports the following classes:
- Beam: Represents a beam in the analysis.
- TrainLoad: Represents a train load applied to the beam.
- CrossSection: Represents the cross-sectional geometry of the beam.
- Rectangle: Represents a rectangular cross-section.

The `__all__` list defines the public interface of this module, specifying
the classes that will be available when the module is imported.

Attributes:
    Beam (class): Represents a beam in the analysis.
    TrainLoad (class): Represents a train load applied to the beam.
    CrossSection (class): Represents the cross-sectional geometry of the beam.
    Rectangle (class): Represents a rectangular cross-section.
"""
from .beam import Beam
from .loads import TrainLoad
from .geometry import CrossSection, Rectangle

__all__ = ["Beam", "TrainLoad", "CrossSection", "Rectangle"]