// The page's script (P829 PR 3): no database or no owner, no button; a send writes the page's fingerprint and a UUID; a
// second send while one waits writes nothing; a refused write puts the state back; Withdraw deletes the row and still
// shows an answer that comes; what the status line says, never "done" alone.
// Run by tests/test_flow_script.py:  node --test tests/flow_script/page_script.test.js
"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");

const script = require(path.join(__dirname, "..", "..", "scripts", "spark", "flow", "page_script.js"));

// The words as the page's words block holds them: literals, the plan's section 9 and the review's words, not the code's own.
const WORDS = {
  offers: { build: { label: "Build the board", says: ["Saves its files in this project."] },
            "pick:light:led-red-5mm": { label: "Pick “Red LED” for light", says: ["Saves “Red LED” as the pick."] } },
  send: "Send", cancel: "Cancel", copy: "Copy", withdraw: "Withdraw", command: "/spark:page",
  intro: "Where this project stands. Use a button to ask spark for a step; Claude runs it at your next /spark:page.",
  waiting: "Sent at %s. Nothing has run yet. To run it, type /spark:page in Claude Code.",
  withdrawn: "Withdrawn. If Claude had already started it, its answer shows here.",
  not_sent: "Could not send. Nothing ran.", not_withdrawn: "Could not withdraw. The request still waits.",
  waiting_for: "Waiting for Claude: %s.", page_from: "Page from %s.",
  now_button: { "Ask Claude in the chat to build the board. It takes seconds and costs nothing.":
                "Build the board. It takes seconds and costs nothing. Use the button." },
  ok: { pick: "Saved as the pick. Nothing is built yet. Reload to see the new state.",
        build: "The board builds. It is not wired, not flashed and not simulated yet. Reload to see the new state." },
  ran: "Spark says: %s. Reload to see the new state.",
  problems: "Ran, with problems: %s. Reload to see the new state.",
  could_not_run: "Could not run: %s. Reload to see the new state.",
  refused: { "the project changed after the page was read, so nothing ran":
             "Nothing ran. The project changed after you clicked. Reload this page and click again." },
  marks: { ok: "✓", problems: "✗", "could-not-run": "?", "not-run": "–" },
};
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const AT = "2026-11-21T14:40:00.000Z";
const WAITING = /^Sent at \d\d:\d\d\. Nothing has run yet\. To run it, type \/spark:page in Claude Code\.$/;
const BUILD_NOW = "Ask Claude in the chat to build the board. It takes seconds and costs nothing.";
const BUILT = "The board builds. It is not wired, not flashed and not simulated yet. Reload to see the new state.";

/** Fake: an element with what the script calls. */
class FakeElement {
  constructor(tag, attributes = {}) {
    Object.assign(this, { tag, attributes, children: [], listeners: {}, style: {}, textContent: "", hidden: false, disabled: false });
  }
  get tagName() { return this.tag.toUpperCase(); }
  get lastChild() { return this.children[this.children.length - 1] || null; }
  getAttribute(name) { return Object.prototype.hasOwnProperty.call(this.attributes, name) ? this.attributes[name] : null; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  addEventListener(kind, act) { this.listeners[kind] = act; }
  appendChild(child) { child.parentNode = this; this.children.push(child); return child; }
  insertBefore(child, _before) { return this.appendChild(child); }
  remove() { if (this.parentNode) this.parentNode.children = this.parentNode.children.filter((each) => each !== this); }
  click() { return this.listeners.click(); }
}

/** Fake: a page with an intro, one sendable offer and the guide's NOW line of it, and a window whose claude.use gives `db`
 * and a user who is the owner unless `owner` is false (null: no user capability). */
function fakeWindow(db, owner = true, nowKey = "build") {
  const body = new FakeElement("body", { "data-fingerprint": "0123456789ab", "data-written": "2026-11-21T15:40:00+01:00" });
  const intro = body.appendChild(new FakeElement("p", { class: "intro" }));
  intro.textContent = "Where this project stands. This page only shows it. To change anything, tell Claude in the chat.";
  const now = body.appendChild(new FakeElement("p", { "data-key": nowKey, "data-makes-stale": "" }));
  now.appendChild(new FakeElement("#text")).textContent = nowKey === "build" ? " " + BUILD_NOW : " Tell Claude a pick for each.";
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
    querySelectorAll: (selector) => (selector === "[data-makes-stale]" ? [now, offer] : []),
  };
  const user = owner === null ? null : { isOwner: async () => owner };
  const uses = { db, user };
  const win = { document, crypto: globalThis.crypto, claude: { use: async (name) => (name in uses ? uses[name] : null) } };
  return { win, made, offer, now, body, intro };
}

