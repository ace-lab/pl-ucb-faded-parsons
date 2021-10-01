// https://werxltd.com/wp/2010/05/13/javascript-implementation-of-javas-string-hashcode-method/
function hash(s) {
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      hash = ((hash << 5) - hash) + s.charCodeAt(i);
      hash |= 0;
    }
    return hash;
};

class ParsonsLogger {
    constructor(widget) {
        this.widget = widget;
        this._events = [];
        this._last_typing_event = null;

        this._userHash = hash($('#username-nav')[0].innerText);
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
            lines: [] 
        };

        for (const line of widget.modified_lines) {
            e.lines.push({ id: line.id, code: line.code, indent: line.indent })
        }

        this._logEvent(e);
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
        this._finishTypingEvent();

        e['widgetId'] = this.widget.options.sortableId;
        e['time'] = e['time'] || Date.now();
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
            const Fr = Firebase.Firestore;
            const db = Firebase.app.db;

            const solutionCode = this.widget.solutionCode().map(t => t.replaceAll('\n', ';'));
            
            let docId = window.localStorage.getItem('docId');

            if (docId) {
                await Fr.updateDoc(Fr.doc(db, "logs", docId), {
                    log: Fr.arrayUnion(...this._events),
                    solutionCode: solutionCode,
                 });
            } else {
                const docRef = await Fr.addDoc(Fr.collection(db, "logs"), {
                    docTitle: document.title,
                    problemHash: this._problemHash,
                    userHash: this_userHash,
                    solutionCode: solutionCode,
                    log: this._events,
                    sent: Date.now(),
                });

                docId = docRef.id;
                window.localStorage.setItem('docId', docId);
            }
            
            console.log("Document written with ID: ", docId);
        } catch (e) {
            console.error("Error adding document: ", e);
        }
    }
}