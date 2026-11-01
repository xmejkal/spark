import { describe, expect, test } from "bun:test";

import type { EmitResult } from "../lib/emitters/wokwi";
import { mergeWithExisting } from "../lib/merge";
import { validate } from "../lib/validate";

const generated: any = {
  version: 1,
  author: "test",
  editor: "wokwi",
  parts: [
    { type: "board-esp32-devkit-c-v4", id: "esp", top: 0, left: 0, attrs: {} },
    { type: "wokwi-led", id: "led1", top: 0, left: 0, attrs: { color: "red" } },
  ],
  connections: [["led1:A", "esp:2", "green", []], ["led1:C", "esp:GND.1", "black", []]],
};

function mark(attrs: Record<string, string> = {}) {
  return { handAdded: "true", ...attrs };
}

function check(extraParts: any[], extraWires: any[] = []) {
  const existing = { ...generated, parts: [...generated.parts, ...extraParts], connections: [...generated.connections, ...extraWires] };
  const { diagram, summary } = mergeWithExisting(generated, existing);
  const result = validate({ diagram, netOutcomes: [], skipped: [], problems: [] } as unknown as EmitResult, 2, summary.keptHandAddedParts);
  return { diagram, existing, result };
}

const wired = [["mine:A", "esp:4", "green", []], ["mine:C", "esp:GND.2", "black", []]];

describe("a hand-added part of a known type", () => {
  test("a wired one passes the lint with nothing to say", () => {
    const { result } = check([{ type: "wokwi-led", id: "mine", top: 1, left: 1, attrs: mark({ color: "blue" }) }], wired);
    expect(result.problems).toEqual([]);
    expect(result.warnings).toEqual([]);
  });

  test("an unwired one is one warning that names it, and not a problem", () => {
    const { result } = check([{ type: "wokwi-led", id: "lone", top: 1, left: 1, attrs: mark() }]);
    expect(result.problems).toEqual([]);
    expect(result.warnings).toEqual([
      {
        code: "hand-added-unwired",
        message: "lone was added by hand and has no wire yet. It stays in the diagram. Wire it in Wokwi if it should do something.",
      },
    ]);
  });

  test("a misspelt attribute on it is still a problem", () => {
    const { result } = check([{ type: "wokwi-led", id: "mine", top: 1, left: 1, attrs: mark({ colr: "x" }) }], wired);
    expect(result.problems.map((problem) => problem.message).join("\n")).toContain("colr");
  });

  test("the diagram keeps the mark", () => {
    const { diagram } = check([{ type: "wokwi-led", id: "mine", top: 1, left: 1, attrs: mark() }], wired);
    expect(diagram.parts.find((part: any) => part.id === "mine")!.attrs!.handAdded).toBe("true");
  });

  test("a generated unwired part still blocks", () => {
    const loose = { ...generated, parts: [...generated.parts, { type: "wokwi-led", id: "loose", top: 2, left: 2, attrs: {} }] };
    const result = validate({ diagram: loose, netOutcomes: [], skipped: [], problems: [] } as unknown as EmitResult, 3, []);
    expect(result.problems.map((problem) => problem.message).join("\n")).toContain("redundant-parts");
    expect(result.warnings).toEqual([]);
  });
});