/** Fake: the Artifact database, in memory: the rows written and deleted, and the watches. `refuse` names a verb that rejects. */
function fakeDb(refuse = null) {
  const rows = new Map();
  const deleted = [];
  const watched = [];
  const doc = (collection, id) => ({
    set: async (row) => { if (store.refuse === "set") throw { code: "invalid_argument" }; rows.set(collection + "/" + id, row); },
    delete: async () => { if (store.refuse === "delete") throw { code: "invalid_argument" }; deleted.push(collection + "/" + id); },
    onSnapshot: (next) => { watched.push([collection + "/" + id, next]); return () => {}; },
  });
  const collection = (name) => ({
    doc: (id) => doc(name, id),
    orderBy: () => ({ limit: () => ({ onSnapshot: (next) => { watched.push([name, next]); return () => {}; } }) }),
  });
  const store = { collection, rows, deleted, watched, refuse };
  return store;
}

/** Fake: a channel that keeps what it was asked; `refuse` names a verb that rejects. */
function fakeChannel(refuse = null) {
  return {
    sent: [], withdrawn: [], answers: {},
    async send(row) { if (refuse === "send") throw new Error("refused"); this.sent.push(row); },
    async withdraw(id) { if (refuse === "withdraw") throw new Error("refused"); this.withdrawn.push(id); },
    watchAnswer(id, heard) { this.answers[id] = heard; return () => {}; },
  };
}

function requests(channel) {
  return new script.Requests(channel, WORDS, "0123456789ab", () => globalThis.crypto.randomUUID(), () => new Date(AT));
}

const buttons = (made) => made.filter((element) => element.tag === "button");
const statusOf = (made) => made.find((element) => element.attributes["aria-live"] === "polite");

test("with no database, or for a viewer who is not the owner, the script makes nothing", async () => {
  for (const [db, owner] of [[null, true], [fakeDb(), false], [fakeDb(), null]]) {
    const { win, made, body, intro } = fakeWindow(db, owner);
    assert.equal(await script.start(win), null);
    assert.deepEqual(made, []);
    assert.equal(body.children.length, 3);
    assert.match(intro.textContent, /This page only shows it/);
    assert.equal(body.children[1].children[0].textContent, " " + BUILD_NOW);  // P993: a viewer's NOW line keeps who acts
  }
  const nothing = fakeWindow(null);
  delete nothing.win.claude;
  assert.equal(await script.start(nothing.win), null);
  assert.deepEqual(nothing.made, []);
});

test("for the owner each sendable offer and the NOW line get a button, the intro says how, the panel the page's time", async () => {
  const db = fakeDb();
  const { win, made, offer, now, intro } = fakeWindow(db);
  await script.start(win);
  assert.deepEqual(buttons(made).map((made) => made.textContent), ["Copy", "Withdraw", "Build the board", "Build the board"]);
  assert.equal(now.children[2].textContent, "Build the board");
  assert.equal(offer.children[1].textContent, "Build the board");
  // P993: with its button there, the NOW line names the step and says to use the button; an offer's line is as it was
  assert.equal(now.children[0].textContent, " Build the board. It takes seconds and costs nothing. Use the button.");
  assert.equal(offer.children[0].text, " ");
  // P993 review: a NOW sentence the words do not name (the parts' "Tell Claude a pick") stays as it is
  const picked = fakeWindow(fakeDb(), true, "pick:light:led-red-5mm");
  await script.start(picked.win);
  assert.equal(picked.now.children[0].textContent, " Tell Claude a pick for each.");
  assert.equal(intro.textContent, "Where this project stands. Use a button to ask spark for a step; Claude runs it at your next /spark:page.");
  const panel = made.find((element) => element.tag === "section");
  assert.match(panel.children[0].textContent, /^Page from \d\d:\d\d\.$/);
  assert.deepEqual(db.watched.map(([name]) => name), ["requests"]);
});

