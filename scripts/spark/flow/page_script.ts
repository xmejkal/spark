/*
 * The page's one script (P829 PR 3, #1187). From disk it does nothing: the page stays as it is. In a published page with
 * the Artifact database, for the artifact's owner only, it says how the page is used in the intro, adds a button to each
 * offer the page may send (a pick, the parts list, the build), asks the person to confirm with the offer's own words, and
 * writes one request row {id, key, seen, at}. One request waits at a time, with Copy and Withdraw; the answer row that
 * /spark:page writes shows under the intro. Python writes every word in the inert block "spark-words"; this script fills
 * in only a time, an offer's label or spark's own line. It never shows the key or the fingerprint, and never "done"
 * alone. Rows from the database are data: set as text only.
 */
"use strict";

// --- MVP ---
/** The collections of the rows: a request and its answer, each named by the request's id. */
const REQUESTS = "requests";
const ANSWERS = "answers";
const WORDS_ID = "spark-words";

interface Offer {
  label: string;
  says: string[];
}

interface Words {
  offers: Record<string, Offer>;
  marks: Record<string, string>;
  refused: Record<string, string>;
  ok: Record<string, string>;
  now_button: Record<string, string>;
  send: string;
  cancel: string;
  copy: string;
  withdraw: string;
  command: string;
  intro: string;
  waiting: string;
  withdrawn: string;
  not_sent: string;
  not_withdrawn: string;
  waiting_for: string;
  page_from: string;
  ran: string;
  note: string;
  problems: string;
  could_not_run: string;
}

interface RequestRow {
  id: string;
  key: string;
  seen: string | null;
  at: string;
  withdrawn?: boolean;
}

interface AnswerRow {
  ran?: unknown;
  status?: string;
  line?: string;
  note?: unknown;
}

interface Shown {
  mark: string;
  text: string;
  grey: boolean;
}

interface RequestChannel {
  send(row: RequestRow): Promise<unknown>;
  withdraw(id: string): Promise<unknown>;
  watchAnswer(id: string, heard: (answer: AnswerRow | null) => void): () => void;
  watch(heard: (request: RequestRow | null, answer: AnswerRow | null) => void): () => void;
}

/** `template` with its one %s replaced by `value`, as text (no $-patterns). */
function fill(template: string, value: unknown): string {
  return template.replace("%s", () => String(value));
}

/** The value of `key` in `map` when `map` holds it itself, else undefined: a row's text never reaches a prototype. */
function own<T>(map: Record<string, T>, key: string | undefined): T | undefined {
  return Object.prototype.hasOwnProperty.call(map, key!) ? map[key!] : undefined;
}

/** A moment as hours and minutes in the browser's zone, or "?" when it is no time. */
function clock(moment: string): string {
  const date = new Date(moment);
  if (Number.isNaN(date.getTime())) return "?";
  return String(date.getHours()).padStart(2, "0") + ":" + String(date.getMinutes()).padStart(2, "0");
}

/** The kind of an offer's key: the word before its first colon. */
function kindOf(key: string): string {
  return String(key).split(":")[0];
}

/** Spark's line without its last full stop, so the words around it end it once. */
function sentence(line: unknown): string {
  return String(line == null ? "" : line).replace(/\.$/, "");
}

/**
 * What the page says of the latest request and its answer: {mark, text, grey}, or null when there is no request. Pure.
 * A request that waits, one withdrawn with no answer yet, an ok by its kind with its note (P1008), problems, could not run, and a refusal in
 * grey. A withdrawn request whose answer came says the answer: Claude may have run it before the withdraw. Never a word
 * alone: each text is one of the page's sentences.
 */
