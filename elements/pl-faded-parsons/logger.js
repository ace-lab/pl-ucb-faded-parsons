// https://werxltd.com/wp/2010/05/13/javascript-implementation-of-javas-string-hashcode-method/
const hash = s => {
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
        hash = ((hash << 5) - hash) + s.charCodeAt(i);
        hash |= 0;
    }
    return hash;
};

/**
 * Returns the result of nesting dotting/calling to the args, returning
 * null early if any intermediate step is null.
 * 
 * > let a = { b: { c: 3, f: x => 2 * x }};
 * 
 * > coalesce(a, 'b', 'c') == 3; // a.b.c
 * 
 * > coalesce(a, 'z', 'c') == null; // a.z.c -> z == null!
 * 
 * > coalesce([1, a, 3], 1, 'b', 'f', 2) == 4;// [1, a, 3][1].b.f(2)
 * 
 * @param  {...any} args properties/args to nesting
 * @returns a0?[a1]?[a2]?...
 */
const coalesce = (...args) =>
    args.reduce((prev, curr) =>
        prev == null ? prev : 
            typeof(prev) === 'function' ? prev(curr) : prev[curr]);

class Logger {
    constructor() {
        this._events = [];
        this._last_text_event = null;
        this._inited = false;
    }

    _init() {
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
        if (!this._inited) this._init();

        if (e == null)
            throw new Error('events cannot be null');
        
        this._finishTextEvent();

        e.questionId ||= coalesce($, 'div.card-header.bg-primary', 0, 'innerText') || document.title;
        e.time ||= Date.now();

        const mapping = this['map_' + e.type];
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
    
    onSubmit() {
        this.logEvent({ type: 'submit' });
        this.commit();
    }
    
    async commit() {
        try {
            const FStore = Firebase.Firestore;
            const db = Firebase.app.db;
            
            let docId = window.localStorage.getItem('docId');

            const rawCommitData = 
                docId ? {
                    log: FStore.arrayUnion(...this._events),
                } : {
                    docTitle: document.title,
                    problemHash: this._problemHash,
                    userHash: this._userHash,
                    usernameStr: this._usernameStr,
                    log: this._events,
                    sent: Date.now()
                };
            
            const commitData = this.map_commit ? this.map_commit(rawCommitData) : rawCommitData;
            if (docId) {
                await FStore.updateDoc(FStore.doc(db, "logs", docId), commitData);
            } else {
                const docRef = await FStore.addDoc(FStore.collection(db, "logs"), commitData);
                docId = docRef.id;
                window.localStorage.setItem('docId', docId);
            }
            
            console.log("Document written with ID: ", docId);
        } catch (e) {
            alert("Error adding document:\n" + e.toString());
        }
    }
}