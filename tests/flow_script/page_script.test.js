// The page's script (P829 PR 3): no database, no button; a send writes the page's fingerprint and a UUID; a second send
// while one waits writes nothing; Withdraw deletes the row; what the status line says, never "done" alone.
// Run by tests/test_flow_script.py:  node --test tests/flow_script/page_script.test.js
"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");

const script = require(path.join(__dirname, "..", "..", "scripts", "spark", "flow", "page_script.js"));

// The words as the page's words block holds them: literals, the plan's section 9, not the code's own.
const WORDS = {
  offers: { build: { label: "Build the board", says: ["Saves its files in this project.", "If Claude Code is closed, this waits until you open it."] },
            "pick:light:led-red-5mm": { label: "Pick “Red LED” for light", says: ["Saves “Red LED” as the pick."] } },
  send: "Send", cancel: "Cancel", copy: "Copy", withdraw: "Withdraw", command: "/spark:page",
  waiting: "Sent at %s, waits for your next message to Claude. Nothing has run yet. In Claude Code, type /spark:page.",
  withdrawn: "Withdrawn. Nothing ran.", waiting_for: "Waiting for Claude: %s.", page_from: "Page from %s.",
  ok: { pick: "Picked and reserved. Nothing is built yet. The page now shows the new state.",
        build: "The board builds. It is not wired, not flashed and not simulated yet. The page now shows the new state." },
  ran: "Spark says: %s. The page now shows the new state.",
  problems: "Ran, with problems: %s. The page now shows the new state.",
  could_not_run: "Could not run: %s. The page now shows the new state.",
  refused: { "the project changed after the page was read, so nothing ran":
             "Nothing ran. The project changed after you clicked. Reload this page and click again." },
  marks: { ok: "✓", problems: "✗", "could-not-run": "?", "not-run": "–" },
};
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const AT = "2026-11-21T14:40:00.000Z";

