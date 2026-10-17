#!/usr/bin/env python3
"""
SPIKE ONLY (P273, #309). Throwaway code, not part of spark. Nothing in scripts/ or tests/ imports it.

The question: when a person moves a part or a jumper in breadboard.json, can the next build keep the move, or name why
it cannot? This file tries one merge rule against spark's own planner, without changing it.

    python3 -I prototype.py EARLIER_BREADBOARD_JSON PROJECT_REQUIREMENTS_JSON OUT_JSON

EARLIER is the diagram the person edited. The project must be built with --keep (dist/board/circuit.json). Run it with
SPARK_HOME set to a scratch store, against copies in a temp folder.

The merge rule:
1. Every part of the earlier diagram whose id and Wokwi type are in the new circuit is reserved first, at its earlier
   position, when each pin lies over a free hole and the pins of a part other than a resistor are each in a group
   (a row) of their own. A resistor keeps its place only when its joined leg is still in the row it joins.
2. Every other part goes through spark's own first-fit placement.
3. A jumper is known by what its two rows hold (a part's pin, as "TactileButton:1.l"). A new jumper takes the earlier
   holes and route of the jumper with the same two ends, when those holes are free and in the rows the new plan gives.
4. Everything else the earlier diagram held is named: the part or jumper, and why it was dropped.
"""

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import breadboard  # noqa: E402
import breadboard_drawing as bd  # noqa: E402


class EarlierDiagram:
    """The edited breadboard.json, read back into parts with their holes, and jumpers with their holes and route."""

    def __init__(self, diagram, geometry):
        self.geometry = geometry
        self.parts = {}
        for part in diagram["parts"]:
            if part["type"] == geometry.surface.type:
                continue
            self.parts[part["id"]] = part
        holes = {hole.name: hole for hole in geometry.surface.holes}
        self.jumpers = []
        for one, other, color, route in diagram["connections"]:
            self.jumpers.append((holes.get(one.split(":", 1)[1]), holes.get(other.split(":", 1)[1]), color, route))

    def holes_of(self, part):
        """{wokwi pin: Hole or None} at the part's earlier position, {} for a type spark has no geometry for."""
        try:
            shape = self.geometry.part(part["type"])
        except bd.NotDrawn:
            return {}
        turned = bd.rotate(shape["pins"], shape["center"], part.get("rotate", 0))
        return {pin: self.geometry.hole_at(part["left"] + x, part["top"] + y) for pin, (x, y) in turned.items()}

    def owners(self):
        """{group: "part:pin"} of the earlier diagram."""
        return {hole.group: "%s:%s" % (pid, pin) for pid, part in self.parts.items()
                for pin, hole in self.holes_of(part).items() if hole}


class KeepEditsPlacement(bd.PartPlacement):
    """Strategy: an earlier part's position when it still fits, else spark's first fit. Records what it kept and
    dropped."""

    def __init__(self, geometry, earlier, catalog):
        self.geometry, self.earlier, self.catalog = geometry, earlier, catalog
        self.first_fit = bd.FirstFitPartPlacement(geometry)
        self.reserved, self.kept, self.dropped, self.started = {}, [], [], False

    def _reserve(self, ledger):
        for pid, part in self.earlier.parts.items():
            drawn = self.catalog.get(pid)
            if drawn is None:
                self.dropped.append((pid, "not in the new circuit"))
                continue
            if drawn.type != part["type"]:
                self.dropped.append((pid, "its Wokwi type changed from %s to %s" % (part["type"], drawn.type)))
                continue
            holes = self.earlier.holes_of(part)
            why = self._why_not(pid, part, holes, ledger, drawn.type == "wokwi-resistor")
            if why:
                self.dropped.append((pid, why))
                continue
            shape = self.geometry.part(part["type"])
            covered = (self.first_fit._covered(shape, part.get("rotate", 0), part["left"], part["top"], holes)
                       if shape.get("covers_holes") else [])
            under = [hole.name for hole in covered if not ledger.is_free(hole)]
            if under:
                self.dropped.append((pid, "its body covers hole %s, taken by %s" % (under[0], ledger.taken[under[0]])))
                continue
            for pin, hole in holes.items():
                ledger.claim(hole, "%s %s" % (pid, pin))
            for hole in covered:
                ledger.claim(hole, "%s, which covers it" % pid)
            self.reserved[pid] = bd.PlacedPart(pid, drawn.type, drawn.attrs, part["left"], part["top"],
                                               part.get("rotate", 0), holes)

    def _why_not(self, pid, part, holes, ledger, resistor):
        off = [pin for pin, hole in holes.items() if hole is None]
        if off:
            return "pin %s is not over a hole" % off[0]
        taken = [hole.name for hole in holes.values() if not ledger.is_free(hole)]
        if taken:
            return "hole %s is taken by %s" % (taken[0], ledger.taken[taken[0]])
        groups = [hole.group for hole in holes.values()]
        if not resistor and (len(set(groups)) < len(groups)
                             or any(not ledger.group_is_free(group) for group in groups)):
            return "two of its pins share a row, or a row holds another part"
        return None

    def place(self, part_id, drawn, ledger, after=0, pinned=None):
        if not self.started:
            self.started = True
            self._reserve(ledger)
        placed = self.reserved.pop(part_id, None)
        if placed and pinned:
            pin, group = pinned
            if placed.holes[pin].group != group:
                self.dropped.append((part_id, "its leg %s is no longer in row %s, which it joins" % (pin, group)))
                for hole in placed.holes.values():
                    del ledger.taken[hole.name]
                placed = None
        if placed:
            self.kept.append(part_id)
            return placed
        return self.first_fit.place(part_id, drawn, ledger, after, pinned)


