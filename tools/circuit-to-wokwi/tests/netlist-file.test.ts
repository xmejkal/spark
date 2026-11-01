import { describe, expect, test } from "bun:test";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { emitWokwiDiagram } from "../lib/emitters/wokwi";
import { buildNetlist, readNetlist } from "../lib/netlist";
import { tinyCircuit } from "./fixtures";

/** What the spark spine writes for a board-only FireBeetle build (P484): the board, its own LED and button. */
const ONBOARD = {
  components: [
    { id: "Mcu", name: "Mcu", type: "board", pins: [] },
    { id: "onboard_led", name: "onboard_led", type: "led-red-5mm", pins: [] },
    { id: "onboard_button", name: "onboard_button", type: "tactile-button", pins: [] },
  ],
  nets: [
    { id: "onboard_led", members: [{ componentId: "Mcu", pinName: "D13" }, { componentId: "onboard_led", pinName: "A" }] },
    { id: "onboard_button", members: [{ componentId: "Mcu", pinName: "D14" }, { componentId: "onboard_button", pinName: "A" }] },
    { id: "ground", name: "GND", members: [{ componentId: "Mcu", pinName: "GND1" }, { componentId: "onboard_led", pinName: "K" },
                                          { componentId: "onboard_button", pinName: "B" }] },
  ],
};
const MAPPING = {
  onboard_led: { wokwiType: "wokwi-led", pins: { A: "A", K: "C" }, attrs: { color: "red" } },
  onboard_button: { wokwiType: "wokwi-pushbutton", pins: { A: "1.l", B: "2.l" }, attrs: { color: "green" } },
};

function convert(...args: string[]) {
  return Bun.spawnSync(["bun", "run", `${import.meta.dir}/../cli.ts`, ...args], { env: process.env });
}

describe("a netlist given as JSON (--netlist)", () => {
  test("a netlist read from a circuit and written as JSON emits the same diagram as the circuit", () => {
    const { netlist } = buildNetlist(tinyCircuit());
    const again = readNetlist(JSON.parse(JSON.stringify(netlist)));
    expect(emitWokwiDiagram(again).diagram).toEqual(emitWokwiDiagram(netlist).diagram);
  });

  test("a file without its two lists is refused", () => {
    expect(() => readNetlist({ components: [] })).toThrow("the netlist file needs a components list and a nets list");
  });

  test("the cli wires the board's own LED and button from the spine's netlist and mapping", () => {
    const folder = mkdtempSync(join(tmpdir(), "spark-netlist-"));
    writeFileSync(join(folder, "netlist.json"), JSON.stringify(ONBOARD));
    writeFileSync(join(folder, "mapping.json"), JSON.stringify(MAPPING));
    const done = convert("--netlist", join(folder, "netlist.json"), "--out", join(folder, "diagram.json"),
                         "--mapping", join(folder, "mapping.json"), "--chips", join(folder, "chips"));
    expect(done.exitCode).toBe(0);
    const diagram = JSON.parse(readFileSync(join(folder, "diagram.json"), "utf8"));
    expect(diagram.author).toBe("generated from netlist.json");
    expect(diagram.connections.map((connection: string[]) => connection.slice(0, 2))).toEqual([
      ["mcu:21", "onboard_led:A"], ["mcu:47", "onboard_button:1.l"], ["mcu:GND.1", "onboard_led:C"],
      ["mcu:GND.1", "onboard_button:2.l"], ["mcu:TX", "$serialMonitor:RX"], ["mcu:RX", "$serialMonitor:TX"],
    ]);
  });

  test("the cli refuses both a circuit and a netlist, and neither", () => {
    const both = convert("--circuit", "c.json", "--netlist", "n.json", "--out", "d.json", "--chips", "x");
    const neither = convert("--out", "d.json", "--chips", "x");
    for (const done of [both, neither]) {
      expect(done.exitCode).toBe(1);
      expect(done.stderr.toString()).toContain("exactly one of --circuit and --netlist is required");
    }
  });
});
