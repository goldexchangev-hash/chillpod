"""Print-tune the ChillPod body and cap for a Bambu Lab H2D.

Reads the Rev 1 STLs and writes:
  stl/Body_H2D.stl           same exterior and phone slot, thinner inner walls,
                             bridge ribs under the slot floor
  stl/Lid_H2D.stl            deeper grip flutes, hollowed crown
  stl/Neck_Support_H2D.stl   snap-off cradle under the horizontal neck
                             (separate object, aligned to the body)

Run from the repo root:  python3 tools/optimize_print.py
"""

from __future__ import annotations

import numpy as np
import trimesh
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STL = ROOT / "stl"
BODY_IN = STL / "Body_Rev1_original.stl"
LID_IN = STL / "Lid_Rev1_original.stl"

# Interior walls go from 2.00 mm to this. 1.68 mm is four 0.42 mm perimeters
# on a 0.4 mm H2D nozzle, which stays watertight in PETG.
WALL = 1.68
CUT = 2.00 - WALL  # 0.32 mm shaved off the cavity side only


def box(xmin, xmax, ymin, ymax, zmin, zmax) -> trimesh.Trimesh:
    ext = np.array([xmax - xmin, ymax - ymin, zmax - zmin], dtype=float)
    center = np.array([(xmin + xmax) / 2, (ymin + ymax) / 2, (zmin + zmax) / 2])
    mesh = trimesh.creation.box(extents=ext)
    mesh.apply_translation(center)
    return mesh


def concat(meshes) -> trimesh.Trimesh:
    return trimesh.util.concatenate(meshes)


def must_be_solid(mesh, pts, label):
    pts = np.asarray(pts, dtype=float)
    inside = mesh.contains(pts)
    bad = pts[~inside]
    if len(bad):
        raise SystemExit(f"{label}: expected solid, but these points are empty:\n{bad[:8]}")


def must_be_empty(mesh, pts, label):
    pts = np.asarray(pts, dtype=float)
    inside = mesh.contains(pts)
    bad = pts[inside]
    if len(bad):
        raise SystemExit(f"{label}: expected empty, but these points are solid:\n{bad[:8]}")


def sphere_y(r, crown=18.42, radius=11.0):
    """Inner cap dome: sphere, crown at y=crown, radius 11 mm."""
    r = float(r)
    r = min(abs(r), radius)
    return crown - (radius - np.sqrt(radius ** 2 - r ** 2))


def revolve(loop_ry, n=160) -> trimesh.Trimesh:
    """Revolve a closed (r, y) loop around Y. r must stay positive."""
    loop = np.asarray(loop_ry, dtype=float)
    if np.linalg.norm(loop[0] - loop[-1]) > 1e-6:
        loop = np.vstack([loop, loop[0]])
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    rings = []
    for r, y in loop[:-1]:
        rings.append(
            np.column_stack(
                [r * np.cos(angles), np.full(n, y), r * np.sin(angles)]
            )
        )
    rings = np.stack(rings, axis=0)  # (nr, n, 3)
    nr = rings.shape[0]
    verts = rings.reshape(-1, 3)
    faces = []
    for i in range(nr):
        i2 = (i + 1) % nr
        for j in range(n):
            j2 = (j + 1) % n
            a = i * n + j
            b = i * n + j2
            c = i2 * n + j
            d = i2 * n + j2
            faces.append([a, c, b])
            faces.append([b, c, d])
    mesh = trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=False)
    mesh.fix_normals()
    mesh.remove_unreferenced_vertices()
    return mesh


