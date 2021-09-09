(function() {
    var ParsonsLogger = function() {
        this.events = new Array();
        this.last_field_update = null;
    };
    window['ParsonsLogger'] = ParsonsLogger;

    ParsonsLogger.prototype.onSortableUpdate = function(event, ui) {
        console.log(event);
    };

    ParsonsLogger.prototype.onBlankUpdate = function(event, codeline) {
        let start, time;
        start = time = Date.now();

        if (this.last_field_update) {
            clearTimeout(this.last_field_update.timeout);
            start = this.last_field_update.start;
        }
        
        this.last_field_update = { 
            id: codeline.id, 
            e: event, 
            start: start,
            time: time,
            value: codeline.value,
            timeout: setTimeout(() => {
                const e = {
                    type: 'typed',
                    time: this.last_field_update.start,
                    duration: this.last_field_update.time - this.last_field_update.start,
                    codelineId: this.last_field_update.id,
                    codelineValue: this.last_field_update.value,
                };
        
                console.log(this, e);
                this.events.push(e);
        
                this.last_field_update = null;
            }, 500),
        };
    }
})();