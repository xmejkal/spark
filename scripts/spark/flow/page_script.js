/*
 * The page's one script (P829 PR 3, #1187). From disk it does nothing: the page stays as it is. In a published page with
 * the Artifact database, it adds a button to each offer the page may send (a pick, the parts list, the build), asks the
 * person to confirm with the offer's own words, and writes one request row {id, key, seen, at}. One request waits at a
 * time, with Copy and Withdraw; the answer row that /spark:page writes shows under the intro. Python writes every word
 * in the inert block "spark-words"; this script fills in only a time, an offer's label or spark's own line. It never
 * shows the key or the fingerprint, and never "done" alone. Rows from the database are data: set as text only.
 */
"use strict";

// --- MVP ---
/** The collections of the rows: a request and its answer, each named by the request's id. */
const REQUESTS = "requests";
const ANSWERS = "answers";
const WORDS_ID = "spark-words";

/** `template` with its one %s replaced by `value`, as text (no $-patterns). */
function fill(template, value) {
  return template.replace("%s", () => String(value));
}

/** The value of `key` in `map` when `map` holds it itself, else undefined: a row's text never reaches a prototype. */
function own(map, key) {
  return Object.prototype.hasOwnProperty.call(map, key) ? map[key] : undefined;
}

/** A moment as hours and minutes in the browser's zone, or "?" when it is no time. */
function clock(moment) {
  const date = new Date(moment);
  if (Number.isNaN(date.getTime())) return "?";
  return String(date.getHours()).padStart(2, "0") + ":" + String(date.getMinutes()).padStart(2, "0");
}

/** The kind of an offer's key: the word before its first colon. */
function kindOf(key) {
  return String(key).split(":")[0];
}

/** Spark's line without its last full stop, so the words around it end it once. */
function sentence(line) {
  return String(line == null ? "" : line).replace(/\.$/, "");
}

/**
 * What the page says of the latest request and its answer: {mark, text, grey}, or null when there is no request. Pure.
 * A request that waits, one withdrawn, an ok by its kind, problems, could not run, and a refusal in grey. Never a word
 * alone: each text is one of the page's sentences.
 */
function shownState(request, answer, words) {
  if (!request) return null;
  const notRun = words.marks["not-run"];
  if (request.withdrawn) return { mark: notRun, text: words.withdrawn, grey: true };
  if (!answer) return { mark: "", text: fill(words.waiting, clock(request.at)), grey: false };
  if (answer.ran !== true) {
    const refused = own(words.refused, answer.line);
    if (refused) return { mark: notRun, text: refused, grey: true };
    return { mark: words.marks["could-not-run"], text: fill(words.could_not_run, sentence(answer.line)), grey: false };
  }
  if (answer.status === "ok") {
    return { mark: words.marks.ok, text: own(words.ok, kindOf(request.key)) || fill(words.ran, sentence(answer.line)), grey: false };
  }
  if (answer.status === "problems") return { mark: words.marks.problems, text: fill(words.problems, sentence(answer.line)), grey: false };
  return { mark: words.marks["could-not-run"], text: fill(words.could_not_run, sentence(answer.line)), grey: false };
}

/**
 * Strategy: RequestChannel, how a request leaves the page and its answer comes back: send(row), watch(heard) and
 * withdraw(id). DbChannel is its one implementation (P829): an Adapter on the Artifact database. watch calls
 * heard(request, answer) with the latest request (by `at`) and its answer, or null for either.
 */
class DbChannel {
  constructor(db) {
    this.db = db;
  }

  send(row) {
    return this.db.collection(REQUESTS).doc(row.id).set(row);
  }

  withdraw(id) {
    return this.db.collection(REQUESTS).doc(id).delete();
  }

  watch(heard) {
    let id = null;
    let request = null;
    let answer = null;
    let stop = null;
    const quiet = () => {};
    return this.db.collection(REQUESTS).orderBy("at", "desc").limit(1).onSnapshot((found) => {
      const latest = found.empty ? null : found.docs[0];
      request = latest ? latest.data() : null;
      if ((latest ? latest.id : null) !== id) {
        if (stop) stop();
        id = latest ? latest.id : null;
        answer = null;
        stop = id ? this.db.collection(ANSWERS).doc(id).onSnapshot((row) => {
          answer = row.exists ? row.data() : null;
          heard(request, answer);
        }, quiet) : null;
      }
      heard(request, answer);
    }, quiet);
  }
}