function shownState(request: RequestRow | null, answer: AnswerRow | null, words: Words): Shown | null {
  if (!request) return null;
  const notRun = words.marks["not-run"];
  if (request.withdrawn && !answer) return { mark: notRun, text: words.withdrawn, grey: true };
  if (!answer) return { mark: "", text: fill(words.waiting, clock(request.at)), grey: false };
  if (answer.ran !== true) {
    const refused = own(words.refused, answer.line);
    if (refused) return { mark: notRun, text: refused, grey: true };
    return { mark: words.marks["could-not-run"], text: fill(words.could_not_run, sentence(answer.line)), grey: false };
  }
  if (answer.status === "ok") {
    const said = own(words.ok, kindOf(request.key)) || fill(words.ran, sentence(answer.line));
    const note = typeof answer.note === "string" && answer.note ? " " + fill(words.note, sentence(answer.note)) : "";
    return { mark: words.marks.ok, text: said + note, grey: false };
  }
  if (answer.status === "problems") return { mark: words.marks.problems, text: fill(words.problems, sentence(answer.line)), grey: false };
  return { mark: words.marks["could-not-run"], text: fill(words.could_not_run, sentence(answer.line)), grey: false };
}

/**
 * Strategy: RequestChannel, how a request leaves the page and its answer comes back: send(row) and withdraw(id), each a
 * Promise; watch(heard), which calls heard(request, answer) with the latest request (by `at`) and its answer, or null
 * for either; and watchAnswer(id, heard), which calls heard(answer) for one request. DbChannel is its one implementation
 * (P829): an Adapter on the Artifact database (`collection`, `doc`, `set`, `delete`, `orderBy`, `limit`, `onSnapshot`).
 */
class DbChannel implements RequestChannel {
  declare db: ArtifactDb;

  constructor(db: ArtifactDb) {
    this.db = db;
  }

  send(row: RequestRow) {
    return this.db.collection(REQUESTS).doc(row.id).set(row);
  }

  withdraw(id: string) {
    return this.db.collection(REQUESTS).doc(id).delete();
  }

  watchAnswer(id: string, heard: (answer: AnswerRow | null) => void) {
    return this.db.collection(ANSWERS).doc(id).onSnapshot((row) => heard(row.exists ? row.data() : null), () => {});
  }

  watch(heard: (request: RequestRow | null, answer: AnswerRow | null) => void) {
    let id: string | null = null;
    let request: RequestRow | null = null;
    let answer: AnswerRow | null = null;
    let stop: (() => void) | null = null;
    return this.db.collection(REQUESTS).orderBy("at", "desc").limit(1).onSnapshot((found) => {
      const latest = found.empty ? null : found.docs[0];
      request = latest ? latest.data() : null;
      if ((latest ? latest.id : null) !== id) {  // a new latest request: its answer is watched once, never per snapshot
        if (stop) stop();
        id = latest ? latest.id : null;
        answer = null;
        stop = id ? this.watchAnswer(id, (row) => {
          answer = row;
          heard(request, answer);
        }) : null;
      }
      heard(request, answer);
    }, () => {});
  }
}

/**
 * Controller: one request at a time. `send` writes a row only while none waits; `withdraw` deletes the waiting one and
 * says so once the delete is done, and keeps listening for its answer; `heard` takes what the channel watched. A write
 * the database refuses puts the state back and says so in `note`. `seen` is the page's fingerprint (its first 12 hex
 * digits), `makeId` gives a UUID and `now` a Date. `listen(changed)` is told each change.
 */
class Requests {
  declare channel: RequestChannel;
  declare words: Words;
  declare seen: string | null;
  declare makeId: () => string;
  declare now: () => Date;
  declare latest: RequestRow | null;
  declare answer: AnswerRow | null;
  declare note: string | null;
  declare listeners: (() => void)[];

  constructor(channel: RequestChannel, words: Words, seen: string | null, makeId: () => string, now: () => Date) {
    Object.assign(this, { channel, words, seen, makeId, now });
    this.latest = null;
    this.answer = null;
    this.note = null;
    this.listeners = [];
  }

  listen(changed: () => void) {
    this.listeners.push(changed);
  }

  changed() {
    this.listeners.forEach((changed) => changed());
  }