test("a click opens the confirm with the offer's words, and Send writes the row with the page's fingerprint and a UUID", async () => {
  const db = fakeDb();
  const { win, made, offer, now } = fakeWindow(db);
  await script.start(win);
  const [copy, withdraw] = buttons(made);
  assert.equal(copy.hidden, true);
  offer.children[1].click();
  const box = offer.children[2];
  assert.deepEqual(box.children.map((child) => child.textContent), ["Build the board", "Saves its files in this project.", "Send", "Cancel"]);
  await box.children[2].click();
  const [[name, row]] = [...db.rows.entries()];
  assert.deepEqual(Object.keys(row), ["id", "key", "seen", "at"]);
  assert.equal(name, "requests/" + row.id);
  assert.match(row.id, UUID);
  assert.equal(row.key, "build");
  assert.equal(row.seen, "0123456789ab");
  assert.equal(offer.children.length, 2, "the confirm is gone");
  assert.match(statusOf(made).textContent, WAITING);
  assert.deepEqual([copy.hidden, withdraw.hidden], [false, false]);
  for (const button of [now.children[2], offer.children[1]]) {
    assert.equal(button.disabled, true);
    assert.equal(button.title, "Waiting for Claude: Build the board.");
  }
});

test("a send the database refuses puts the state back and says nothing ran", async () => {
  const db = fakeDb("set");
  const { win, made, offer } = fakeWindow(db);
  const asked = await script.start(win);
  assert.equal(await asked.send("build"), null);
  assert.equal(asked.waiting(), null);
  assert.equal(statusOf(made).textContent, "– Could not send. Nothing ran.");
  assert.equal(offer.children[1].disabled, false);
  assert.equal(buttons(made)[0].hidden, true);
  assert.equal(db.rows.size, 0);
  db.refuse = null;
  assert.notEqual(await asked.send("build"), null, "a later send runs");
  assert.match(statusOf(made).textContent, WAITING);
});

test("a second send while one waits writes nothing", async () => {
  const channel = fakeChannel();
  const asked = requests(channel);
  assert.equal((await asked.send("build")).key, "build");
  assert.equal(await asked.send("pick:light:led-red-5mm"), null);
  assert.equal(channel.sent.length, 1);
});

test("a snapshot older than the page's own send, or with no request, leaves the wait on", async () => {
  const asked = requests(fakeChannel());
  const row = await asked.send("build");
  asked.heard(null, null);
  asked.heard({ id: "older", key: "build", at: "2026-11-20T10:00:00.000Z" }, { ran: true, status: "ok" });
  assert.equal(asked.waiting(), row);
  asked.heard(row, null);
  assert.equal(asked.waiting(), row);
});

