// The page's script (P829 PR 3): no database or no owner, no button; a send writes the page's fingerprint and a UUID; a
// second send while one waits writes nothing; a refused write puts the state back; Withdraw deletes the row and still
// shows an answer that comes; what the status line says, never "done" alone. P1067: a need's picks are radios, and one
// Send writes their keys in one row.
// Run by tests/test_flow_script.py:  node --test tests/flow_script/page_script.test.js
"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");

// P1062: the last request's time is read in the browser's zone; the tests pin it, as the Python tests pin the machine's.
process.env.TZ = "Europe/Prague";
const script = require(path.join(__dirname, "..", "..", "scripts", "spark", "flow", "page_script.js"));

// The words as the page's words block holds them: literals, the plan's section 9 and the review's words, not the code's own.
const STALE = "These steps may be marked out of date: requirements.";
/** P1067: a pick's words, with its need and its part, as page_words writes them. */
const pick = (need, part) => ({ label: "Pick “" + part + "” for " + need, says: ["Saves “" + part + "” as the pick.", STALE], need, part });
const WORDS = {
  offers: { build: { label: "Build the board", says: ["Saves its files in this project."] },
            "pick:light:led-red-5mm": { label: "Pick “Red LED” for light", says: ["Saves “Red LED” as the pick."] },
            "pick:display:oled-128": pick("display", "OLED 128"), "pick:display:lcd-1602": pick("display", "LCD 1602"),
            "pick:button:tactile-6mm": pick("button", "Tactile 6 mm"), "pick:button:tactile-12mm": pick("button", "Tactile 12 mm") },
  send: "Send", cancel: "Cancel", copy: "Copy", copied: "Copied: paste it in Claude Code.", withdraw: "Withdraw", command: "/spark:page",
  intro: "Where this project stands. Use a button to ask spark for a step; Claude runs it at your next /spark:page.",
  waiting: "Sent at %s. Nothing has run yet. To run it, type /spark:page in Claude Code.",
  withdrawn: "Withdrawn. If Claude had already started it, its answer shows here.",
  not_sent: "Could not send. Nothing ran.", not_withdrawn: "Could not withdraw. The request still waits.",
  waiting_for: "Waiting for Claude: %s.", last_request: "Your last request, %s: %s.",
  months: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
  request_kinds: { pick: "a pick", requirements: "the parts list", build: "the build" },
  request_other: "a step this page no longer offers",
  now_button: { "Ask Claude in the chat to build the board. It takes seconds and costs nothing.":
                "Build the board. It takes seconds and costs nothing. Use the button." },
  ok: { pick: "Saved as the pick. Nothing is built yet. Reload to see the new state.",
        build: "The board builds. It is not wired, not flashed and not simulated yet. Reload to see the new state." },
  ran: "Spark says: %s. Reload to see the new state.",
  note: "Note: %s.",
  problems: "Ran, with problems: %s. Reload to see the new state.",
  could_not_run: "Could not run: %s. Reload to see the new state.",
  refused: { "the project changed after the page was read, so nothing ran":
             "Nothing ran. The project changed after you clicked. Reload this page and click again." },
  marks: { ok: "✓", problems: "✗", "could-not-run": "?", "not-run": "–" },
  not_now: "not now", picks_said: ["%d pick (%s)", "%d picks (%s)"], send_picks: "Send %s", choose_first: "Choose a part first.",
  picks_together: "Spark checks the picks together. If one fails, spark saves none.",
  waiting_picks: "Sent at %s: %s. Nothing has run yet. To run it, type /spark:page in Claude Code.",
  ok_picks: "Saved as the picks. Nothing is built yet. Reload to see the new state.",
  last_request_picks: "your picks",
  refused_picks: { "the request names a step that spark does not offer now, so nothing ran":
                   "Nothing ran. Spark no longer offers one of these picks. Reload this page." },
};
/** P1067: the needs of the parts fold and their picks, in the page's order. */
const NEEDS = [["display", ["pick:display:oled-128", "pick:display:lcd-1602"]], ["button", ["pick:button:tactile-6mm", "pick:button:tactile-12mm"]]];
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
  get nextSibling() { const siblings = this.parentNode ? this.parentNode.children : []; return siblings[siblings.indexOf(this) + 1] || null; }
  insertBefore(child, before) {
    const at = this.children.indexOf(before);
    child.parentNode = this;
    this.children.splice(at < 0 ? this.children.length : at, 0, child);
    return child;
  }
  remove() { if (this.parentNode) this.parentNode.children = this.parentNode.children.filter((each) => each !== this); }
  closest(selector) {  // only "[name]", which is all the script asks
    for (let at = this; at; at = at.parentNode) if (at.getAttribute && at.getAttribute(selector.slice(1, -1)) !== null) return at;
    return null;
  }
  querySelector(tag) { return this.children.find((each) => each.tag === tag) || null; }
  click() { return this.listeners.click(); }
}