/**
 * Controller: one request at a time. `send` writes a row only while none waits; `withdraw` deletes the waiting one;
 * `heard` takes what the channel watched. `seen` is the page's fingerprint (its first 12 hex digits), `makeId` gives a
 * UUID and `now` a Date. `listen(changed)` is told each change.
 */
class Requests {
  constructor(channel, words, seen, makeId, now) {
    Object.assign(this, { channel, words, seen, makeId, now });
    this.latest = null;
    this.answer = null;
    this.listeners = [];
  }

  listen(changed) {
    this.listeners.push(changed);
  }

  changed() {
    this.listeners.forEach((changed) => changed());
  }

  waiting() {
    return this.latest && !this.latest.withdrawn && !this.answer ? this.latest : null;
  }

  send(key) {
    if (this.waiting()) return null;
    const row = { id: this.makeId(), key: key, seen: this.seen, at: this.now().toISOString() };
    this.latest = row;
    this.answer = null;
    this.channel.send(row);
    this.changed();
    return row;
  }

  withdraw() {
    const waiting = this.waiting();
    if (!waiting) return;
    this.channel.withdraw(waiting.id);
    this.latest = Object.assign({}, waiting, { withdrawn: true });
    this.changed();
  }

  heard(request, answer) {
    // a withdrawn request stays said until a newer one comes: the older one the delete uncovers is not news
    if (this.latest && this.latest.withdrawn && !(request && String(request.at) > String(this.latest.at))) return;
    this.latest = request;
    this.answer = answer;
    this.changed();
  }

  shown() {
    return shownState(this.latest, this.answer, this.words);
  }
}

/** The label of an offer's key on this page, or the empty text. */
function labelOf(words, key) {
  const offer = own(words.offers, key);
  return offer ? offer.label : "";
}

/**
 * View: the buttons, the confirm and the status line, made with createElement and addEventListener, every text set as
 * text. The status panel stands under the intro.
 */
class PageView {
  constructor(win, requests, words) {
    Object.assign(this, { win, doc: win.document, requests, words });
    this.buttons = [];
    this.box = null;
  }

  button(words, act) {
    const made = this.doc.createElement("button");
    made.type = "button";
    made.textContent = words;
    made.addEventListener("click", act);
    return made;
  }

  draw() {
    const doc = this.doc;
    this.panel = doc.createElement("section");
    this.panel.id = "request";
    const written = doc.body.getAttribute("data-written");
    if (written && written !== "none") {
      const from = doc.createElement("p");
      from.textContent = fill(this.words.page_from, clock(written));
      this.panel.appendChild(from);
    }
    this.status = doc.createElement("p");
    this.status.setAttribute("aria-live", "polite");
    this.copy = this.button(this.words.copy, () => this.copyCommand());
    this.withdraw = this.button(this.words.withdraw, () => this.requests.withdraw());
    [this.status, this.copy, this.withdraw].forEach((part) => this.panel.appendChild(part));
    const intro = doc.querySelector(".intro");
    intro.parentNode.insertBefore(this.panel, intro.nextSibling);
    doc.querySelectorAll("li[data-makes-stale]").forEach((item) => {
      const key = item.getAttribute("data-key");
      const offer = own(this.words.offers, key);
      if (!offer) return;
      const made = this.button(offer.label, () => this.confirm(item, key, offer));
      item.appendChild(doc.createTextNode(" "));
      item.appendChild(made);
      this.buttons.push(made);
    });
    this.requests.listen(() => this.render());
    this.render();
  }

  confirm(item, key, offer) {
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
      this.box.appendChild(line);
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

/** Start the page in `win`: nothing at all without the Artifact database, so the page from disk stays as it is. */
async function start(win) {
  const claude = win.claude;
  const db = claude && typeof claude.use === "function" ? await claude.use("db") : null;
  if (!db) return null;
  const words = JSON.parse(win.document.getElementById(WORDS_ID).textContent);
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