def owners_of(layout):
    return {hole.group: "%s:%s" % (part.id, pin) for part in layout.parts for pin, hole in part.holes.items()}


def merge_jumpers(layout, earlier):
    """[(Jumper, route)], the kept jumpers, and the dropped ones with why."""
    old_owner, new_owner = earlier.owners(), owners_of(layout)
    by_key, dropped = {}, []
    for one, other, color, route in earlier.jumpers:
        ends = [old_owner.get(hole.group) if hole else None for hole in (one, other)]
        if None in ends:
            dropped.append(("jumper %s-%s" % (one and one.name, other and other.name),
                            "one end is in a row that holds no pin in the earlier diagram"))
            continue
        by_key[frozenset(ends)] = (one, other, route)
    taken = {hole.name for part in layout.parts for hole in part.holes.values()}
    taken |= {hole.name for jumper in layout.jumpers for hole in (jumper.one, jumper.other)}
    first_fit = bd.FirstFitPartPlacement(earlier.geometry)
    for part in layout.parts:
        shape = earlier.geometry.part(part.type)
        if shape.get("covers_holes"):
            taken |= {hole.name for hole in first_fit._covered(shape, part.rotate, part.left, part.top, part.holes)}
    merged, kept = [], []
    for jumper in layout.jumpers:
        key = frozenset((new_owner.get(jumper.one.group), new_owner.get(jumper.other.group)))
        found = by_key.pop(key, None)
        if found is None:
            merged.append((jumper, []))
            continue
        one, other, route = found
        if new_owner.get(one.group) != new_owner.get(jumper.one.group):
            one, other = other, one
        mine = {jumper.one.name, jumper.other.name}
        ok = (one.group == jumper.one.group and other.group == jumper.other.group
              and all(hole.name in mine or hole.name not in taken for hole in (one, other)))
        if ok:
            merged.append((bd.Jumper(one, other, jumper.step), route))
            kept.append("%s-%s" % (one.name, other.name))
        else:
            merged.append((jumper, []))
            dropped.append(("jumper %s-%s" % (one.name, other.name), "its holes are not free in the rows it joins now"))
    for key, (one, other, _) in by_key.items():
        dropped.append(("jumper %s-%s" % (one.name, other.name),
                        "the new circuit does not join %s" % " and ".join(sorted(key))))
    return merged, kept, dropped


def nets(diagram, geometry):
    """The connections a diagram makes, as a set of frozensets of "part:pin", from rows and jumpers only."""
    earlier = EarlierDiagram(diagram, geometry)
    owner_groups = {}
    for pid, part in earlier.parts.items():
        for pin, hole in earlier.holes_of(part).items():
            if hole:
                owner_groups.setdefault(hole.group, []).append("%s:%s" % (pid, pin))
    parent = {}

    def find(node):
        parent.setdefault(node, node)
        while parent[node] != node:
            node = parent[node]
        return node
    for one, other, _, _ in earlier.jumpers:
        parent[find(one.group)] = find(other.group)
    found = {}
    for group, owners in owner_groups.items():
        found.setdefault(find(group), []).extend(owners)
    return {frozenset(owners) for owners in found.values() if len(owners) > 1}


def main(argv):
    earlier_path, requirements, out = (Path(arg) for arg in argv)
    geometry = bd.WokwiGeometry.load()
    earlier = EarlierDiagram(json.loads(earlier_path.read_text()), geometry)
    read = breadboard._read_build(requirements)
    catalog = breadboard._describe_parts(read, geometry)
    fresh = bd.BreadboardPlanner(geometry, catalog).plan(read.steps)
    placement = KeepEditsPlacement(geometry, earlier, catalog)
    layout = bd.BreadboardPlanner(geometry, catalog, placement).plan(read.steps)
    merged, kept_jumpers, dropped_jumpers = merge_jumpers(layout, earlier)
    renderer = bd.WokwiBreadboardDiagram(breadboard.STEP_COLORS)
    diagram = renderer.render(layout._replace(jumpers=[jumper for jumper, _ in merged]))
    for connection, (_, route) in zip(diagram["connections"], merged):
        connection[3] = route
    out.write_text(json.dumps(diagram, indent=2) + "\n")
    fresh_nets = nets(renderer.render(fresh), geometry)
    merged_nets = nets(diagram, geometry)
    print(json.dumps({
        "kept_parts": placement.kept,
        "kept_jumpers": kept_jumpers,
        "dropped": ["%s: %s" % one for one in placement.dropped + dropped_jumpers],
        "same_connections_as_a_fresh_plan": fresh_nets == merged_nets,
        "connections": sorted(sorted(net) for net in merged_nets),
    }, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
