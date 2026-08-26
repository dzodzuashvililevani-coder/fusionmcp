# Component measurements

Fill this in with a caliper, then copy the numbers into `params.yaml`.
Photograph each part next to a ruler and drop it in `photos/`.

## Motor
- [ ] Bolt circle (hole to hole, across the base): ____ mm
- [ ] Screw thread (M1.4 / M2 / M3): ____
- [ ] Base diameter: ____ mm
- [ ] Height incl. shaft: ____ mm
- [ ] Mass (one motor): ____ g
- [ ] Stator size stamped on it (e.g. 1103, 1104): ____
- [ ] KV rating if printed: ____

## Propellers
- [ ] Diameter: ____ mm   (2"=51, 2.5"=63.5, 3"=76.2)
- [ ] Shaft hole diameter: ____ mm
- [ ] Blade count: ____

## Flight controller
- [ ] Mounting hole pattern (square, hole to hole): ____ mm  (16 / 20 / 25.5 / 30.5)
- [ ] Board size: ____ x ____ mm
- [ ] Screw size: ____
- [ ] Mass: ____ g
- [ ] ESCs integrated on the board, or separate? ____

## ESCs (if separate)
- [ ] Size: ____ x ____ mm     - [ ] Mass each: ____ g
- [ ] Current rating: ____ A

## Battery
- [ ] L x W x H: ____ x ____ x ____ mm
- [ ] Mass: ____ g   - [ ] Cell count / voltage: ____   - [ ] Capacity: ____ mAh
- [ ] Connector type: ____

## Camera
- [ ] Body width: ____ mm   - [ ] Mount ear spacing: ____ mm
- [ ] Mass: ____ g   - [ ] Lens protrusion: ____ mm

## VTX / receiver / antenna
- [ ] VTX size and mass: ____
- [ ] Receiver mass: ____   - [ ] Antenna mass and length: ____

## Wood stock
- [ ] Actual thickness (measure, do not trust the label): ____ mm
- [ ] Species / type: ____
- [ ] Sheet size: ____ x ____ mm
- [ ] Cutting method: laser / CNC / jigsaw
- [ ] Kerf: run `frame kerf-test`, cut `dxf/kerf_test.dxf`, then
      kerf = nominal - measured: ____ mm  -> `stock.kerf_mm`

## Screws and holes
- [ ] Motor screw size (M1.4 / M2 / M3): ____   -> `params.yaml motors.screw`
- [ ] FC standoff screw size: ____              -> `center_plate.fc_screw`
- [ ] Clearance needed for a screw to drop through YOUR plywood: ____ mm
      Start at 0.3, test it on the kerf coupon -> `holes.screw_clearance_mm`
- [ ] Battery strap width: ____ mm              -> `holes.ziptie_slot_mm`

## Motor thrust
No datasheet for a salvaged Temu motor. Measure it:
tape the motor to a kitchen scale (upside down, pushing DOWN),
run it to 100% throttle, read the grams.
- [ ] Max thrust per motor: ____ g

---

Once every blank above is filled and copied into `params.yaml`, `frame report`
must end with **0 failures** before anything reaches the cutter. Keep this file
even after copying: it is how you tell a mis-measurement from a mis-typing.
