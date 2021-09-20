async function add_ada() {
    const addDoc = Firebase.Firestore.addDoc;
    const collection = Firebase.Firestore.collection;
    const db = Firebase.app.db;

    try {
        const docRef = await addDoc(collection(db, "users"), {
            first: "Ada",
            last: "Lovelace",
            born: 1815
        });
        console.log("Document written with ID: ", docRef.id);
    } catch (e) {
        console.error("Error adding document: ", e);
    }
}

class ParsonsLogger {
    constructor(widget) {
        this.widget = widget;
        this.events = [];
        this.last_field_update = null;
    }
    logEvent(e) {
        e['widgetId'] = this.widget.options.sortableId;
        e['time'] = e['time'] || Date.now();
        this.events.push(e);
    }
    onSubmit() {
        const e = { type: 'submit' };

        console.log('submit event', e);
        this.logEvent(e);
    }
    onSortableUpdate(event, ui) {
        console.log(event);
    }
    finishTypingEvent() {
        if (!this.last_field_update)
            return;

        clearTimeout(this.last_field_update.timeout);

        const e = {
            type: 'typed',
            time: this.last_field_update.start,
            duration: Date.now() - this.last_field_update.start,
            codelineName: this.last_field_update.codelineName,
            codelineValue: this.last_field_update.value,
        };

        console.log('typing event', e);
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

                console.log('paste event', e);
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
}