def build_body(body: trimesh.Trimesh) -> trimesh.Trimesh:
    # Shave the cavity side of the big flat walls. Exterior, phone-slot
    # opening, and neck threads are not touched. Boxes overlap the cavity
    # by 0.06 mm so the cut does not leave a coplanar skin.
    c = CUT
    cuts = [
        # bottom skin, inner face was z=2
        box(10, 110, 22, 190, 2.0 - c, 2.06),
        # top rails beside the phone slot, inner face was z=29
        box(4.0, 14.6, 24, 186, 29.0 - 0.06, 29.0 + c),
        box(105.4, 116.0, 24, 186, 29.0 - 0.06, 29.0 + c),
        # top skin at the closed end and just before the neck pocket
        box(10, 110, 8, 16.5, 29.0 - 0.06, 29.0 + c),
        box(10, 110, 190.2, 193.2, 29.0 - 0.06, 29.0 + c),
        # long side walls, inner faces were x=2 and x=118
        box(2.0 - c, 2.06, 22, 188, 8, 27),
        box(117.94, 118.0 + c, 22, 188, 8, 27),
        # phone-slot walls, water side only (slot opening stays put)
        box(15.75 - 0.04, 15.75 + c, 26, 182, 18.2, 27.2),
        box(104.25 - c, 104.25 + 0.04, 26, 182, 18.2, 27.2),
        # slot floor, water side only (phone still sits on z=17)
        box(22, 98, 26, 182, 15.0 - 0.04, 15.0 + c),
    ]

    samples = {
        "bottom": [[60, 100, 1.84], [20, 40, 1.84], [100, 170, 1.84]],
        "rail": [[8, 100, 29.2], [110, 80, 29.2], [60, 12, 29.2]],
        "side": [[1.7, 100, 16], [118.3, 100, 16]],
        "slotwall": [[15.9, 100, 22], [104.1, 100, 22]],
        "floor": [[60, 100, 15.15], [40, 60, 15.15]],
    }
    for name, pts in samples.items():
        must_be_solid(body, pts, name)

    # These must survive: outer skin, phone contact face, neck bore wall.
    keep = [
        [0.4, 100, 16],
        [60, 100, 16.6],
        [119.6, 100, 16],
        [69.0, 205, 15.5],  # neck wall, r=9 (bore is r=8, thread root is r=10)
        [60, 12, 30.2],
    ]
    must_be_solid(body, keep, "keep-before")

    print("cutting inner walls...")
    carved = trimesh.boolean.difference([body, concat(cuts)], engine="manifold")
    if not carved.is_watertight:
        raise SystemExit("body not watertight after wall cut")
    must_be_empty(carved, [[60, 100, 1.84], [8, 100, 29.16], [1.75, 100, 16]], "after-cut")
    must_be_solid(carved, [[60, 100, 0.6], [60, 100, 16.5], [0.4, 100, 16]], "after-cut-keep")

    # Ribs under the slot floor. They run across the width so the 84 mm
    # floor bridges about 20 mm instead of 84 mm. A notch on the bottom
    # keeps the water as one volume.
    rib_meshes = []
    for y in (32, 52, 72, 92, 112, 132, 152, 172):
        rib = box(12, 108, y - 0.5, y + 0.5, 1.62, 15.40)
        notch = box(52, 68, y - 0.7, y + 0.7, 1.40, 6.6)
        rib = trimesh.boolean.difference([rib, notch], engine="manifold")
        rib_meshes.append(rib)
    print("adding bridge ribs...")
    out = trimesh.boolean.union([carved, concat(rib_meshes)], engine="manifold")
    if not out.is_watertight:
        raise SystemExit("body not watertight after ribs")
    # Rib occupies the cavity; slot above the floor stays empty.
    must_be_solid(out, [[40, 32, 10], [90, 112, 12]], "rib")
    must_be_empty(out, [[60, 32, 4], [60, 100, 20], [60, 100, 3]], "channels")
    return out


def build_lid(lid: trimesh.Trimesh) -> trimesh.Trimesh:
    cx, cz = 15.43123555, 15.65006935

    # Deeper flutes in the existing 18-scallop grip. Valleys were only
    # 0.35 mm, which a 0.4 mm nozzle barely reproduces.
    flutes = []
    length = 19.0 - 1.6
    for i in range(18):
        ang = np.radians(i * 20.0 + 10.0)  # center the cut on a valley
        # Cylinder axis along Y, sitting just outside the skirt.
        cyl = trimesh.creation.cylinder(radius=1.15, height=length, sections=28)
        # creation.cylinder is along Z. Rotate onto Y.
        cyl.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
        radial = 15.55
        cyl.apply_translation(
            [cx + radial * np.cos(ang), 1.6 + length / 2, cz + radial * np.sin(ang)]
        )
        flutes.append(cyl)

    # Hollow the solid crown. Leave ~2.0 mm under the flat top and ~1.7 mm
    # over the inner dome so the cap still feels solid.
    rs = np.linspace(0.6, 12.4, 28)
    bottom = []
    for r in rs:
        if r < 11.0:
            by = float(sphere_y(r) + 1.70)
        else:
            by = 13.4
        by = max(by, 13.4)
        if by > 20.6:
            continue
        bottom.append((float(r), by))
    if len(bottom) < 4:
        raise SystemExit("crown cutter profile collapsed")
    top = [(r, 20.95) for r, _ in bottom]
    loop = bottom + top[::-1]
    cutter = revolve(loop, n=144)
    # Close the small axial hole left by revolving a loop that stays off r=0.
    plug = trimesh.creation.cylinder(radius=0.9, height=0.9, sections=24)
    plug.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    plug.apply_translation([0, 20.50, 0])
    cutter = trimesh.boolean.union([cutter, plug], engine="manifold")
    cutter.apply_translation([cx, 0, cz])

    # Every cutter sample must already be plastic. Threads and the outside stay.
    probe = []
    for r, y in bottom[::3]:
        probe.append([cx + r * 0.85, (y + 20.95) / 2, cz])
    probe.append([cx, 20.4, cz])
    probe.append([cx + 8, 18.5, cz])
    must_be_solid(lid, probe, "crown-cutter")
    must_be_solid(lid, [[cx + 13.2, 6.0, cz], [cx + 14.6, 8.0, cz]], "lid-keep")

    print("cutting flutes and hollowing cap...")
    out = trimesh.boolean.difference([lid, concat(flutes), cutter], engine="manifold")
    if not out.is_watertight:
        raise SystemExit("lid not watertight")
    must_be_empty(out, [[cx, 20.4, cz], [cx + 6.0, 19.5, cz]], "crown-void")
    must_be_solid(out, [[cx, 22.4, cz], [cx + 13.2, 6.0, cz], [cx, 18.7, cz]], "lid-remain")
    return out


