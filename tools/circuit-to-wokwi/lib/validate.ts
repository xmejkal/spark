/**
 * Prove the generated diagram is worth trusting, offline, before it is written.
 *
 * Two checks, answering different questions:
 *
 *   lint      — "is this a valid Wokwi project?"   Wokwi's own rules and part registry
 *   coverage  — "does it simulate *this* board?"   every net that could be wired, was
 *
 * The second is the one this tool exists for. A diagram that lints perfectly but silently lost a
 * net is a simulation quietly disagreeing with the hardware, which is worse than no simulation.
 */

import { DiagramLinter } from "@wokwi/diagram-lint";

import type { EmitResult } from "./emitters/wokwi";
import type { Problem } from "./types";

export interface ValidationResult {
  problems: Problem[];
  checkedNets: number;
  wiredNets: number;
  lintIssues: number;
  /** Not blocking: a hand-added part with no wire yet (P497). */
  warnings: string[];
}

/** The mark merge.ts puts on a part the person added in Wokwi; the linter does not know it as an attribute. */
const HAND_ADDED_ATTR = "handAdded";

export function validate(emitted: EmitResult, componentCount?: number, handAddedIds: string[] = []): ValidationResult {
  const { problems: lintProblems, warnings } = lint(emitted, handAddedIds);
  const coverageProblems = [
    ...checkNetCoverage(emitted),
    ...checkNothingVanished(emitted, componentCount),
  ];

  return {
    problems: [...lintProblems, ...coverageProblems],
    checkedNets: emitted.netOutcomes.length,
    wiredNets: emitted.netOutcomes.filter((outcome) => outcome.wires > 0).length,
    lintIssues: lintProblems.length,
    warnings,
  };
}

/**
 * Wokwi's own lint, less two things that are the person's hand-added parts (P497): the mark itself is not an attribute
 * of the part (`invalid-attribute` with attrName handAdded), and a part with no wire yet is a warning, not a stop. The
 * ids come from the merge summary, so a generated part that shares an id and the mark is still held to every rule.
 */
function lint(emitted: EmitResult, handAddedIds: string[]): { problems: Problem[]; warnings: string[] } {
  const result = new DiagramLinter().lint(emitted.diagram as any);
  const problems: Problem[] = [];
  const warnings: string[] = [];
  for (const issue of result.issues) {
    if (issue.severity === "info") continue;
    const partId = (issue as any).partId;
    if (issue.rule === "invalid-attribute" && (issue as any).context?.attrName === HAND_ADDED_ATTR) continue;
    if (issue.rule === "redundant-parts" && handAddedIds.includes(partId)) {
      warnings.push(
        `${partId} is hand-added and has no wire yet: it stays in the diagram, and the build passed. ` +
          "Wire it in Wokwi if it should do something.",
      );
      continue;
    }
    problems.push({ message: `${issue.rule}: ${issue.message}`, context: { component: partId } });
  }
  return { problems, warnings };
}

/**
 * A net with two or more simulated endpoints must have produced a wire.
 *
 * Nets that lost members to skip rules are not failures — that is the skip rules working, and
 * the emitter records exactly how many went that way.
 */
/**
 * Every component in the design must have become a part, or been skipped for a stated reason,
 * or been reported. Nothing may simply disappear.
 *
 * This is the check that catches a skip rule quietly widening its reach — renaming a component
 * so an unanchored pattern starts matching it used to remove it from the simulation in silence.
 */
function checkNothingVanished(emitted: EmitResult, componentCount?: number): Problem[] {
  if (componentCount === undefined) return [];

  const accountedFor = emitted.diagram.parts.length + emitted.skipped.length +
    emitted.problems.length;
  if (accountedFor >= componentCount) return [];

  return [
    {
      message:
        `${componentCount - accountedFor} component(s) in the design became neither a part nor ` +
        `a stated omission. Something is being dropped silently`,
    },
  ];
}

function checkNetCoverage(emitted: EmitResult): Problem[] {
  return emitted.netOutcomes
    .filter((outcome) => outcome.simulatedEndpoints >= 2 && outcome.wires === 0)
    .map((outcome) => ({
      message: "this net connects two simulated parts but produced no wire",
      context: { net: outcome.name ?? outcome.netId },
    }));
}
