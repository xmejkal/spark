/*
 * The page's one script (P829 PR 3, #1187). From disk it does nothing: the page stays as it is. In a published page with
 * the Artifact database, for the artifact's owner only, it says how the page is used in the intro, adds a button to each
 * offer the page may send (a pick, the parts list, the build), asks the person to confirm with the offer's own words, and
 * writes one request row, whose shape `flow.py run-request --help` says. In the parts fold each need's picks are radios,
 * and one Send names the chosen picks in one row (P1067). One request waits at a time, with Copy and Withdraw; the panel stands last
 * in the guide, under the NOW box (P1062), and says the last request with its date, in the browser's zone, and its label,
 * then the answer row that /spark:page writes. Beside each chat offer's tell (P1122) it adds a Copy that only copies the
 * tell and never sends. Python writes every word in the inert block "spark-words"; this script
 * fills in only a time, an offer's label or spark's own line. It never shows the key or the fingerprint, and never "done"
 * alone. Rows from the database are data: set as text only.
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
    if (Number.isNaN(date.getTime()))
        return "?";
    return String(date.getHours()).padStart(2, "0") + ":" + String(date.getMinutes()).padStart(2, "0");
}
/** A moment as "22 Nov 2026, 11:36" in the browser's zone, the month from Python's `months`, or "?" when it is no time. */
function dayAndTime(moment, months) {
    const date = new Date(moment);
    if (Number.isNaN(date.getTime()))
        return "?";
    return date.getDate() + " " + months[date.getMonth()] + " " + date.getFullYear() + ", " + clock(moment);
}
/** The kind of an offer's key: the word before its first colon. */
function kindOf(key) {
    return String(key).split(":")[0];
}
/** True for a row of several picks (P1067): its `keys` is a list. Any other row is read by its `key`. */
function isPicks(request) {
    return Array.isArray(request.keys);
}
/**
 * P1067: "2 picks (display, button)", the picks of `keys` by the needs of their offers in `words.offers`, in their order,
 * or the empty text when one of them left the page. `picks_said` is (one, many), and its %d is the count. Pure.
 */
function picksSaid(words, keys) {
    const offers = keys.map((key) => own(words.offers, key));
    if (!offers.length || offers.some((offer) => !offer || !offer.need))
        return "";
    const said = words.picks_said[offers.length === 1 ? 0 : 1].replace("%d", () => String(offers.length));
    return fill(said, offers.map((offer) => offer.need).join(words.needs_join));
}
/**
 * The label of a request: for picks, `picksSaid`, else `last_request_picks` (P1067); for a key, its offer's label on this
 * page, else its kind's words, else `request_other` (P1062): never a part of a key. A row of another shape reads as
 * `request_other`. Pure.
 */
function requestLabel(words, request) {
    if (isPicks(request))
        return picksSaid(words, request.keys) || words.last_request_picks;
    return labelOf(words, request.key) || own(words.request_kinds, kindOf(request.key)) || words.request_other;
}
/** The line of a request that waits: its time, and for picks which they are (P1067). Pure. */
function waitingLine(request, words) {
    if (!isPicks(request))
        return fill(words.waiting, clock(request.at));
    return fill(fill(words.waiting_picks, clock(request.at)), requestLabel(words, request));
}
/** Spark's line without its last full stop, so the words around it end it once. */
function sentence(line) {
    return String(line == null ? "" : line).replace(/\.$/, "");
}
/**
 * What the page says of the latest request and its answer: {mark, text, grey}, or null when there is no request. Pure.
 * A request that waits, one withdrawn with no answer yet, an ok by its kind with its note (P1008), problems, a step that
 * ran and could not finish in spark's own line (never "Could not run:", P1062), could not run, and a refusal in grey. A
 * withdrawn request whose answer came says the answer: Claude may have run it before the withdraw. Never a word alone:
 * each text is one of the page's sentences.
 */
