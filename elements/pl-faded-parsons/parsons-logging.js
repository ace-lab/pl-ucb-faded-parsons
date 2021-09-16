// // Import the functions you need from the SDKs you need
// import { initializeApp } from "https://www.gstatic.com/firebasejs/9.0.2/firebase-app.js";
// import { getAnalytics } from "https://www.gstatic.com/firebasejs/9.0.2/firebase-analytics.js";
// // TODO: Add SDKs for Firebase products that you want to use
// // https://firebase.google.com/docs/web/setup#available-libraries

// // Your web app's Firebase configuration
// // For Firebase JS SDK v7.20.0 and later, measurementId is optional
// const firebaseConfig = {
//   apiKey: "AIzaSyD3RdPsfO50vjyFKD6wYseNvdaQZFRslZg",
//   authDomain: "faded-parsons-logging.firebaseapp.com",
//   projectId: "faded-parsons-logging",
//   storageBucket: "faded-parsons-logging.appspot.com",
//   messagingSenderId: "591608062092",
//   appId: "1:591608062092:web:4b4e4963e6026136119ba9",
//   measurementId: "G-NCF4CRWMHG"
// };

// // Initialize Firebase
// const app = initializeApp(firebaseConfig);
// const analytics = getAnalytics(app);

(function() {
    var ParsonsLogger = function(widget) {
        this.widget = widget;
        this.events = [];
        this.last_field_update = null;
    };   

    window['ParsonsLogger'] = ParsonsLogger;

    ParsonsLogger.prototype.logEvent = function(e) {
        e['widgetId'] = this.widget.options.sortableId;
        e['time'] = e['time'] || Date.now();
        this.events.push(e);
    };

    ParsonsLogger.prototype.onSubmit = function() {
        const e = { type: 'submit' };

        console.log('submit event', e);
        this.logEvent(e);
    };

    ParsonsLogger.prototype.onSortableUpdate = function(event, ui) {
        console.log(event);
    };

    ParsonsLogger.prototype.finishTypingEvent = function() {
        if (!this.last_field_update) return;
        
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

    ParsonsLogger.prototype.onBlankUpdate = function(event, codeline) {
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
})();