  waiting() {
    return this.latest && !this.latest.withdrawn && !this.answer ? this.latest : null;
  }

  async send(key: string) {
    if (this.waiting()) return null;
    const before: unknown[] = [this.latest, this.answer];
    const row = { id: this.makeId(), key: key, seen: this.seen, at: this.now().toISOString() };
    [this.latest, this.answer, this.note] = [row, null, null];
    this.changed();
    try {
      await this.channel.send(row);
    } catch (refused) {
      [this.latest, this.answer, this.note] = before.concat(this.words.not_sent) as [RequestRow | null, AnswerRow | null, string];
      this.changed();
      return null;
    }
    return row;
  }

  async withdraw() {
    const waiting = this.waiting();
    if (!waiting) return;
    this.note = null;
    try {
      await this.channel.withdraw(waiting.id);
    } catch (refused) {
      this.note = this.words.not_withdrawn;
      this.changed();
      return;
    }
    if (this.latest !== waiting) return;  // an answer or a newer request came while the delete ran
    this.latest = Object.assign({}, waiting, { withdrawn: true });
    this.channel.watchAnswer(waiting.id, (answer) => this.heardWithdrawn(waiting.id, answer));
    this.changed();
  }

  heardWithdrawn(id: string, answer: AnswerRow | null) {
    if (!answer || !this.latest || this.latest.id !== id || !this.latest.withdrawn) return;
    this.answer = answer;
    this.changed();
  }

  heard(request: RequestRow | null, answer: AnswerRow | null) {
    const local = this.latest;
    // a snapshot older than what this page knows, or with no request, is not news: the page's own row may not be there yet
    if (local && (!request || String(request.at) < String(local.at))) return;
    // the withdrawn row itself, before the delete reaches the snapshot: its answer comes through heardWithdrawn
    if (local && local.withdrawn && request!.id === local.id) return;
    if (!local || request!.id !== local.id || Boolean(answer) !== Boolean(this.answer)) this.note = null;
    this.latest = request;
    this.answer = answer;
    this.changed();
  }

  shown() {
    if (this.note) return { mark: this.words.marks["not-run"], text: this.note, grey: true };
    return shownState(this.latest, this.answer, this.words);
  }
}

/** The label of an offer's key on this page, or the empty text. */
function labelOf(words: Words, key: string): string {
  const offer = own(words.offers, key);
  return offer ? offer.label : "";
}

/**
 * View: the intro, the status panel, the buttons and the confirm, made with createElement and addEventListener, every
 * text set as text. The panel stands under the intro; a button stands on each element that carries `data-makes-stale`
 * (a sendable offer, and the guide's line of what to do now when its phase has one sendable offer).
 */
class PageView {
  declare win: Window;
  declare doc: Document;
  declare requests: Requests;
  declare words: Words;
  declare panel: HTMLElement;
  declare status: HTMLElement;
  declare copy: HTMLButtonElement;
  declare withdraw: HTMLButtonElement;
  declare buttons: HTMLButtonElement[];
  declare box: HTMLElement | null;

  constructor(win: Window, requests: Requests, words: Words) {
    Object.assign(this, { win, doc: win.document, requests, words });
    this.panel = this.doc.createElement("section");
    this.status = this.doc.createElement("p");
    this.copy = this.button(words.copy, () => this.copyCommand());
    this.withdraw = this.button(words.withdraw, () => this.requests.withdraw());
    this.buttons = [];
    this.box = null;
  }

  button(words: string, act: () => void) {
    const made = this.doc.createElement("button");
    made.type = "button";
    made.textContent = words;
    made.addEventListener("click", act);
    return made;
  }

  draw() {
    this.drawPanel();
    this.drawButtons();
    this.requests.listen(() => this.render());
    this.render();
  }