function shownState(request, answer, words) {
    if (!request)
        return null;
    const notRun = words.marks["not-run"];
    if (request.withdrawn && !answer)
        return { mark: notRun, text: words.withdrawn, grey: true };
    if (!answer)
        return { mark: "", text: waitingLine(request, words), grey: false };
    if (answer.ran !== true) {
        const refused = own(isPicks(request) ? words.refused_picks : words.refused, answer.line);
        if (refused)
            return { mark: notRun, text: refused, grey: true };
        return { mark: words.marks["could-not-run"], text: fill(words.could_not_run, sentence(answer.line)), grey: false };
    }
    if (answer.status === "ok") {
        const said = (isPicks(request) ? words.ok_picks : own(words.ok, kindOf(request.key))) || fill(words.ran, sentence(answer.line));
        const note = typeof answer.note === "string" && answer.note ? " " + fill(words.note, sentence(answer.note)) : "";
        return { mark: words.marks.ok, text: said + note, grey: false };
    }
    const unsaved = isPicks(request) ? words.no_pick_saved + " " : ""; // P1067: several picks are saved together or not at all
    if (answer.status === "problems")
        return { mark: words.marks.problems, text: unsaved + fill(words.problems, sentence(answer.line)), grey: false };
    return { mark: words.marks["could-not-run"], text: fill(words.ran, sentence(answer.line)), grey: false };
}
/** A Shown as the status line says it: its mark, then its text. */
function said(shown) {
    return (shown.mark ? shown.mark + " " : "") + shown.text;
}
/**
 * The status line of the last request (P1062): "Your last request, <its time>: <its label>." and what `shownState` says,
 * or the waiting line alone, or the empty text with no request. The label is `requestLabel`'s. Pure.
 */
function lastRequest(request, answer, words) {
    const shown = shownState(request, answer, words);
    if (!request || !shown)
        return "";
    if (!request.withdrawn && !answer)
        return said(shown);
    return fill(fill(words.last_request, dayAndTime(request.at, words.months)), requestLabel(words, request)) + " " + said(shown);
}
/**
 * Strategy: RequestChannel, how a request leaves the page and its answer comes back: send(row) and withdraw(id), each a
 * Promise; watch(heard), which calls heard(request, answer) with the latest request (by `at`) and its answer, or null
 * for either; and watchAnswer(id, heard), which calls heard(answer) for one request. DbChannel is its one implementation
 * (P829): an Adapter on the Artifact database (`collection`, `doc`, `set`, `delete`, `orderBy`, `limit`, `onSnapshot`).
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
    watchAnswer(id, heard) {
        return this.db.collection(ANSWERS).doc(id).onSnapshot((row) => heard(row.exists ? row.data() : null), () => { });
    }
    watch(heard) {
        let id = null;
        let request = null;
        let answer = null;
        let stop = null;
        return this.db.collection(REQUESTS).orderBy("at", "desc").limit(1).onSnapshot((found) => {
            const latest = found.empty ? null : found.docs[0];
            request = latest ? latest.data() : null;
            if ((latest ? latest.id : null) !== id) { // a new latest request: its answer is watched once, never per snapshot
                if (stop)
                    stop();
                id = latest ? latest.id : null;
                answer = null;
                stop = id ? this.watchAnswer(id, (row) => {
                    answer = row;
                    heard(request, answer);
                }) : null;
            }
            heard(request, answer);
        }, () => { });
    }
}
/**
 * Controller: one request at a time. `send` writes a row only while none waits; `withdraw` deletes the waiting one and
 * says so once the delete is done, and keeps listening for its answer; `heard` takes what the channel watched. A write
 * the database refuses puts the state back and says so in `note`. `seen` is the page's fingerprint (its first 12 hex
 * digits), `makeId` gives a UUID and `now` a Date. `listen(changed)` is told each change.
 */
