"""
The built netlist, with the questions the physics rules ask of it (P708): `physics_check` judges the board, this file
reads it.
"""

import math

from spark.design import copper
from spark.design import netlist


# --- MVP ---
class Board(netlist.Netlist):
    """
    Value: the built netlist, plus the two questions only this file asks of it.

    The walk itself is `netlist.Netlist` since P35. This class had its own, and that one dropped
    every trace naming no net — which is how spark's own generator wires every signal — so on a
    generated board its member lists were a fraction of the truth and its arithmetic sized rails
    from what was left. Three walks, three answers to one circuit; now one.
    """

    def __init__(self, circuit):
        super().__init__(circuit)
        self.pcb_components = {e["pcb_component_id"]: e
                               for e in circuit if e.get("type") == "pcb_component"}

    def footprint_of(self, component_name):
        """
        The package string, e.g. `res0603`.

        Read from `cad_component` first, falling back to `pcb_component` for older netlists. This
        looked only at `pcb_component`, where the engine no longer puts it: measured against the
        reference board it resolved 0 of 28 components, so every rule downstream of it examined
        nothing. Exactly the defect fixed in build_check, in a second file, which is why
        that fix needed to be an audit rather than a patch.
        """
        source = self.named(component_name)
        if not source:
            return None
        wanted = source["source_component_id"]
        for element in self.elements:
            if element.get("type") not in ("cad_component", "pcb_component"):
                continue
            if element.get("source_component_id") != wanted:
                continue
            footprint = (element.get("footprinter_string") or "").strip()
            if footprint:
                return footprint
        return None

    def narrowest_by_net(self):
        """
        The narrowest routed segment ON EACH NET.

        Per net, not per board. The first version of this compared every rail against the
        board's globally narrowest trace, which answers a question nobody asked: once the motor
        loop is widened and the signals are not, the global minimum says the motor rail is thin
        when it is not. A rail is only as good as its own narrowest segment.
        """
        nets_of_trace = {}
        for element in self.elements:
            if element["type"] != "source_trace":
                continue
            names = [self.nets[n].get("name") for n in element.get("connected_source_net_ids", [])
                     if n in self.nets]
            nets_of_trace[element["source_trace_id"]] = names

        segments = {}
        for element in self.elements:
            if element["type"] != "pcb_trace":
                continue
            measured = measured_route(element.get("route", []))
            for net_name in nets_of_trace.get(element.get("source_trace_id"), []):
                segments.setdefault(net_name, []).extend(measured)

        # The width a net SUSTAINS, not the narrowest copper anywhere on it. On a generated board, six segments 0.12 to 0.85 mm
        # long at 1.20 mm wide were the last step into a 1.2 mm pad; judged as a long uniform trace, a correctly sized 2.9 A rail
        # was called unbuildable. A neck that short is bonded to a pad and a plated barrel, both heatsinks, and belongs to the PAD
        # (`build_check`'s subject). A net that is ALL necks falls back to the absolute minimum, so it cannot pass unjudged.
        narrowest = {}
        for net_name, measured in segments.items():
            sustained = copper.sustained_width_mm(measured)
            if sustained is None:
                widths = [width for width, _ in measured if width]
                if not widths:
                    continue
                sustained = min(widths)
            narrowest[net_name] = sustained
        return narrowest


def measured_route(route):
    """Value: (width, length or None) of each step of a trace's `route` that has a width; the length runs to the next step."""
    measured = []
    for index, step in enumerate(route):
        if "width" not in step:
            continue
        length = None
        if index + 1 < len(route):
            nxt = route[index + 1]
            if None not in (step.get("x"), step.get("y"), nxt.get("x"), nxt.get("y")):
                length = math.dist((step["x"], step["y"]), (nxt["x"], nxt["y"]))
        measured.append((step["width"], length))
    return measured
# --- end MVP ---