test("Withdraw says withdrawn only once the delete is done, and still shows the answer that comes for it", async () => {
  const db = fakeDb();
  const { win, made, offer } = fakeWindow(db);
  const asked = await script.start(win);
  const row = await asked.send("build");
  asked.heard(row, null);
  const withdraw = buttons(made).find((made) => made.textContent === "Withdraw");
  const done = withdraw.click();
  assert.match(asked.shown().text, WAITING, "not before the delete is done");
  await done;
  assert.deepEqual(db.deleted, ["requests/" + row.id]);
  assert.deepEqual(asked.shown(), { mark: "–", text: "Withdrawn. If Claude had already started it, its answer shows here.", grey: true });
  assert.equal(withdraw.hidden, true);
  assert.equal(offer.children[1].disabled, false);
  asked.heard(row, null);
  asked.heard({ id: "older", key: "build", at: "2026-11-20T10:00:00.000Z" }, { ran: true, status: "ok" });
  assert.equal(asked.shown().text, "Withdrawn. If Claude had already started it, its answer shows here.", "neither is news");
  const [name, answerHeard] = db.watched[db.watched.length - 1];
  assert.equal(name, "answers/" + row.id);
  answerHeard({ exists: true, data: () => ({ for: row.id, ran: true, status: "ok", line: "ran Build the board: ok" }) });
  assert.deepEqual(asked.shown(), { mark: "✓", text: BUILT, grey: false });
  assert.equal(statusOf(made).textContent, "✓ " + BUILT);
});

test("a withdraw the database refuses leaves the request waiting and says so", async () => {
  const channel = fakeChannel("withdraw");
  const asked = requests(channel);
  const row = await asked.send("build");
  await asked.withdraw();
  assert.equal(asked.waiting(), row);
  assert.deepEqual(asked.shown(), { mark: "–", text: "Could not withdraw. The request still waits.", grey: true });
  assert.deepEqual(channel.answers, {});
});

test("the answer the channel hears ends the wait, and the buttons come back", async () => {
  const asked = requests(fakeChannel());
  const row = await asked.send("pick:light:led-red-5mm");
  asked.heard(row, { for: row.id, ran: true, status: "ok", line: "ran Pick “Red LED” for light: ok" });
  assert.equal(asked.waiting(), null);
  assert.deepEqual(asked.shown(), { mark: "✓", text: "Saved as the pick. Nothing is built yet. Reload to see the new state.", grey: false });
  assert.notEqual(await asked.send("build"), null);
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
  assert.match(said(null).text, WAITING);
  assert.deepEqual(said({ ran: true, status: "ok", line: "ran Build the board: ok" }), { mark: "✓", text: BUILT, grey: false });
  assert.deepEqual(said({ ran: true, status: "problems", line: "R1 has no footprint." }),
    { mark: "✗", text: "Ran, with problems: R1 has no footprint. Reload to see the new state.", grey: false });
  assert.deepEqual(said({ ran: true, status: "could-not-run", line: "tsci is not installed" }),
    { mark: "?", text: "Could not run: tsci is not installed. Reload to see the new state.", grey: false });
  assert.deepEqual(said({ ran: false, status: "could-not-run", line: "the project changed after the page was read, so nothing ran" }),
    { mark: "–", text: "Nothing ran. The project changed after you clicked. Reload this page and click again.", grey: true });
  assert.deepEqual(said({ ran: false, status: "could-not-run", line: "constructor" }),
    { mark: "?", text: "Could not run: constructor. Reload to see the new state.", grey: false });
  assert.deepEqual(script.shownState({ key: "constructor", at: AT }, { ran: true, status: "ok", line: "ran x: ok" }, WORDS),
    { mark: "✓", text: "Spark says: ran x: ok. Reload to see the new state.", grey: false });
  for (const answer of [null, { ran: true, status: "ok" }, { ran: true, status: "problems" }, { ran: false }]) {
    const text = said(answer).text;
    assert.notEqual(text.trim().toLowerCase(), "done");
    assert.ok(text.split(" ").length > 3, text);
  }
});

test("the script's text holds no markup of a control, no web address and no closing tag", () => {
  const text = require("node:fs").readFileSync(path.join(__dirname, "..", "..", "scripts", "spark", "flow", "page_script.js"), "utf8");
  for (const word of ["http", "<button", "<input", "<iframe", "onclick", "innerHTML", "</"]) {
    assert.equal(text.toLowerCase().includes(word.toLowerCase()), false, word);
  }
});
