// https://werxltd.com/wp/2010/05/13/javascript-implementation-of-javas-string-hashcode-method/
String.prototype.hashCode = function() {
    let hash = 0;
    if (this.length === 0) return hash;
    for (let i = 0; i < this.length; i++) {
      const chr = this.charCodeAt(i);
      hash = ((hash << 5) - hash) + chr;
      hash |= 0;
    }
    return hash;
};

class ParsonsLogger {
    constructor(widget) {
        this.widget = widget;
        this.events = [];
        this.last_field_update = null;

        this.problemHash = document.title.hashCode();

        const prevHash = window.localStorage.getItem('problemHash');
        const resuming = prevHash === ("" + this.problemHash);
        
        if (!prevHash) {
            window.localStorage.setItem('problemHash', this.problemHash);
            window.localStorage.removeItem('docId'); // need a new doc
        }
        
        const e = { type: resuming ? 'resume' : 'init', lines: [] };
        for (const line of widget.modified_lines) {
            e.lines.push({ id: line.id, code: line.code, indent: line.indent })
        }

        this.logEvent(e);
    }
    logEvent(e) {
        e['widgetId'] = this.widget.options.sortableId;
        e['time'] = e['time'] || Date.now();
        // console.log(e);
        this.events.push(e);
    }
    onSubmit() {
        this.logEvent({ type: 'submit' });
        this.sendLog();
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
            solLines.push({ id: lineId, indent: indent});
        }
        this.logEvent({ type: event.type, targetId: lineId, solutionLines: solLines });
    }
    finishTypingEvent() {
        if (!this.last_field_update) return;

        clearTimeout(this.last_field_update.timeout);

        const e = {
            type: 'typed',
            time: this.last_field_update.start,
            duration: Date.now() - this.last_field_update.start,
            codelineName: this.last_field_update.codelineName,
            codelineValue: this.last_field_update.value,
        };

        this.logEvent(e);

        this.last_field_update = null;
    }
    onBlankUpdate(event, codeline) {
        switch (event.inputType) {
            case 'insertFromPaste':
            case 'insertFromPasteAsQuotation':
            case 'insertFromDrop':
                this.finishTypingEvent();

                const e = {
                    type: 'paste',
                    duration: 0,
                    codelineName: codeline.name,
                    codelineValue: codeline.value,
                };

                this.logEvent(e);
                break;
            case 'deleteByDrag':
            case 'deleteByCut':
            // do something special?
            // right now just continues to default...
            default: // generic typing event
                if (this.last_field_update) {
                    // if the last update was to a different field, finish the previous event
                    // otherwise clear the timeout
                    if (this.last_field_update.codelineName !== codeline.name) {
                        this.finishTypingEvent();
                    } else {
                        clearTimeout(this.last_field_update.timeout);
                    }
                }

                this.last_field_update = {
                    codelineName: codeline.name,
                    e: event,
                    start: this.last_field_update ?
                        this.last_field_update.start : Date.now(),
                    value: codeline.value,
                    timeout: setTimeout(() => this.finishTypingEvent(), 1000),
                };
        }
    }
    async sendLog() {
        try {
            const Fr = Firebase.Firestore;
            const db = Firebase.app.db;

            const solutionCode = this.widget.solutionCode().map(t => t.replaceAll('\n', ';'));
            
            let docId = window.localStorage.getItem('docId');

            if (docId) {
                await Fr.updateDoc(Fr.doc(db, "logs", docId), {
                    log: Fr.arrayUnion(...this.events),
                    solutionCode: solutionCode,
                 });
            } else {
                const docRef = await Fr.addDoc(Fr.collection(db, "logs"), {
                    docTitle: document.title,
                    problemHash: this.problemHash,
                    solutionCode: solutionCode,
                    log: this.events,
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