  drawPanel() {
    const doc = this.doc;
    const intro = doc.querySelector(".intro")!;
    intro.textContent = this.words.intro;
    this.panel.id = "request";
    const written = doc.body.getAttribute("data-written");
    if (written && written !== "none") {
      const from = doc.createElement("p");
      from.textContent = fill(this.words.page_from, clock(written));
      this.panel.appendChild(from);
    }
    this.status.setAttribute("aria-live", "polite");
    [this.status, this.copy, this.withdraw].forEach((part) => this.panel.appendChild(part));
    intro.parentNode!.insertBefore(this.panel, intro.nextSibling);
  }

  drawButtons() {
    this.doc.querySelectorAll("[data-makes-stale]").forEach((item) => {
      const key = item.getAttribute("data-key")!;
      const offer = own(this.words.offers, key);
      if (!offer) return;
      const made = this.button(offer.label, () => this.confirm(item, key, offer));
      // P993: the guide's line of what to do now (a <p>; an offer is an <li>) asks Claude in the chat; with its button
      // here, its sentence becomes the step and "Use the button." (`now_button`). A sentence it does not name stays.
      const said = item.tagName === "P" ? item.lastChild : null;
      const step = said ? own(this.words.now_button, said.textContent!.trim()) : undefined;
      if (step) said!.textContent = " " + step;
      item.appendChild(this.doc.createTextNode(" "));
      item.appendChild(made);
      this.buttons.push(made);
    });
  }

  confirm(item: Element, key: string, offer: Offer) {
    if (this.requests.waiting()) return;
    this.close();
    const doc = this.doc;
    this.box = doc.createElement("div");
    this.box.setAttribute("role", "group");
    const title = doc.createElement("strong");
    title.textContent = offer.label;
    this.box.appendChild(title);
    offer.says.forEach((said) => {
      const line = doc.createElement("p");
      line.textContent = said;
      this.box!.appendChild(line);
    });
    this.box.appendChild(this.button(this.words.send, () => {
      this.close();
      this.requests.send(key);
    }));
    this.box.appendChild(this.button(this.words.cancel, () => this.close()));
    item.appendChild(this.box);
  }

  close() {
    if (this.box) this.box.remove();
    this.box = null;
  }

  copyCommand() {
    const clipboard = this.win.navigator && this.win.navigator.clipboard;
    if (clipboard) clipboard.writeText(this.words.command).catch(() => {});
  }

  render() {
    const shown = this.requests.shown();
    const waiting = this.requests.waiting();
    this.status.textContent = shown ? (shown.mark ? shown.mark + " " : "") + shown.text : "";
    this.status.style.color = shown && shown.grey ? "var(--muted)" : "";
    this.copy.hidden = !waiting;
    this.withdraw.hidden = !waiting;
    const why = waiting ? fill(this.words.waiting_for, labelOf(this.words, waiting.key)) : "";
    this.buttons.forEach((made) => {
      made.disabled = Boolean(waiting);
      made.title = why;
    });
  }
}

/**
 * Start the page in `win`: nothing at all without the Artifact database, or for a viewer who is not the artifact's
 * owner (`user.isOwner()`), so the page from disk, and the page a viewer reads, stays as it is.
 */
async function start(win: Window) {
  const claude = win.claude;
  const db = claude && typeof claude.use === "function" ? await claude.use("db") : null;
  if (!db) return null;
  const user = await claude!.use("user");
  if (!user || !(await user.isOwner())) return null;
  const words = JSON.parse(win.document.getElementById(WORDS_ID)!.textContent!);
  const channel = new DbChannel(db);
  const requests = new Requests(channel, words, win.document.body.getAttribute("data-fingerprint"),
    () => win.crypto.randomUUID(), () => new Date());
  new PageView(win, requests, words).draw();
  channel.watch((request, answer) => requests.heard(request, answer));
  return requests;
}

if (typeof module === "object" && module.exports) {
  module.exports = { REQUESTS, ANSWERS, shownState, DbChannel, Requests, PageView, start };
} else {
  start(window).catch(() => {});
}
// --- end MVP ---
