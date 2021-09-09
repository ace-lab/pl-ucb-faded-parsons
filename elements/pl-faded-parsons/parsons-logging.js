(function() {
    var ParsonsLogger = function() {
        this.events = new Array();
        this.last_field_update = null;
    };
    window['ParsonsLogger'] = ParsonsLogger;

    ParsonsLogger.prototype.onSortableUpdate = function(event, ui) {
        console.log(event);
    };

    ParsonsLogger.prototype.finishTypingEvent = function() {
        if (!this.last_field_update) return;
        
        clearTimeout(this.last_field_update.timeout);

        const e = {
            type: 'typed',
            time: this.last_field_update.start,
            duration: this.last_field_update.time - this.last_field_update.start,
            codelineId: this.last_field_update.id,
            codelineValue: this.last_field_update.value,
        };

        console.log('typing event', e);
        this.events.push(e);

        this.last_field_update = null;
    }

    ParsonsLogger.prototype.onBlankUpdate = function(event, codeline) {
        let time = Date.now();

        switch (event.inputType) {
            case 'insertFromPaste': 
            case 'insertFromPasteAsQuotation':
            case 'insertFromDrop':
                this.finishTypingEvent();

                const e = {
                    type: 'paste',
                    time: time,
                    duration: 0,
                    codelineId: codeline.id,
                    codelineValue: codeline.value,
                };

                console.log('paste event', e);
                this.events.push(e);
                break;
            case 'deleteByDrag':
            case 'deleteByCut':
                // do something special?
                // right now just continues to default...
            default: // generic typing event
                if (this.last_field_update && this.last_field_update.id !== codeline.name) {
                    this.finishTypingEvent();
                }
                
                let start = time;
        
                if (this.last_field_update) {
                    clearTimeout(this.last_field_update.timeout);
                    start = this.last_field_update.start;
                }
                
                this.last_field_update = { 
                    id: codeline.name, 
                    e: event, 
                    start: start,
                    time: time,
                    value: codeline.value,
                    timeout: setTimeout(() => this.finishTypingEvent(), 1000),
                };
        }
    }
})();