/** Fake: a page with an intro, one sendable offer and the guide's NOW line of it, and a window whose claude.use gives `db`
 * and a user who is the owner unless `owner` is false (null: no user capability). With `guide`, the page holds the guide's
 * section (P1062), whose NOW box holds the NOW line. With `ask`, the NOW box also holds a chat offer's block with that tell
 * (P1122), and the window's clipboard keeps what is written to it. With `needs`, the parts fold holds NEEDS' rows, each
 * `<li class="need" data-need>` with its picks, after the build's row (P1067). */
function fakeWindow(db, owner = true, nowKey = "build", guide = true, ask = null, needs = false) {
  const body = new FakeElement("body", { "data-fingerprint": "0123456789ab", "data-written": "2026-11-21T15:40:00+01:00" });
  const intro = body.appendChild(new FakeElement("p", { class: "intro" }));
  const section = guide ? new FakeElement("section", { id: "guide" }) : null;
  intro.textContent = "Where this project stands. This page only shows it. To change anything, tell Claude in the chat.";
  const now = body.appendChild(new FakeElement("p", { "data-key": nowKey, "data-makes-stale": "" }));
  now.appendChild(new FakeElement("#text")).textContent = nowKey === "build" ? " " + BUILD_NOW : " Tell Claude a pick for each.";
  const offer = body.appendChild(new FakeElement("li", { "data-key": "build", "data-makes-stale": "" }));
  const block = ask === null ? null : body.appendChild(new FakeElement("div", { class: "ask", "data-key": "look-at-board" }));
  if (block) {
    block.appendChild(new FakeElement("strong")).textContent = "Ask Claude";
    block.appendChild(new FakeElement("code")).textContent = ask;
  }
  const list = needs ? body.appendChild(new FakeElement("ul")) : null;
  const picks = [];
  for (const [need, keys] of needs ? NEEDS : []) {
    const row = list.appendChild(new FakeElement("li", { class: "need", "data-need": need }));
    row.appendChild(new FakeElement("strong")).textContent = need;
    const inner = row.appendChild(new FakeElement("ul"));
    keys.forEach((key) => picks.push(inner.appendChild(new FakeElement("li", { "data-key": key, "data-makes-stale": "requirements" }))));
  }
  const words = new FakeElement("script", { id: "spark-words" });
  words.textContent = JSON.stringify(WORDS);
  const made = [];
  const document = {
    body,
    createElement: (tag) => { const element = new FakeElement(tag); made.push(element); return element; },
    createTextNode: (text) => ({ text }),
    getElementById: (id) => (id === "spark-words" ? words : null),
    querySelector: (selector) => ({ ".intro": intro, "#guide": section }[selector] || null),
    querySelectorAll: (selector) => ({ "[data-makes-stale]": [now, offer, ...picks], ".ask[data-key]": block ? [block] : [] }[selector] || []),
  };
  const user = owner === null ? null : { isOwner: async () => owner };
  const uses = { db, user };
  const clipboard = { written: [], writeText: async (text) => { clipboard.written.push(text); } };
  const win = { document, crypto: globalThis.crypto, navigator: { clipboard },
                claude: { use: async (name) => (name in uses ? uses[name] : null) } };
  if (section) body.appendChild(section);
  return { win, made, offer, now, body, intro, section, block, clipboard, list, picks };
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
    assert.equal(body.children.length, 4);
    assert.match(intro.textContent, /This page only shows it/);
    assert.equal(body.children[1].children[0].textContent, " " + BUILD_NOW);  // P993: a viewer's NOW line keeps who acts
  }
  const nothing = fakeWindow(null);
  delete nothing.win.claude;
  assert.equal(await script.start(nothing.win), null);
  assert.deepEqual(nothing.made, []);
});

