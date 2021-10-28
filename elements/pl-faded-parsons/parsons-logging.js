// https://werxltd.com/wp/2010/05/13/javascript-implementation-of-javas-string-hashcode-method/
function hash(s) {
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      hash = ((hash << 5) - hash) + s.charCodeAt(i);
      hash |= 0;
    }
    return hash;
}

function coalesce(...args) {
    let prev = args.shift();
    for (const curr of args) {
        if (prev == null) return prev;
        if (curr == null) return curr;

        prev = typeof(prev) === 'function' ?
                prev(curr) : prev[curr];
    }
    return prev;
}

class Logger {
    constructor(widget) {
        this.widget = widget;
        this._events = [];
        this._last_text_event = null;
        this._inited = false;
    }

    init() {
        if (this._inited) return;
        this._inited = true;

        const usernameStr = document.getElementById('navbarDropdown').innerText.trim();

        this._usernameStr = usernameStr;
        this._userHash = hash(usernameStr);
        this._problemHash = hash(document.title);

        this._sessionHash = this._userHash ^ this._problemHash;

        const prevHash = window.localStorage.getItem('sessionHash');
        const resuming = prevHash && prevHash === ("" + this._sessionHash);
        
        window.localStorage.setItem('sessionHash', this._sessionHash);

        if (!resuming) {
            window.localStorage.removeItem('docId'); // need a new doc
        }

        const e = { 
            type: resuming ? 'resume' : 'init', 
            problemHash: this._problemHash, 
            userHash: this._userHash,
            usernameStr: usernameStr,
        };

        this.logEvent(e);
    }

    logEvent(e) {
        if (!this._inited) this.init();

        if (e == null)
            throw new Error('events cannot be null');
        
        this._finishTextEvent();

        e.questionId ||= coalesce($, 'div.card-header.bg-primary', 0, innerText);
        e.time ||= Date.now();

        const mapping = this['map' + e.type];
        if (mapping) {
            e = mapping.call(this, e);
        }

        if (e != null) { // mapping may make e null!
            this._events.push(e);
        }
    }
    
    onTextUpdate(event, eventId, newText) {
        switch (event.inputType) {
            case 'insertFromPaste':
            case 'insertFromPasteAsQuotation':
            case 'insertFromDrop':
                this._finishTextEvent();

                const e = {
                    type: 'paste',
                    duration: 0,
                    eventId: eventId,
                    value: newText,
                };

                this.logEvent(e);
                break;
            case 'deleteByDrag':
            case 'deleteByCut':
            // do something special?
            // right now just continues to default...
            default: // generic text event
                if (this._last_text_event) {
                    // if the last update was to a different field, finish the previous event
                    // otherwise clear the timeout
                    if (this._last_text_event.eventId !== eventId) {
                        this._finishTextEvent();
                    } else {
                        clearTimeout(this._last_text_event.timeout);
                    }
                }

                this._last_text_event = {
                    eventId: eventId,
                    e: event,
                    start: this._last_text_event ?
                        this._last_text_event.start : Date.now(),
                    value: newText,
                    timeout: setTimeout(() => this._finishTextEvent(), 1000),
                };
        }
    }
    
    _finishTextEvent() {
        if (!this._last_text_event) return;

        clearTimeout(this._last_text_event.timeout);

        const e = {
            type: 'typed',
            time: this._last_text_event.start,
            duration: Date.now() - this._last_text_event.start,
            value: this._last_text_event.value,
            eventId: this._last_text_event.eventId,
        };

        this._last_text_event = null;

        this.logEvent(e);
    }
    
    async commit() {
        try {
            const FStore = Firebase.Firestore;
            const db = Firebase.app.db;

            const solutionCode = this.widget.solutionCode().map(t => t.replaceAll('\n', ';'));
            
            let docId = window.localStorage.getItem('docId');

            if (docId) {
                await FStore.updateDoc(FStore.doc(db, "logs", docId), {
                    log: FStore.arrayUnion(...this._events),
                    solutionCode: solutionCode,
                 });
            } else {
                const docRef = await FStore.addDoc(FStore.collection(db, "logs"), {
                    docTitle: document.title,
                    problemHash: this._problemHash,
                    userHash: this._userHash,
                    usernameStr: this._usernameStr,
                    solutionCode: solutionCode,
                    log: this._events,
                    sent: Date.now(),
                });

                docId = docRef.id;
                window.localStorage.setItem('docId', docId);
            }
            
            console.log("Document written with ID: ", docId);
        } catch (e) {
            alert("Error adding document:\n" + e.toString());
        }
    }
}

class ParsonsLogger extends Logger {
    constructor(widget) {
        super(widget);
    }

    mapresume(e) { 
        e.lines = this.widget.modified_lines.map(function (line) {
            return { id: line.id, code: line.code, indent: line.indent };
        });
        return e;
    }

    mapinit(e) { 
        e.lines = this.widget.modified_lines.map(function (line) {
            return { id: line.id, code: line.code, indent: line.indent };
        });
        return e;
    }
    
    onSubmit() {
        this.logEvent({ type: 'submit' });
        this.commit();
    }
    
    onSortableUpdate(event, ui) {
        if (event.type === 'reindent') {
            this.logEvent(event);
            return;
        }
        const lineId = ui.item[0].id;
        const solLines = [];
        for (const child of event.target.children) {
            const lineId = child.id;
            const modLine = this.widget.getLineById(lineId);
            const indent = modLine && modLine.indent;
            solLines.push({ id: lineId, indent: indent });
        }
        this.logEvent({ type: event.type, targetId: lineId, solutionLines: solLines });
    }
    
    onTextUpdate(event, codeline) {
        super.onTextUpdate(event, codeline.name, codeline.value);
    }
}