/** Fake: an element with what the script calls. */
class FakeElement {
  constructor(tag, attributes = {}) {
    Object.assign(this, { tag, attributes, children: [], listeners: {}, style: {}, textContent: "", hidden: false, disabled: false });
  }
  getAttribute(name) { return Object.prototype.hasOwnProperty.call(this.attributes, name) ? this.attributes[name] : null; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  addEventListener(kind, act) { this.listeners[kind] = act; }
  appendChild(child) { child.parentNode = this; this.children.push(child); return child; }
  insertBefore(child, _before) { return this.appendChild(child); }
  remove() { if (this.parentNode) this.parentNode.children = this.parentNode.children.filter((each) => each !== this); }
  click() { this.listeners.click(); }
  all() { return [this].concat(...this.children.map((child) => (child.all ? child.all() : [child]))); }
}

/** Fake: a page with an intro and one sendable offer, and a window whose claude.use gives `db`. */
function fakeWindow(db) {
  const body = new FakeElement("body", { "data-fingerprint": "0123456789ab", "data-written": "2026-11-21T15:40:00+01:00" });
  const intro = body.appendChild(new FakeElement("p", { class: "intro" }));
  const offer = body.appendChild(new FakeElement("li", { "data-key": "build", "data-makes-stale": "" }));
  const words = new FakeElement("script", { id: "spark-words" });
  words.textContent = JSON.stringify(WORDS);
  const made = [];
  const document = {
    body,
    createElement: (tag) => { const element = new FakeElement(tag); made.push(element); return element; },
    createTextNode: (text) => ({ text }),
    getElementById: (id) => (id === "spark-words" ? words : null),
    querySelector: (selector) => (selector === ".intro" ? intro : null),
    querySelectorAll: (selector) => (selector === "li[data-makes-stale]" ? [offer] : []),
  };
  const win = { document, crypto: globalThis.crypto, claude: { use: async (name) => (name === "db" ? db : null) } };
  return { win, made, offer, body };
}

/** Fake: the Artifact database, in memory: the rows written and deleted, and the watches. */
function fakeDb() {
  const rows = new Map();
  const deleted = [];
  const watched = [];
  const doc = (collection, id) => ({
    set: async (row) => { rows.set(collection + "/" + id, row); },
    delete: async () => { deleted.push(collection + "/" + id); rows.delete(collection + "/" + id); },
    onSnapshot: (next) => { watched.push([collection + "/" + id, next]); return () => {}; },
  });
  const collection = (name) => ({
    doc: (id) => doc(name, id),
    orderBy: () => ({ limit: () => ({ onSnapshot: (next) => { watched.push([name, next]); return () => {}; } }) }),
  });
  return { collection, rows, deleted, watched };
}

/** Fake: a channel that keeps what it was asked. */
function fakeChannel() {
  return { sent: [], withdrawn: [], send(row) { this.sent.push(row); }, withdraw(id) { this.withdrawn.push(id); } };
}

function requests(channel) {
  return new script.Requests(channel, WORDS, "0123456789ab", () => globalThis.crypto.randomUUID(), () => new Date(AT));
}

const buttons = (made) => made.filter((element) => element.tag === "button");

test("with no database the script makes nothing", async () => {
  const { win, made, body } = fakeWindow(null);
  assert.equal(await script.start(win), null);
  assert.deepEqual(made, []);
  assert.equal(body.children.length, 2);
  const nothing = fakeWindow(null);
  delete nothing.win.claude;
  assert.equal(await script.start(nothing.win), null);
  assert.deepEqual(nothing.made, []);
});

test("with the database each sendable offer gets its button, and the panel says the page's time", async () => {
  const db = fakeDb();
  const { win, made, offer } = fakeWindow(db);
  await script.start(win);
  assert.deepEqual(buttons(made).map((made) => made.textContent), ["Copy", "Withdraw", "Build the board"]);
  assert.equal(offer.children[1].textContent, "Build the board");
  const panel = made.find((element) => element.tag === "section");
  assert.match(panel.children[0].textContent, /^Page from \d\d:\d\d\.$/);
  assert.deepEqual(db.watched.map(([name]) => name), ["requests"]);
});

test("a click opens the confirm with the offer's words, and Send writes the row with the page's fingerprint and a UUID", async () => {
  const db = fakeDb();
  const { win, made, offer } = fakeWindow(db);
  await script.start(win);
  offer.children[1].click();
  const box = offer.children[2];
  assert.deepEqual(box.children.map((child) => child.textContent),
    ["Build the board", "Saves its files in this project.", "If Claude Code is closed, this waits until you open it.", "Send", "Cancel"]);
  box.children[3].click();
  const [[name, row]] = [...db.rows.entries()];
  assert.deepEqual(Object.keys(row), ["id", "key", "seen", "at"]);
  assert.equal(name, "requests/" + row.id);
  assert.match(row.id, UUID);
  assert.equal(row.key, "build");
  assert.equal(row.seen, "0123456789ab");
  assert.equal(offer.children.length, 2, "the confirm is gone");
  const status = made.find((element) => element.attributes["aria-live"] === "polite");
  assert.match(status.textContent, /^Sent at \d\d:\d\d, waits for your next message to Claude\. Nothing has run yet\. In Claude Code, type \/spark:page\.$/);
  assert.equal(offer.children[1].disabled, true);
  assert.equal(offer.children[1].title, "Waiting for Claude: Build the board.");
});

test("a second send while one waits writes nothing", () => {
  const channel = fakeChannel();
  const asked = requests(channel);
  assert.equal(asked.send("build").key, "build");
  assert.equal(asked.send("pick:light:led-red-5mm"), null);
  assert.equal(channel.sent.length, 1);
});

test("Withdraw deletes the waiting row and says nothing ran", async () => {
  const db = fakeDb();
  const { win, made, offer } = fakeWindow(db);
  const asked = await script.start(win);
  const row = asked.send("build");
  const withdraw = buttons(made).find((made) => made.textContent === "Withdraw");
  assert.equal(withdraw.hidden, false);
  withdraw.click();
  assert.deepEqual(db.deleted, ["requests/" + row.id]);
  assert.deepEqual(asked.shown(), { mark: "–", text: "Withdrawn. Nothing ran.", grey: true });
  assert.equal(withdraw.hidden, true);
  assert.equal(offer.children[1].disabled, false);
  asked.heard({ id: "older", key: "build", at: "2026-11-20T10:00:00.000Z" }, { ran: true, status: "ok" });
  assert.equal(asked.shown().text, "Withdrawn. Nothing ran.", "the older row the delete uncovers is not news");
});

test("the answer the channel hears ends the wait, and the buttons come back", () => {
  const asked = requests(fakeChannel());
  const row = asked.send("pick:light:led-red-5mm");
  asked.heard(row, { for: row.id, ran: true, status: "ok", line: "ran Pick “Red LED” for light: ok" });
  assert.equal(asked.waiting(), null);
  assert.deepEqual(asked.shown(), { mark: "✓", text: "Picked and reserved. Nothing is built yet. The page now shows the new state.", grey: false });
  assert.notEqual(asked.send("build"), null);
});

test("the channel watches the latest request and then its answer, so a reloaded page finds both", () => {
  const db = fakeDb();
  const heard = [];
  new script.DbChannel(db).watch((request, answer) => heard.push([request && request.id, answer && answer.status]));
  const latest = { empty: false, docs: [{ id: "r1", data: () => ({ id: "r1", key: "build", at: AT }) }] };
  db.watched[0][1](latest);
  assert.deepEqual(db.watched.map(([name]) => name), ["requests", "answers/r1"]);
  db.watched[1][1]({ exists: true, data: () => ({ for: "r1", ran: true, status: "ok" }) });
  db.watched[0][1](latest);
  assert.deepEqual(heard, [["r1", null], ["r1", "ok"], ["r1", "ok"]]);
  assert.equal(db.watched.length, 2, "the same request is watched once");
});

test("the status line says each state in the page's words, and never done alone", () => {
  const request = { id: "x", key: "build", at: AT };
  const said = (answer) => script.shownState(request, answer, WORDS);
  assert.equal(script.shownState(null, null, WORDS), null);
  assert.match(said(null).text, /^Sent at \d\d:\d\d, waits for your next message to Claude\./);
  assert.deepEqual(said({ ran: true, status: "ok", line: "ran Build the board: ok" }),
    { mark: "✓", text: "The board builds. It is not wired, not flashed and not simulated yet. The page now shows the new state.", grey: false });
  assert.deepEqual(said({ ran: true, status: "problems", line: "R1 has no footprint." }),
    { mark: "✗", text: "Ran, with problems: R1 has no footprint. The page now shows the new state.", grey: false });
  assert.deepEqual(said({ ran: true, status: "could-not-run", line: "tsci is not installed" }),
    { mark: "?", text: "Could not run: tsci is not installed. The page now shows the new state.", grey: false });
  assert.deepEqual(said({ ran: false, status: "could-not-run", line: "the project changed after the page was read, so nothing ran" }),
    { mark: "–", text: "Nothing ran. The project changed after you clicked. Reload this page and click again.", grey: true });
  assert.deepEqual(said({ ran: false, status: "could-not-run", line: "constructor" }),
    { mark: "?", text: "Could not run: constructor. The page now shows the new state.", grey: false });
  assert.deepEqual(script.shownState({ key: "constructor", at: AT }, { ran: true, status: "ok", line: "ran x: ok" }, WORDS),
    { mark: "✓", text: "Spark says: ran x: ok. The page now shows the new state.", grey: false });
  for (const answer of [null, { ran: true, status: "ok" }, { ran: true, status: "problems" }, { ran: false }]) {
    const text = said(answer).text;
    assert.notEqual(text.trim().toLowerCase(), "done");
    assert.ok(text.split(" ").length > 3, text);
  }
});

test("the script's text holds no key or fingerprint it shows, no markup of a control and no web address", () => {
  const text = require("node:fs").readFileSync(path.join(__dirname, "..", "..", "scripts", "spark", "flow", "page_script.js"), "utf8");
  for (const word of ["http", "<button", "<input", "<iframe", "onclick", "innerHTML", "</"]) {
    assert.equal(text.toLowerCase().includes(word.toLowerCase()), false, word);
  }
});
