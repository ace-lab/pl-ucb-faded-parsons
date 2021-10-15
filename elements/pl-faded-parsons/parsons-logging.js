// https://werxltd.com/wp/2010/05/13/javascript-implementation-of-javas-string-hashcode-method/
function hash(s) {
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      hash = ((hash << 5) - hash) + s.charCodeAt(i);
      hash |= 0;
    }
    return hash;
}

function identity(x) { return x; }
function compose(f, g) {
    if (f === identity) return g;
    if (g === identity) return f;
    return function(x) { return f(g(x)); }
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
        this._event_mappings = {};
        this._last_typing_event = null;

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
            lines: widget.modified_lines.map(function (line) {
                return { id: line.id, code: line.code, indent: line.indent };
            }),
        };

        this._logEvent(e);
    }

    mapDataOn(event_type, event_mapper) {
        const old = this._event_mappings[event_type] || identity;
        this._event_mappings[event_type] = compose(event_mapper, old);
    }
    
    onSubmit() {
        this._logEvent({ type: 'submit' });
        this._commit();
    }
    
    onSortableUpdate(event, ui) {
        if (event.type === 'reindent') {
            this._logEvent(event);
            return;
        }
        const lineId = ui.item[0].id;
        const solLines = [];
        for (const child of event.target.children) {
            const lineId = child.id;
            const modLine = this.widget.getLineById(lineId);
            const indent = modLine && modLine.indent;
            solLines.push({ id: lineId, indent: indent});
        }
        this._logEvent({ type: event.type, targetId: lineId, solutionLines: solLines });
    }
    
    onBlankUpdate(event, codeline) {
        switch (event.inputType) {
            case 'insertFromPaste':
            case 'insertFromPasteAsQuotation':
            case 'insertFromDrop':
                this._finishTypingEvent();

                const e = {
                    type: 'paste',
                    duration: 0,
                    codelineName: codeline.name,
                    codelineValue: codeline.value,
                };

                this._logEvent(e);
                break;
            case 'deleteByDrag':
            case 'deleteByCut':
            // do something special?
            // right now just continues to default...
            default: // generic typing event
                if (this._last_typing_event) {
                    // if the last update was to a different field, finish the previous event
                    // otherwise clear the timeout
                    if (this._last_typing_event.codelineName !== codeline.name) {
                        this._finishTypingEvent();
                    } else {
                        clearTimeout(this._last_typing_event.timeout);
                    }
                }

                this._last_typing_event = {
                    codelineName: codeline.name,
                    e: event,
                    start: this._last_typing_event ?
                        this._last_typing_event.start : Date.now(),
                    value: codeline.value,
                    timeout: setTimeout(() => this._finishTypingEvent(), 1000),
                };
        }
    }

    _logEvent(e) {
        if (e == null)
            throw new Error('events cannot be null');
        
        this._finishTypingEvent();

        e.widgetId ||= this.widget.options.sortableId;
        e.time ||= Date.now();

        e = coalesce(this._event_mappings, e.type, e) || e;

        this._events.push(e);
    }
    
    _finishTypingEvent() {
        if (!this._last_typing_event) return;

        clearTimeout(this._last_typing_event.timeout);

        const e = {
            type: 'typed',
            time: this._last_typing_event.start,
            duration: Date.now() - this._last_typing_event.start,
            codelineName: this._last_typing_event.codelineName,
            codelineValue: this._last_typing_event.value,
        };

        this._last_typing_event = null;

        this._logEvent(e);
    }
    
    async _commit() {
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
}