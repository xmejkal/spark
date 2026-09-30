"""
The built design, as connectivity. One walk, for every rule that asks what is joined to what.

There were three walks over `circuit.json` in this repository, and on one circuit they gave three
different answers. With `U1.GND` wired pin-to-pin to `U2.GND` and `U2.GND` also on the named net
`GND`, the rules checker said U1 was connected, the physics checker's map did not contain U1 at
all, and the chain's ground check reported U1 as reaching no ground — a false problem that stops a
good board's build. Only one of the three had learned, the night before, that a trace may name no
net (backlog P8); the other two never heard.

So this is the type that was missing from a codebase whose whole job is netlists. It is
deliberately thin: an index of what exists, and a map of what is joined. Rules live in the files
that own them.

**Connectivity comes from `source_trace`**, which states its ports and its nets explicitly. It is
tempting to group ports by `subcircuit_connectivity_map_key` instead, but in a real export 16 of
92 ports carry no key at all, and grouping on that joins every one of them into a single phantom
net, wiring a 5 V pin to an H-bridge input. Unconnected is a state, not a grouping.

**A trace that names no net is still a connection.** spark's own generator wires every signal
pin-to-pin, so on the boards this tool produces most connections name no net at all. Such a trace
becomes a net of its own, keyed `trace:<its connectivity key, or its own id>` and carrying no
name — the connectivity key is what groups the several traces of one wire.

Membership is not transitive here: a pin joined by a pin-to-pin trace to a pin that sits on `GND`
is on its own `trace:` net and on no named one. That is what all three walkers did, and making it
transitive is a change with its own consequences, not a tidy-up to slip into a refactor.
"""

#: The element types this reads, named once so a caller can see what a netlist is made of.
COMPONENT, PORT, NET, TRACE = "source_component", "source_port", "source_net", "source_trace"


class Netlist:
    """What the built design joins to what, indexed by net."""

    def __init__(self, circuit):
        self.elements = circuit
        self.components = {e["source_component_id"]: e for e in circuit if e.get("type") == COMPONENT}
        self.ports = {e["source_port_id"]: e for e in circuit if e.get("type") == PORT}
        self.nets = {e["source_net_id"]: e for e in circuit if e.get("type") == NET}

        #: net id -> [(component name, port name)]. `.get("type")` rather than `e["type"]`
        #: throughout: one of the three walkers indexed it directly and a circuit element without
        #: a type was a traceback rather than a finding.
        self.members = {net_id: [] for net_id in self.nets}
        #: port id -> the net ids it sits on, so "is this pin wired at all" is one lookup.
        self.nets_of_port = {}
        #: (component name, ANY name that port answers to) -> net ids. See `names_of`.
        self.by_name = {}
        for element in circuit:
            if element.get("type") != TRACE:
                continue
            net_ids = [n for n in element.get("connected_source_net_ids") or [] if n in self.members]
            if not net_ids:
                net_ids = [self.trace_net_id(element)]
                self.members.setdefault(net_ids[0], [])
            for port_id in element.get("connected_source_port_ids") or []:
                port = self.ports.get(port_id)
                if not port:
                    continue
                owner = self.components.get(port.get("source_component_id"), {})
                member = (owner.get("name", "?"), port.get("name", "?"))
                for net_id in net_ids:
                    self.members[net_id].append(member)
                    self.nets_of_port.setdefault(port_id, set()).add(net_id)
                    for alias in self.names_of(port):
                        self.by_name.setdefault((member[0], alias), set()).add(net_id)

    @staticmethod
    def trace_net_id(trace):
        """The net a net-less trace stands in for: its wire's key, or failing that its own id."""
        return "trace:" + (trace.get("subcircuit_connectivity_map_key") or trace["source_trace_id"])

    def net_named(self, name):
        """The id of the net with this name, or None. Names are the rules' vocabulary, not ids."""
        for net_id, net in self.nets.items():
            if net.get("name") == name:
                return net_id
        return None

    def net_names(self):
        """Every net's name, for a rule that asks whether a thing exists before asking about it."""
        return [net.get("name") for net in self.nets.values() if net.get("name")]

    def power_nets(self):
        return {net_id for net_id, net in self.nets.items() if net.get("is_power")}

    @staticmethod
    def names_of(port):
        """
        Every name a port answers to: what it is called, and every hint the builder recorded.

        A component built from `pinLabels` carries the label as the port's NAME — the flow
        meter's `VCC` is a port called VCC. A component built from a FOOTPRINT does not: the
        FireBeetle module's ports are called `pin17`, `pin32`, and the silkscreen label lives
        only in `port_hints`. That is the only name a person, a board file or a rule ever uses.

        Keying membership on `name` alone therefore made every rule about the microcontroller's
        own pads miss, silently and in both directions. Reproduced on the irrigation controller
        on 2026-09-30, both on a board that is correct: `compare_design` with
        `must_not_float: [["Mcu", "D11"]]` answered "Mcu.D11 connects to nothing" while
        `board.tsx` line 81 wires it to Valve4.SIGNAL, and P29's supply walk reported the
        processor's own 3.3 V pad as unfed. A pad has one identity and several spellings.
        """
        names = [port.get("name")] + list(port.get("port_hints") or [])
        return {name for name in names if name}

    def nets_of(self, component_name, port_name):
        """Which nets a given pin sits on, by any of its names. Empty means joined to nothing."""
        return set(self.by_name.get((component_name, port_name), ()))

    def component(self, name):
        for element in self.components.values():
            if element.get("name") == name:
                return element
        return None

    #: `check_physics` calls the same question `named`; both names are kept so neither file has to
    #: change its own vocabulary to share the walk.
    named = component

    def components_on(self, net_name):
        """Every component with a pin on the net of this NAME, sorted."""
        net_id = self.net_named(net_name)
        return sorted({name for name, _ in self.members.get(net_id, [])}) if net_id else []
