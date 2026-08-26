"""Generate the small DXF files that do not need Fusion.

Deliberately narrow. The *frame* cut file comes out of Fusion via
`fusion_scripts/export_dxf.py` -- generating it twice, from two different
geometry engines, is how a DXF and a model silently diverge.

What lives here is the calibration coupon, which has no 3D model to export
from and which you need *before* the first real cut.

`ezdxf` is an optional dependency:  uv pip install -e ".[dxf]"
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .params import hole_diameter_mm

# Layer names are the convention in dxf/README.md. Colours are AutoCAD indices;
# most cutter software keys off the layer name, but the colours make the file
# readable if you open it in a viewer first.
LAYERS = {
    "CUT": 1,        # red
    "HOLES": 5,      # blue
    "ENGRAVE": 3,    # green
    "REFERENCE": 8,  # grey - never sent to the machine
}

KERF_SQUARE_SIZES_MM = (5.0, 10.0, 15.0, 20.0)
COUPON_GAP_MM = 6.0
LABEL_HEIGHT_MM = 3.0


def _require_ezdxf():
    try:
        import ezdxf  # noqa: PLC0415 - optional dependency, imported on use
    except ImportError as exc:  # pragma: no cover - depends on the install extras
        raise ImportError(
            "ezdxf is not installed. Run:  uv pip install -e \".[dxf]\""
        ) from exc
    return ezdxf


def _new_doc(ezdxf):
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    for name, colour in LAYERS.items():
        if name not in doc.layers:
            doc.layers.add(name, color=colour)
    return doc


def _square(msp, x: float, y: float, size: float) -> None:
    msp.add_lwpolyline(
        [(x, y), (x + size, y), (x + size, y + size), (x, y + size)],
        close=True,
        dxfattribs={"layer": "CUT"},
    )


def _label(ezdxf, msp, text: str, x: float, y: float) -> None:
    from ezdxf.enums import TextEntityAlignment  # noqa: PLC0415 - needs ezdxf present

    entity = msp.add_text(text, dxfattribs={"layer": "ENGRAVE", "height": LABEL_HEIGHT_MM})
    entity.set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)


def write_kerf_test(p: dict[str, Any], path: Path) -> tuple[Path, list[float]]:
    """Write a kerf calibration coupon. Returns (path, nominal square sizes).

    Cut it, measure a square with calipers: the cutter removes half a kerf from
    each side, so  kerf = nominal - measured. The screw holes on the same coupon
    tell you whether your `holes.screw_clearance_mm` actually lets a screw drop
    through this particular wood.
    """
    ezdxf = _require_ezdxf()
    doc = _new_doc(ezdxf)
    msp = doc.modelspace()

    sizes = list(KERF_SQUARE_SIZES_MM)
    x = 0.0
    top = max(sizes)
    for size in sizes:
        _square(msp, x, 0.0, size)
        _label(ezdxf, msp, f"{size:g}", x + size / 2.0, -LABEL_HEIGHT_MM * 1.5)
        x += size + COUPON_GAP_MM

    # A row of screw holes at the sizes this design actually drills, so one
    # coupon answers both "what is my kerf" and "does an M2 drop through".
    screws = sorted({str(p["motors"]["screw"]), str(p["center_plate"]["fc_screw"])})
    hole_y = top + COUPON_GAP_MM * 2
    hx = 0.0
    for screw in screws:
        dia = hole_diameter_mm(p, screw)
        msp.add_circle((hx + dia / 2, hole_y), dia / 2, dxfattribs={"layer": "HOLES"})
        _label(ezdxf, msp, screw, hx + dia / 2, hole_y + dia / 2 + LABEL_HEIGHT_MM)
        hx += dia + COUPON_GAP_MM

    # Stock outline, so you can see the coupon is nowhere near the sheet limit.
    sw, sh = p["stock"]["size_mm"]
    msp.add_lwpolyline(
        [(-10, -10), (sw - 10, -10), (sw - 10, sh - 10), (-10, sh - 10)],
        close=True,
        dxfattribs={"layer": "REFERENCE"},
    )

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(path)
    return path, sizes