class Requests {
    constructor(channel, words, seen, makeId, now) {
        Object.assign(this, { channel, words, seen, makeId, now });
        this.latest = null;
        this.answer = null;
        this.note = null;
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
        return this.write({ key });
    }
    /** P1067: one request of several picks, `keys`, one per need, as the browser's radios keep them. */
    sendPicks(keys) {
        return this.write({ keys });
    }
    async write(named) {
        if (this.waiting())
            return null;
        const before = [this.latest, this.answer];
        const row = Object.assign({ id: this.makeId() }, named, { seen: this.seen, at: this.now().toISOString() });
        [this.latest, this.answer, this.note] = [row, null, null];
        this.changed();
        try {
            await this.channel.send(row);
        }
        catch (refused) {
            [this.latest, this.answer, this.note] = before.concat(this.words.not_sent);
            this.changed();
            return null;
        }
        return row;
    }
    async withdraw() {
        const waiting = this.waiting();
        if (!waiting)
            return;
        this.note = null;
        try {
            await this.channel.withdraw(waiting.id);
        }
        catch (refused) {
            this.note = this.words.not_withdrawn;
            this.changed();
            return;
        }
        if (this.latest !== waiting)
            return; // an answer or a newer request came while the delete ran
        this.latest = Object.assign({}, waiting, { withdrawn: true });
        this.channel.watchAnswer(waiting.id, (answer) => this.heardWithdrawn(waiting.id, answer));
        this.changed();
    }
    heardWithdrawn(id, answer) {
        if (!answer || !this.latest || this.latest.id !== id || !this.latest.withdrawn)
            return;
        this.answer = answer;
        this.changed();
    }
    heard(request, answer) {
        const local = this.latest;
        // a snapshot older than what this page knows, or with no request, is not news: the page's own row may not be there yet
        if (local && (!request || String(request.at) < String(local.at)))
            return;
        // the withdrawn row itself, before the delete reaches the snapshot: its answer comes through heardWithdrawn
        if (local && local.withdrawn && request.id === local.id)
            return;
        if (!local || request.id !== local.id || Boolean(answer) !== Boolean(this.answer))
            this.note = null;
        this.latest = request;
        this.answer = answer;
        this.changed();
    }
    shown() {
        if (this.note)
            return { mark: this.words.marks["not-run"], text: this.note, grey: true };
        return shownState(this.latest, this.answer, this.words);
    }
}
/** The label of an offer's key on this page, or the empty text. */
function labelOf(words, key) {
    const offer = own(words.offers, key);
    return offer ? offer.label : "";
}
/**
 * View: the intro, the status panel, the buttons and the confirm, made with createElement and addEventListener, every
 * text set as text. The panel stands last in the guide, under the NOW box (P1062), or under the intro on a page with no
 * guide; a button stands on each element that carries `data-makes-stale` (a sendable offer, and the NOW box's NEXT line
 * when the guide's now names one sendable offer), but a pick in a need's row (`[data-need]`), which gets a radio, with one
 * Send of the chosen picks after the need rows (P1067), and a Copy in each chat offer's block (`.ask[data-key]`, P1122).
 */
