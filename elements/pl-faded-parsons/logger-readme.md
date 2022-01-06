LOGGER README
=============

The logger file is designed to be used as the base class of a general logging system for a new question element.

*This logger cannot be used with the built-in PrairieLearn elements without modification.*

## Install Guide

### 1. Include `logger.js`

Copy `./logger.js` into your `course/elements/my-element` directory.

Then, edit your `elements/my-element/info.json` to include `logger.js` as a dependency, eg:

```json
{
  "controller": "my-element.py",
  "dependencies": {
    "elementScripts": [
      "logger.js",
      "my-element.js"
    ]
  }
}
```

### 2. Optionally Include Firebase and Firstore

#### Opting Out
If you choose not to include Firebase, the logger will not commit any of its records.
To intercept these commits, override the async `commit` method, or else the system will alert when the commits fail.

Simply do not follow the rest of step two to opt out!

#### Opting In

In your `./my-element-question.mustache` add the following snippet to the top of your element.

```html
<script type="module">
    import * as Fb from "https://www.gstatic.com/firebasejs/9.0.2/firebase-app.js";
    import * as Firestore from "https://www.gstatic.com/firebasejs/9.0.2/firebase-firestore.js";

    const firebaseConfig = { /* fill me with your Firebase Config */ };

    const Firebase = Object.create(Fb);
    Firebase.Firestore = Firestore;
    Firebase.app = Firebase.initializeApp(firebaseConfig);
    Firebase.app.db = Firebase.Firestore.getFirestore(Firebase.app);

    window['Firebase'] = Firebase;
</script> 
```
Learn how to start a firbase project [here](https://firebase.google.com/docs/web/setup). Learn more about firbase configs [here](https://firebase.google.com/docs/web/learn-more#config-object).

### Making Log Events

Once the logger is configured, you can begin to use it after your DOM is rendered!
The simplest way is to simply add another `<script>` tag at the bottom of your question mustache file, or include a new dependency js file after the Logger! Then simply wire up the proper callbacks like so:

```javascript
class MyLogger extends Logger { 
    onCoolness() { this.logEvent({ type: 'cool' }); }
}

const logger = new MyLogger();

inputField.addEventListener('onchange', 
    () => logger.onTextUpdate(/* ... */));

submitButton.addEventListener('submit', 
    () => logger.onSubmit());

praiseButton.addEventListener('submit', 
    () => logger.onCoolness());

// ...
```

## Using the Logger

The logger is designed to be extended to fit the particular needs of your custom element, though it is capable of running without extension.

Below are a list of feature highlights that come out of the box.

### Built-in Feature Highlights

#### Batched Text Events

The logger will automatically batch together a series of edits from a single field within a short timespan (eg typing 'h', 'e', 'l, 'x' '\b', 'l', 'o' would not log seven events, just a single "hello" event).
The batching is controlled by a `batchId` which will group consecutive edits that share the same id.

#### Sessions

Much like batching text events, the logger also has the notion of user sessions.
A session is defined as a user solving a problem - if either the user or the problem changes, the session ends!

These sessions provide the continuity that would typically be lost when a student reloads a page or submits a problem to be graded (thereby reloading the page)!
Events are emitted when the logger initializes or resumes a session, but these can be muted by extensions to provide a seamless session abstraction!

#### Commiting to Firebase

The logger only commits when persistent memory must be written or data will be lost - at page unload!

The logger will manage writing to firestore so that sessions are represented as a single sub-document within the `logs` document, creating any necessary documents as it goes!

If there is an error in the commiting process, it will raise an alert and enter recovery mode.
The next time the logger is initialized, it will recover the logs lost at the most recent error!


## Extensibility

This logger was desgined to be extended!
___Excluding methods with an underscore prefix___, not only can the behavior of any of the methods be altered, the handling of any type of event can be editted as well!

New events and event types can be made on the fly - just be sure each event has some type!

Simply write a `map_mytype(e)` method on your subclass, and any event with the field `type: 'mytype'` will automatically be routed through it!
Whatever `map_mytype(e)` returns will be added to the log!

See the `ParsonsLogger` example below of how you can wrap logger methods, map events by their type, and introduce new types of events altogether!

### An Example: `ParsonsLogger`

```javascript
/**
 * A class that performs the funcitonality specific to ParsonsWidget.
 */
class ParsonsLogger extends Logger {
    
    ///// ADDING CUSTOM DATA ////////////////////////////////////////

    constructor(widget) {
        super();
        this.widget = widget;
    }

    ///// CUSTOM EVENT HANDLING /////////////////////////////////////

    /**
     * Adds a record of the modified code lines to the event
     * @param {*} e incoming event
     * @returns modified event
     */
    _add_widget_lines(e) {
        e.lines = this.widget.modified_lines.map(line =>
            ({ id: line.id, code: line.code, indent: line.indent })
        );
        return e;
    }

    /** Alter the resume and init events before they are logged
     *  so they contain a record of modified code lines at the onset.
     */
    map_resume(e) { return this._add_widget_lines(e); }
    map_init(e) { return this._add_widget_lines(e); }

    /** Edit commit events */
    map_commit(e) {
        // Only on commit, add the current solution code
        e.solutionCode = this.widget.solutionCode();
        return e;
    }
    
    ///// OVERRIDING WITH WRAPPER ///////////////////////////////////

    /**
     * A callback for capturing codeline text edits
     * @param {InputEvent} event the original onInput event
     * @param {ParsonsCodeline} codeline the codeline that was editted
     */
    onTextUpdate(event, codeline) {
        const batchId = codeline.name; // batch by codeline!
        super.onTextUpdate(event, batchId, codeline.value);
    }
    
    ///// ADDING NEW EVENTS/HANDLERS ////////////////////////////////

    /**
     * A callback for catching line sorting and reindenting.
     * @param {*} event the sort/indent event to log
     * @param {*} ui the parsons jsortable-ui object that raised the event
     */
    onSortableUpdate(event, ui) {
        if (event.type === 'reindent') {
            this.logEvent(event);
            return;
        }
        const lineId = ui.item[0].id;
        const solLines = [];
        for (const child of event.target.children) {
            // lines are collected...
        }
        this.logEvent({ 
            type: event.type, 
            targetId: lineId, 
            solutionLines: solLines 
        });
    }
}
```