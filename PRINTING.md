# Printing the ChillPod bottle and cap (Bambu Lab H2D)

These files are a print-tuned Rev 2 of `Body_Rev 1` and `Lid_Rev 1`. The outside shape, the phone slot, and the screw threads are unchanged. What changed is only what the printer and the freezer care about.

| File | What to do with it |
| --- | --- |
| `stl/Body_H2D.stl` | The bottle. Already sitting on its flat back. |
| `stl/Lid_H2D.stl` | The cap. Already sitting on its flat top, opening up. |
| `stl/Neck_Support_H2D.stl` | Optional snap-off cradle for the spout. Same coordinates as the body. |
| `stl/Body_Rev1_original.stl` | Untouched Rev 1, for comparison. |
| `stl/Lid_Rev1_original.stl` | Untouched Rev 1 cap. |

Regenerate with `python3 tools/optimize_print.py`.

## What changed

**Bottle, same silhouette.** Outer size is still 120 × 215 × 31 mm. The phone opening is still 84.5 mm wide and the floor the phone sits on is still at the same height. Threads on the spout are the original profile (4 mm pitch, about 0.30 mm of radial clearance), so this cap fits this spout and a Rev 1 cap still fits.

**The tank ceiling can bridge.** Printed flat, the floor under the phone is an 84 mm bridge over the water tank. That sags and leaks. Eight 1 mm ribs now run across the tank every 20 mm, so the bridge is about 20 mm. Each rib has a notch along the bottom, so the water is still one volume and ice can expand through them instead of being locked in pockets.

**Walls are 1.68 mm on the big flat faces** (they were 2.0 mm). That is four perimeters at a 0.42 mm line width. Fillets, the spout, and the phone-contact surfaces stay as they were. This is as thin as a freezer bottle should go: water expands about 9% when it freezes, and a thinner wall splits along the layers.

**Cap uses less plastic and is easier to grip.** The crown was solid. It is now a hollow shell about 2 mm thick under the top and about 1.7 mm over the inner dome (saved 2.8 cm³, 26%). The old scallops were only 0.35 mm deep, which a 0.4 mm nozzle barely shows. They are now flutes about 0.9 mm deep. The lip and the threads are unchanged.

**Spout cradle.** The spout sticks out of the end and its underside is in mid-air. `Neck_Support_H2D.stl` is a comb that stands on the bed 0.28 mm under the belly of the spout, with a tab past the opening so you can peel it off. It does not touch the bottle, so it will not weld on.

Plastic volume: bottle 148.2 → 144.5 cm³ (the ribs spend most of what the thinner walls save), cap 10.9 → 8.1 cm³. In PETG that is roughly 8 g less for the pair.

## H2D settings

The H2D bed is large enough to print this flat. Do not stand the bottle on its end: the broad faces would be stacked layers, and that is the direction ice blows out.

- **Material: PETG** (Bambu PETG HF or PETG). PLA gets brittle in the freezer and cracks when the ice expands. Dry the spool.
- **Nozzle: 0.4 mm.** Line width 0.42 mm. Layer height 0.20 mm (first layer 0.20 mm).
- **Wall loops: 6.** The modeled walls are 1.68–2.0 mm, so six loops make them solid with no sparse infill in the skin. Infill 10% gyroid is only a fallback.
- **Top/bottom shells: 5.** No ironing on the phone floor (it can leave a ridge).
- **Seam: aligned**, on a long edge, not across the spout.
- **Supports: On build plate only.** That lets the slicer hold up the spout and keeps it from building supports inside the tank, where you could never dig them out. The ribs are the tank ceiling's support. Turn on "don't support bridges" if you see support planned on the phone floor.
- If the auto supports under the threads look ragged, delete them and load `Neck_Support_H2D.stl` with the body (do not move it). Print it in PETG and snap it off, or assign it to the H2D's second nozzle with support-interface filament.
- **Cap: no supports, no brim.** Do not flip it. The flat top is already on the bed and the threads build upward, which is the clean direction.
- Brim on the bottle is optional. The back is a full flat face.

Before you trust it with water, fill it, screw the cap on firmly, and leave it on a paper towel for an hour. A cold seam weeps. If it weeps, a thin smear of food-safe silicone on the spout face is enough. The threads themselves are not a seal; the cap's dome seats on the mouth.

## Freezing

Leave about 10% empty. A bottle filled to the top will split no matter how it was printed. Freeze it upright so the air pocket stays at the spout.