class PageView {
    constructor(win, requests, words) {
        Object.assign(this, { win, doc: win.document, requests, words });
        this.panel = this.doc.createElement("section");
        this.status = this.doc.createElement("p");
        this.copy = this.button(words.copy, () => this.copyCommand());
        this.withdraw = this.button(words.withdraw, () => this.requests.withdraw());
        this.buttons = [];
        this.radios = [];
        this.picks = null;
        this.chooseFirst = null;
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
        this.drawPanel();
        this.drawButtons();
        this.drawAsks();
        this.requests.listen(() => this.render());
        this.render();
    }
    drawPanel() {
        const doc = this.doc;
        const intro = doc.querySelector(".intro");
        intro.textContent = this.words.intro;
        this.panel.id = "request";
        this.status.setAttribute("aria-live", "polite");
        [this.status, this.copy, this.withdraw].forEach((part) => this.panel.appendChild(part));
        const guide = doc.querySelector("#guide");
        if (guide)
            guide.appendChild(this.panel);
        else
            intro.parentNode.insertBefore(this.panel, intro.nextSibling);
    }
    drawButtons() {
        const needs = [];
        this.doc.querySelectorAll("[data-makes-stale]").forEach((item) => {
            const key = item.getAttribute("data-key");
            const offer = own(this.words.offers, key);
            if (!offer)
                return;
            const need = item.closest("[data-need]");
            if (need) {
                if (!needs.includes(need))
                    needs.push(this.drawNeed(need));
                // P1135: the row's text (its part and what you have) becomes its radio's label, which leads the row as the design
                // draws it (P1067's look in Chrome, 27 Nov); a line after it, that spark cannot build from the pick, stays.
                const text = item.firstChild;
                const label = this.radio(need, key, text.textContent.trim());
                text.remove();
                item.insertBefore(label, item.firstChild);
                return;
            }
            const made = this.button(offer.label, () => this.confirm(item, offer.label, offer.says, () => this.requests.send(key)));
            // P993: the guide's line of what to do now (a <p>; an offer is an <li>) asks Claude in the chat; with its button
            // here, its sentence becomes the step and "Use the button." (`now_button`). A sentence it does not name stays.
            const said = item.tagName === "P" ? item.lastChild : null;
            const step = said ? own(this.words.now_button, said.textContent.trim()) : undefined;
            if (step)
                said.textContent = " " + step;
            if (item.tagName === "LI")
                item.textContent = ""; // P1135: an offer's row is its button alone, which says its label
            item.appendChild(this.doc.createTextNode(" "));
            item.appendChild(made);
            this.buttons.push(made);
        });
        if (needs.length)
            this.drawSendPicks(needs[needs.length - 1]);
    }
    /**
     * P1067: a need's row as a radiogroup named by its need, whose first radio, "not now", is checked. P1135: on a picked need
     * it reads its keep word ("keep “X”"), and the group points at the row's picked line.
     */
    drawNeed(need) {
        const name = need.getAttribute("data-need");
        const keep = own(this.words.keep, name);
        need.setAttribute("role", "radiogroup");
        need.setAttribute("aria-label", name);
        if (keep)
            need.setAttribute("aria-describedby", "picked-" + name);
        need.insertBefore(this.radio(need, "", keep || this.words.not_now), need.querySelector("ul"));
        return need;
    }
    /**
     * P1067: one native radio of `need` in a label, its value `key` (the empty text: not now). The browser keeps one choice
     * per need, so the script holds no rule of its own; a choice sends nothing. The label's height is the page's 44 px target,
     * and the radio keeps the browser's own focus ring.
     */
    radio(need, key, words) {
        const label = this.doc.createElement("label");
        Object.assign(label.style, { display: "inline-flex", alignItems: "center", minHeight: "var(--button-height)" });
        const made = this.doc.createElement("input");
        made.type = "radio";
        made.name = "pick:" + need.getAttribute("data-need");
        made.value = key;
        made.checked = !key;
        made.addEventListener("change", () => {
            this.close();
            this.render();
        });
        label.appendChild(made);
        label.appendChild(this.doc.createTextNode(" " + words));
        this.radios.push(made);
        return label;
    }
    /** The keys of the chosen picks, in the page's order. */
    chosen() {
        return this.radios.filter((radio) => radio.checked && radio.value).map((radio) => radio.value);
    }
    /**
     * P1067: after the need rows, one row with `data-makes-stale`, so its Send of the picks is teal, and under it, while no
     * part is chosen, why it waits, as text.
     */
    drawSendPicks(last) {
        const row = this.doc.createElement("li");
        row.setAttribute("data-makes-stale", "");
        this.picks = this.button(this.words.send, () => this.confirmPicks(row));
        this.chooseFirst = this.doc.createElement("p");
        this.chooseFirst.textContent = this.words.choose_first;
        row.appendChild(this.picks);
        row.appendChild(this.chooseFirst);
        last.parentNode.insertBefore(row, last.nextSibling);
    }
    /** P1067: the Send box of the chosen picks: a line per pick, a line two picks share once, then that spark checks them together. */
    confirmPicks(row) {
        const keys = this.chosen();
        if (!keys.length)
            return;
        const offers = keys.map((key) => own(this.words.offers, key));
        const counts = new Map();
        offers.forEach((offer) => offer.says.forEach((said) => counts.set(said, (counts.get(said) || 0) + 1)));
        const lines = offers.map((offer) => {
            const alone = offer.says.filter((said) => counts.get(said) === 1);
            return alone.length ? offer.label + this.words.label_join + alone.join(" ") : offer.label;
        });
        const shared = [...counts.keys()].filter((said) => counts.get(said) > 1);
        this.confirm(row, this.picks.textContent, lines.concat(shared, this.words.picks_together), () => this.requests.sendPicks(keys));
    }
    /**
     * P1122: one Copy in each chat offer's block, after its tell, and P1286: one in the deploy's run block, after its line to
     * type. A click writes the block's `code` text to the clipboard and then says `copied`, or `copied_line` for the run
     * block. It never sends and never touches the channel, and it is not among `buttons`, so a waiting request leaves it as
     * it is.
     */
    drawAsks() {
        this.doc.querySelectorAll(".ask[data-key], .run").forEach((block) => {
            const tell = block.querySelector("code");
            if (!tell)
                return;
            const said = block.getAttribute("class") === "run" ? this.words.copied_line : this.words.copied;
            const made = this.button(this.words.copy, () => this.copyTell(tell.textContent, made, said));
            block.appendChild(this.doc.createTextNode(" "));
            block.appendChild(made);
        });
    }
    copyTell(tell, made, said) {
        const clipboard = this.win.navigator && this.win.navigator.clipboard;
        if (!clipboard)
            return Promise.resolve();
        return clipboard.writeText(tell).then(() => {
            made.textContent = said;
        }, () => { });
    }
    /** The confirm box in `item`: its title, its lines, Send, which closes it and does `send`, and Cancel. */
    confirm(item, head, says, send) {
        if (this.requests.waiting())
            return;
        this.close();
        const doc = this.doc;
        this.box = doc.createElement("div");
        this.box.setAttribute("role", "group");
        const title = doc.createElement("strong");
        title.textContent = head;
        this.box.appendChild(title);
        says.forEach((said) => {
            const line = doc.createElement("p");
            line.textContent = said;
            this.box.appendChild(line);
        });
        this.box.appendChild(this.button(this.words.send, () => {
            this.close();
            send();
        }));
        this.box.appendChild(this.button(this.words.cancel, () => this.close()));
        item.appendChild(this.box);
    }
    close() {
        if (this.box)
            this.box.remove();
        this.box = null;
    }
    copyCommand() {
        const clipboard = this.win.navigator && this.win.navigator.clipboard;
        if (clipboard)
            clipboard.writeText(this.words.command).catch(() => { });
    }
    render() {
        const shown = this.requests.shown();
        const waiting = this.requests.waiting();
        const latest = lastRequest(this.requests.latest, this.requests.answer, this.words);
        this.status.textContent = shown ? (this.requests.note ? said(shown) : latest) : "";
        this.status.style.color = shown && shown.grey ? "var(--muted)" : "";
        this.copy.hidden = !waiting;
        this.withdraw.hidden = !waiting;
        const why = waiting ? fill(this.words.waiting_for, requestLabel(this.words, waiting)) : "";
        this.buttons.forEach((made) => {
            made.disabled = Boolean(waiting);
            made.title = why;
        });
        this.radios.forEach((radio) => {
            radio.disabled = Boolean(waiting);
        });
        if (!this.picks)
            return;
        const keys = this.chosen();
        this.picks.textContent = keys.length ? fill(this.words.send_picks, picksSaid(this.words, keys)) : this.words.send;
        this.picks.disabled = Boolean(waiting) || !keys.length;
        this.picks.title = why;
        this.chooseFirst.hidden = keys.length > 0;
    }
}
/**
 * Start the page in `win`: nothing at all without the Artifact database, or for a viewer who is not the artifact's
 * owner (`user.isOwner()`), so the page from disk, and the page a viewer reads, stays as it is.
 */
async function start(win) {
    const claude = win.claude;
    const db = claude && typeof claude.use === "function" ? await claude.use("db") : null;
    if (!db)
        return null;
    const user = await claude.use("user");
    if (!user || !(await user.isOwner()))
        return null;
    const words = JSON.parse(win.document.getElementById(WORDS_ID).textContent);
    const channel = new DbChannel(db);
    const requests = new Requests(channel, words, win.document.body.getAttribute("data-fingerprint"), () => win.crypto.randomUUID(), () => new Date());
    new PageView(win, requests, words).draw();
    channel.watch((request, answer) => requests.heard(request, answer));
    return requests;
}
if (typeof module === "object" && module.exports) {
    module.exports = { REQUESTS, ANSWERS, shownState, lastRequest, dayAndTime, DbChannel, Requests, PageView, start };
}
else {
    start(window).catch(() => { });
}
