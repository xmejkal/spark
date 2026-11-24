// The parts of the Artifact runtime that the page script uses (P1061), and CommonJS's `module`, which node's tests give it.

interface ArtifactRow {
  readonly id: string;
  readonly exists: boolean;
  data(): any;
}

interface ArtifactQuery {
  readonly empty: boolean;
  readonly docs: ArtifactRow[];
}

interface ArtifactDoc {
  set(row: object): Promise<unknown>;
  delete(): Promise<unknown>;
  onSnapshot(heard: (row: ArtifactRow) => void, failed: () => void): () => void;
}

interface ArtifactCollection {
  doc(id: string): ArtifactDoc;
  orderBy(field: string, direction: "asc" | "desc"): ArtifactCollection;
  limit(count: number): ArtifactCollection;
  onSnapshot(heard: (found: ArtifactQuery) => void, failed: () => void): () => void;
}

interface ArtifactDb {
  collection(name: string): ArtifactCollection;
}

interface ArtifactUser {
  isOwner(): Promise<boolean>;
}

interface ArtifactRuntime {
  use(name: "db"): Promise<ArtifactDb | null>;
  use(name: "user"): Promise<ArtifactUser | null>;
}

interface Window {
  claude?: ArtifactRuntime;
}

declare var module: { exports: unknown } | undefined;