def neck_bottom(body, x, y):
    loc, _, _ = body.ray.intersects_location(
        np.array([[x, y, -2.0]]), np.array([[0.0, 0.0, 1.0]]), multiple_hits=True
    )
    if len(loc) == 0:
        return None
    return float(np.min(loc[:, 2]))


def build_support(body: trimesh.Trimesh) -> trimesh.Trimesh:
    """Snap-off cradle under the belly of the horizontal neck.

    Fins stop 0.48 mm short of the lowest point of the neck over each fin,
    so they support the threads without welding to them. Only the underside
    that actually overhangs (below z=8.6) is cradled. A tab past the spout
    gives something to peel.
    """
    parts = []
    xs = np.linspace(50.5, 69.5, 28)
    ys = (200.5, 203.0, 205.5, 208.0, 210.4)
    half_t = 0.24  # 0.48 mm fin, one nozzle line
    for y in ys:
        for x0, x1 in zip(xs[:-1], xs[1:]):
            samples = []
            for yy in (y - half_t, y, y + half_t):
                for xx in (x0, (x0 + x1) / 2, x1):
                    z = neck_bottom(body, xx, yy)
                    if z is not None and 1.2 < z < 8.6:
                        samples.append(z)
            if len(samples) < 2:
                continue
            top = min(samples) - 0.48
            if top <= 0.50:
                continue
            parts.append(box(x0 - 0.02, x1 + 0.02, y - half_t, y + half_t, 0.42, top))
    parts.append(box(52.0, 68.0, 200.0, 210.8, 0.0, 0.48))
    parts.append(box(54.5, 65.5, 210.5, 218.5, 0.0, 2.2))
    support = concat(parts)
    support = trimesh.boolean.difference([support, body], engine="manifold")
    support.remove_unreferenced_vertices()
    # Thread flanks get closer to a fin's side than the sampled underside.
    # Nudge any vertex that would fuse until it sits 0.28 mm off the bottle.
    for _ in range(4):
        closest, dist, _ = trimesh.proximity.closest_point(body, support.vertices)
        close = dist < 0.28
        if not np.any(close):
            break
        delta = support.vertices[close] - closest[close]
        norm = np.linalg.norm(delta, axis=1, keepdims=True)
        norm = np.maximum(norm, 1e-6)
        support.vertices[close] = closest[close] + delta / norm * 0.30
    _closest, dist, _ = trimesh.proximity.closest_point(body, support.vertices)
    gap = float(dist.min()) if len(dist) else 0.0
    print(f"support clearance min {gap:.3f} mm")
    if gap < 0.18:
        raise SystemExit("neck support is too close to the body and would fuse")
    return support


def report(name, original, updated):
    saved = original.volume - updated.volume
    print(
        f"{name}: {original.volume/1000:.1f} cm³ -> {updated.volume/1000:.1f} cm³  "
        f"saved {saved/1000:.1f} cm³ ({100*saved/original.volume:.1f}%)  "
        f"watertight {updated.is_watertight}"
    )


def main():
    body = trimesh.load(BODY_IN, force="mesh")
    lid = trimesh.load(LID_IN, force="mesh")
    body_out = build_body(body)
    lid_out = build_lid(lid)
    support = build_support(body)
    report("body", body, body_out)
    report("lid", lid, lid_out)
    print(
        f"support: {support.volume/1000:.2f} cm³  faces {len(support.faces)}  "
        f"watertight {support.is_watertight}  bounds z {support.bounds[:,2]}"
    )

    # Fit checks against the original design.
    # Phone slot opening at z=22 should still read ~84.5 mm inside.
    def slot_width(mesh, y=100, z=22):
        loc, _, _ = mesh.ray.intersects_location(
            np.array([[-5.0, y, z]]), np.array([[1.0, 0.0, 1e-9]]), multiple_hits=True
        )
        xs = np.sort(loc[:, 0])
        # innermost pair around the slot
        return xs

    print("slot rays x", np.round(slot_width(body_out), 2))
    print("outer bounds", np.round(body_out.bounds, 2))
    print("lid bounds", np.round(lid_out.bounds, 2))

    lid_print = orient_lid_for_print(lid_out)
    body_out.export(STL / "Body_H2D.stl")
    lid_print.export(STL / "Lid_H2D.stl")
    support.export(STL / "Neck_Support_H2D.stl")
    print("lid print bounds", np.round(lid_print.bounds, 2), "watertight", lid_print.is_watertight)
    print("wrote STLs")


def orient_lid_for_print(lid: trimesh.Trimesh) -> trimesh.Trimesh:
    """Drop the cap on its flat top, opening facing up, ready for the H2D bed."""
    lid = lid.copy()
    y_top = float(lid.bounds[1, 1])
    v = np.array(lid.vertices)
    x, y, z = v[:, 0], v[:, 1], v[:, 2]
    lid.vertices = np.column_stack([x - x.min(), z - z.min(), y_top - y])
    return lid


if __name__ == "__main__":
    main()