test("for the owner each sendable offer and the NOW line get a button, and the intro says how", async () => {
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
  // P1062: the status line says the last request with its date and label first
  assert.match(statusOf(made).textContent, /^Your last request, \d{1,2} [A-Z][a-z]{2} \d{4}, \d\d:\d\d: Build the board\. ✓ /);
  assert.ok(statusOf(made).textContent.endsWith("✓ " + BUILT));
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
  assert.deepEqual(said({ ran: true, status: "ok", line: "ran Build the board: ok", note: "the board record names no wokwi_part_type" }),
    { mark: "✓", text: BUILT + " Note: the board record names no wokwi_part_type.", grey: false });
  assert.deepEqual(said({ ran: true, status: "ok", line: "ran Build the board: ok", note: null }), { mark: "✓", text: BUILT, grey: false });
  assert.deepEqual(said({ ran: true, status: "problems", line: "R1 has no footprint." }),
    { mark: "✗", text: "Ran, with problems: R1 has no footprint. Reload to see the new state.", grey: false });
  // P1062 (E13): a step that ran never reads "Could not run:"; it says spark's own line
  assert.deepEqual(said({ ran: true, status: "could-not-run", line: "tsci is not installed" }),
    { mark: "?", text: "Spark says: tsci is not installed. Reload to see the new state.", grey: false });
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

test("the last request says its date in the page's month words and its label, then what spark answered", () => {
  const at = "2026-11-21T10:36:00.000Z";
  const build = { id: "x", key: "build", at };
  const said = (request, answer) => script.lastRequest(request, answer, WORDS);
  assert.equal(said(build, { ran: true, status: "ok", line: "ran Build the board: ok" }),
    "Your last request, 21 Nov 2026, 11:36: Build the board. ✓ " + BUILT);
  assert.equal(said(Object.assign({}, build, { withdrawn: true }), null),
    "Your last request, 21 Nov 2026, 11:36: Build the board. – Withdrawn. If Claude had already started it, its answer shows here.");
  assert.match(said(build, null), WAITING);
  assert.equal(said(null, null), "");
  assert.equal(said({ id: "y", key: "requirements", at }, { ran: true, status: "problems", line: "R1 has no footprint." }),
    "Your last request, 21 Nov 2026, 11:36: the parts list. ✗ Ran, with problems: R1 has no footprint. Reload to see the new state.");
  const months = WORDS.months.map((month) => month.toUpperCase());
  assert.equal(script.dayAndTime(at, months), "21 NOV 2026, 11:36");
  assert.equal(script.dayAndTime("not a time", months), "?");
  for (const answer of [{ ran: true, status: "could-not-run", line: "x" }, { ran: true, status: "problems", line: "x" }]) {
    assert.equal(said(build, answer).includes("✓"), false);
    assert.equal(said(build, answer).includes("Could not run:"), false);
  }
});

test("a request whose offer is no longer on the page is said by its kind's words, never by a part of its key", () => {
  const at = "2026-11-21T10:36:00.000Z";
  const said = (key) => script.lastRequest({ id: "x", key, at }, { ran: true, status: "ok", line: "ran x: ok" }, WORDS);
  assert.equal(said("pick:light:led-green"),
    "Your last request, 21 Nov 2026, 11:36: a pick. ✓ Saved as the pick. Nothing is built yet. Reload to see the new state.");
  for (const key of ["constructor", "needs-drop:light", "pick-other"]) {
    const line = said(key);
    assert.ok(line.startsWith("Your last request, 21 Nov 2026, 11:36: a step this page no longer offers. "), line);
    assert.equal(line.includes(key.split(":")[0] + "."), false, line);
  }
});

test("the panel stands last in the guide, under the NOW box, or after the intro on a page with no guide", async () => {
  const { win, made, section } = fakeWindow(fakeDb());
  await script.start(win);
  const panel = made.find((element) => element.tag === "section");
  assert.equal(section.lastChild, panel);
  assert.equal(panel.id, "request");
  assert.equal(panel.children.length, 3, "the status line, Copy and Withdraw: no line of the page's time");
  const plain = fakeWindow(fakeDb(), true, "build", false);
  await script.start(plain.win);
  const alone = plain.made.find((element) => element.tag === "section");
  assert.equal(plain.body.children[1], alone);
});

const TELL = "Look at this project's board with me.";

test("P1122: the owner gets one Copy in a chat offer's block, which copies the tell and never sends", async () => {
  const db = fakeDb();
  const { win, made, block, clipboard } = fakeWindow(db, true, "build", true, TELL);
  await script.start(win);
  assert.deepEqual(buttons(made).map((made) => made.textContent), ["Copy", "Withdraw", "Build the board", "Build the board", "Copy"]);
  const copy = block.children.filter((child) => child.tag === "button");
  assert.equal(copy.length, 1);
  assert.equal(block.children[3], copy[0], "after the head and the tell");
  await copy[0].click();
  assert.deepEqual(clipboard.written, [TELL]);
  assert.equal(copy[0].textContent, "Copied: paste it in Claude Code.");
  assert.equal(db.rows.size, 0, "nothing is sent");
});

test("P1122: a waiting request leaves the Copy of a chat offer as it is", async () => {
  const { win, made, block } = fakeWindow(fakeDb(), true, "build", true, TELL);
  const asked = await script.start(win);
  await asked.send("build");
  const copy = block.children.find((child) => child.tag === "button");
  assert.deepEqual([copy.disabled, copy.title], [false, undefined]);
  assert.equal(buttons(made).filter((made) => made.disabled).length, 2, "only the two buttons of the build wait");
});

test("P1122: from disk or for a viewer a chat offer's block gets no Copy, and its tell stays to select", async () => {
  for (const [db, owner] of [[null, true], [fakeDb(), false]]) {
    const { win, made, block } = fakeWindow(db, owner, "build", true, TELL);
    assert.equal(await script.start(win), null);
    assert.deepEqual(made, []);
    assert.deepEqual(block.children.map((child) => child.textContent), ["Ask Claude", TELL]);
  }
});

test("the script's text holds no markup of a control, no web address and no closing tag", () => {
  const text = require("node:fs").readFileSync(path.join(__dirname, "..", "..", "scripts", "spark", "flow", "page_script.js"), "utf8");
  for (const word of ["http", "<button", "<input", "<iframe", "onclick", "innerHTML", "</"]) {
    assert.equal(text.toLowerCase().includes(word.toLowerCase()), false, word);
  }
});

// P1067: several picks in one Send.
const radiosOf = (made) => made.filter((element) => element.tag === "input");
const textOf = (label) => label.children.map((child) => (child.tag ? "" : child.text)).join("");
/** A click on `radio`, as the browser does it: the other radios of its need let go. */
function choose(made, radio) {
  radiosOf(made).filter((each) => each.name === radio.name).forEach((each) => { each.checked = each === radio; });
  radio.listeners.change();
}
const OLED = "pick:display:oled-128";
const TACTILE = "pick:button:tactile-6mm";
const TWO_PICKS = "2 picks (display, button)";
async function aPicksPage(db = fakeDb()) {
  const page = fakeWindow(db, true, "build", true, null, true);
  const asked = await script.start(page.win);
  const radio = (key) => radiosOf(page.made).find((each) => each.value === key);
  const sendRow = page.list.children[page.list.children.length - 1];
  return Object.assign(page, { db, asked, radio, sendRow, sendPicks: sendRow.children[0], chooseFirst: sendRow.children[1] });
}

test("P1067: each need gets native radios, not now first and checked, each labelled by its part, and a choice sends nothing", async () => {
  const { made, list, radio, db } = await aPicksPage();
  const [display, button] = list.children;
  assert.deepEqual([display.attributes.role, display.attributes["aria-label"], button.attributes["aria-label"]],
    ["radiogroup", "display", "button"]);
  assert.deepEqual(radiosOf(made).map((each) => [each.type, each.name, each.value, each.checked]), [
    ["radio", "pick:display", "", true], ["radio", "pick:display", OLED, false], ["radio", "pick:display", "pick:display:lcd-1602", false],
    ["radio", "pick:button", "", true], ["radio", "pick:button", TACTILE, false], ["radio", "pick:button", "pick:button:tactile-12mm", false]]);
  const labels = made.filter((element) => element.tag === "label");
  assert.deepEqual(labels.map(textOf), [" not now", " OLED 128", " LCD 1602", " not now", " Tactile 6 mm", " Tactile 12 mm"]);
  assert.equal(display.children[1], labels[0], "not now stands first, before the need's picks");
  assert.deepEqual([labels[1].style.minHeight, labels[1].style.display], ["var(--button-height)", "inline-flex"]);
  choose(made, radio(OLED));
  assert.equal(db.rows.size, 0);
  assert.deepEqual(buttons(made).map((each) => each.textContent), ["Copy", "Withdraw", "Build the board", "Build the board", "Send 1 pick (display)"]);
});

test("P1067: Send-picks is disabled and says to choose a part while none is chosen, then names the chosen picks", async () => {
  const { made, list, radio, sendRow, sendPicks, chooseFirst } = await aPicksPage();
  assert.equal(list.children.indexOf(sendRow), 2, "after the need rows");
  assert.equal(sendRow.attributes["data-makes-stale"], "", "a data-makes-stale row, so Send-picks is teal");
  assert.deepEqual([sendPicks.textContent, sendPicks.disabled, chooseFirst.textContent, chooseFirst.hidden],
    ["Send", true, "Choose a part first.", false]);
  choose(made, radio(TACTILE));
  assert.deepEqual([sendPicks.textContent, sendPicks.disabled, chooseFirst.hidden], ["Send 1 pick (button)", false, true]);
  choose(made, radio(OLED));
  assert.equal(sendPicks.textContent, "Send " + TWO_PICKS, "in the page's order");
  choose(made, radio(""));
  choose(made, radiosOf(made).filter((each) => each.value === "")[1]);
  assert.deepEqual([sendPicks.textContent, sendPicks.disabled, chooseFirst.hidden], ["Send", true, false]);
});

test("P1067: the Send box says each pick, a line they share once, and that spark checks them together", async () => {
  const { made, radio, sendRow, sendPicks } = await aPicksPage();
  choose(made, radio(OLED));
  choose(made, radio(TACTILE));
  sendPicks.click();
  const box = sendRow.children[2];
  assert.equal(box.attributes.role, "group");
  assert.deepEqual(box.children.map((child) => child.textContent), ["Send " + TWO_PICKS,
    "Pick “OLED 128” for display Saves “OLED 128” as the pick.", "Pick “Tactile 6 mm” for button Saves “Tactile 6 mm” as the pick.",
    STALE, "Spark checks the picks together. If one fails, spark saves none.", "Send", "Cancel"]);
});

test("P1067: Send writes one row of the picks' keys and no key, and while it waits the radios keep their choice, disabled", async () => {
  const { made, radio, db, sendRow, sendPicks } = await aPicksPage();
  choose(made, radio(OLED));
  choose(made, radio(TACTILE));
  sendPicks.click();
  await sendRow.children[2].children[5].click();
  const [[name, row]] = [...db.rows.entries()];
  assert.deepEqual(Object.keys(row), ["id", "keys", "seen", "at"]);
  assert.deepEqual([name, row.keys, row.seen], ["requests/" + row.id, [OLED, TACTILE], "0123456789ab"]);
  assert.match(row.id, UUID);
  assert.match(statusOf(made).textContent, /^Sent at \d\d:\d\d: 2 picks \(display, button\)\. Nothing has run yet\./);
  assert.deepEqual(radiosOf(made).map((each) => [each.checked, each.disabled]),
    [[false, true], [true, true], [false, true], [false, true], [true, true], [false, true]]);
  assert.deepEqual([sendPicks.disabled, sendPicks.title], [true, "Waiting for Claude: " + TWO_PICKS + "."]);
});

test("P1067: after a send the database refuses, and after Withdraw, the radios come back with the same choices", async () => {
  const refusing = await aPicksPage(fakeDb("set"));
  choose(refusing.made, refusing.radio(OLED));
  assert.equal(await refusing.asked.sendPicks([OLED]), null);
  assert.equal(statusOf(refusing.made).textContent, "– Could not send. Nothing ran.");
  assert.deepEqual([refusing.radio(OLED).checked, refusing.radio(OLED).disabled, refusing.sendPicks.disabled], [true, false, false]);
  const { made, radio, asked, sendPicks } = await aPicksPage();
  choose(made, radio(TACTILE));
  const row = await asked.sendPicks([TACTILE]);
  assert.equal(radio(TACTILE).disabled, true);
  await buttons(made).find((each) => each.textContent === "Withdraw").click();
  assert.equal(asked.latest.id, row.id);
  assert.deepEqual([radio(TACTILE).checked, radio(TACTILE).disabled, sendPicks.disabled], [true, false, false]);
});

test("P1067: a row of picks waits naming them, its last request says them, and an ok or a refusal says it in the picks' words", () => {
  const request = { id: "x", keys: [OLED, TACTILE], at: "2026-11-21T10:36:00.000Z" };
  assert.equal(script.shownState(request, null, WORDS).text,
    "Sent at 11:36: 2 picks (display, button). Nothing has run yet. To run it, type /spark:page in Claude Code.");
  assert.equal(script.lastRequest(request, { ran: true, status: "ok", line: "ran x: ok" }, WORDS),
    "Your last request, 21 Nov 2026, 11:36: 2 picks (display, button). ✓ Saved as the picks. Nothing is built yet. Reload to see the new state.");
  assert.deepEqual(script.shownState(request, { ran: false, line: "the request names a step that spark does not offer now, so nothing ran" }, WORDS),
    { mark: "–", text: "Nothing ran. Spark no longer offers one of these picks. Reload this page.", grey: true });
  assert.equal(script.lastRequest({ id: "y", keys: [OLED, "pick:fan:gone"], at: request.at }, { ran: true, status: "ok", line: "ran x: ok" }, WORDS),
    "Your last request, 21 Nov 2026, 11:36: your picks. ✓ Saved as the picks. Nothing is built yet. Reload to see the new state.");
});

test("P1067: on a page with need rows the build and the NOW line still send one key", async () => {
  for (const which of ["offer", "now"]) {
    const page = await aPicksPage();
    const item = page[which];
    item.children.find((child) => child.tag === "button").click();
    const box = item.children.find((child) => child.tag === "div");
    assert.deepEqual(box.children.map((child) => child.textContent), ["Build the board", "Saves its files in this project.", "Send", "Cancel"]);
    await box.children[2].click();
    const [[, row]] = [...page.db.rows.entries()];
    assert.deepEqual([Object.keys(row), row.key], [["id", "key", "seen", "at"], "build"], which);
  }
});

test("P1067: a row of a shape the page does not know reads as request_other and breaks nothing", () => {
  const at = "2026-11-21T10:36:00.000Z";
  const ok = { ran: true, status: "ok", line: "ran x: ok" };
  for (const request of [{ id: "x", at }, { id: "x", keys: OLED, at }, { id: "x", keys: { 0: OLED }, at }]) {
    assert.equal(script.lastRequest(request, ok, WORDS),
      "Your last request, 21 Nov 2026, 11:36: a step this page no longer offers. ✓ Spark says: ran x: ok. Reload to see the new state.",
      JSON.stringify(request));
    assert.match(script.shownState(request, null, WORDS).text, WAITING);
  }
});
