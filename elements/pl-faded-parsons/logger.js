/**
 * An extensible logger that tracks events and commits them.
 * Designed specifically to handle text and submission events by default.
 *
 *
 * Default captured events can be altered by adding a mapping method
 * corresponding to each type of captured events:
 *      `init`    `resume`    `paste`    `text`    `submit`    `commit`
 *
 * Extending Logger with a class that has functions named
 *      `map_init`  `map_resume`  `map_paste`  `map_text`  `map_submit`  `map_commit`
 * that each take an event and return an event (or null to cancel it) will
 * alter the event before it enters the log.
 *
 * Custom event types can be trivially created! Just use:
 * > logEvent({ type: 'myType' })
 *
 * This type will also be compatible with the mapping method system, just
 * provide a `map_myType` method!
 *
 * Calling commit will cause the Logger to write to a Firebase repository.
 * This requires `Firebase.Firestore` to be the Firestore module, and
 * `Firebase.app.db` to be the current Firebase app's Firestore database.
 * 
 * Using this template in your html will do the necessary setup:
 * ```
<script type="module">
    import * as Fb from "https://www.gstatic.com/firebasejs/9.0.2/firebase-app.js";
    import * as Firestore from "https://www.gstatic.com/firebasejs/9.0.2/firebase-firestore.js";

    // Your web app's Firebase configuration
    const firebaseConfig = { ... };

    const Firebase = Object.create(Fb);
    Firebase.Firestore = Firestore;
    Firebase.app = Firebase.initializeApp(firebaseConfig);
    Firebase.app.db = Firebase.Firestore.getFirestore(Firebase.app);

    window['Firebase'] = Firebase;
</script> 
 * ```
 */
class Logger {
  constructor() {
    this._events = [];
    this._last_text_event = null;
  }

  /**
   * Initializes the Logger with the session data required for committing,
   * exiting recovery mode if necessary.
   */
  _init() {
    if (this._inited) return;
    this._inited = true;

    // TODO: Find a better way to access the username/email of current user
    const usernameStr = document
      .getElementById("navbarDropdown")
      .innerText.trim();

    this._usernameStr = usernameStr;
    // https://werxltd.com/wp/2010/05/13/javascript-implementation-of-javas-string-hashcode-method/
    const hash = (s) => {
      let hash = 0;
      for (let i = 0; i < s.length; i++) {
        hash = (hash << 5) - hash + s.charCodeAt(i);
        hash |= 0; // convert to iu64
      }
      return hash;
    };

    this._userHash = hash(usernameStr);
    this._problemHash = hash(document.title);

    this._sessionHash = this._userHash ^ this._problemHash;

    const prevHash = window.localStorage.getItem("sessionHash");
    const recovering = window.localStorage.getItem("recovery");
    const resuming = prevHash && prevHash === "" + this._sessionHash;

    window.localStorage.setItem("sessionHash", this._sessionHash);

    if (!resuming) {
      window.localStorage.removeItem("docId"); // need a new doc
    }

    if (recovering) {
      this._events = JSON.parse(recovering);
      window.localStorage.removeItem("recovery");
    }

    const e = {
      type: resuming ? "resume" : "init",
      problemHash: this._problemHash,
      userHash: this._userHash,
      usernameStr: usernameStr,
    };

    this.logEvent(e);

    window.addEventListener("beforeunload", () => this.commit());
  }

  /**
   * Puts the logger into recovery mode, and uninitializes all fields.
   */
  _deinit() {
    if (!this._inited) return;

    this._finishTextEvent();
    this._last_text_event = null;

    if (this._events && this._events.length) {
      window.localStorage.setItem('recovery', this.dumpLog());
      this._events = [];
    }
    
    this._inited = false;
  }

  /**
   * Takes an event { type: string; * }, runs `this['map_' + e.type](e)`,
   * and adds it to the log if the result is not null or undefined.
   *
   * Adds e.time and e.questionId if they are not already provided.
   * @param {object} e the non-null event to log
   */
  logEvent(e) {
    if (!this._inited) this._init();

    if (e == null) throw new Error("events cannot be null");

    if (typeof e.type !== "string")
      throw new Error("events must have a string type");

    this._finishTextEvent();

    if (!e.questionId) {
      // TODO: Find a better way to access the name of the question
      //       this logger's widget is accessing
      const questionNameClasses = "card-header bg-primary";
      const elements = document.getElementsByClassName(questionNameClasses);
      const questionText = elements.length
        ? elements[0].innerText
        : document.title;
      e.questionId = questionText.trim();
    }
    e.time ||= Date.now();

    const mapping = this["map_" + e.type];
    if (mapping) {
      e = mapping.call(this, e);
    }

    if (e != null) {
      // mapping may make e null!
      this._events.push(e);
    }
  }

  /**
   * A callback for catching and combining single edit actions into more cohesive
   * text events. With the exception of paste events, `event`s raised with the same
   * `batchId` within `timeout` millis of each other will be combined into a single
   * edit event.
   *
   * Paste events (including drag-and-drops), and events raised with unique `batchId`s
   * will finish the previous text event, if one exists, before logging their own,
   * separate event. 
   * 
   * (In general, any call to logEvent will cause any incomplete text event to resolve 
   * before proceeding - ie if `onTextUpdate(x)` is called before `logEvent(e)`, then
   * the data in `x` will appear before the data in `e` in the log.)
   *
   * @see _finishTextEvent for a way to manually end any current text event
   *
   * @param {InputEvent} event the original field onInput event
   * @param {(string | number)?} batchId the id used to unify a series of edits (null if force no batch)
   * @param {string} newText the new state of the text field
   * @param {number?} timeout the timeout for edit actions before logging the aggregate event
   */
  onTextUpdate(event, batchId, newText, timeout = 1500) {
    switch (event.inputType) {
      case "insertFromPaste":
      case "insertFromPasteAsQuotation":
      case "insertFromDrop":
        // calls this._finishTextEvent() first
        this.logEvent({
          type: "paste",
          duration: 0,
          batchId: batchId,
          value: newText,
        });
        break;
      // do something special with these?
      // case "deleteByDrag":
      // case "deleteByCut":
      default:
        const noBatch = batchId == null;

        if (this._last_text_event) {
          // if the last update was to a different field, finish the previous event
          // otherwise clear the timeout
          if (noBatch || this._last_text_event.batchId !== batchId) {
            this._finishTextEvent();
          } else {
            clearTimeout(this._last_text_event.timeout);
          }
        }

        this._last_text_event = {
          batchId: batchId,
          e: event,
          start: this._last_text_event
            ? this._last_text_event.start
            : Date.now(),
          value: newText,
          timeout: setTimeout(() => this._finishTextEvent(), timeout),
        };

        if (noBatch) this._finishTextEvent();
    }
  }

  /**
   * Finishes any text event that is still in progress and logs it.
   */
  _finishTextEvent() {
    if (!this._last_text_event) return;

    clearTimeout(this._last_text_event.timeout);

    const e = {
      type: "text",
      time: this._last_text_event.start,
      value: this._last_text_event.value,
      batchId: this._last_text_event.batchId,
    };

    // critical! Infinite-mutual-recursion if 
    // this field is not cleared before logEvent is called
    this._last_text_event = null;

    this.logEvent(e);
  }

  /**
   * A callback for when a submit button is pressed.
   * Logs a new submit event, and commits the log.
   */
  onSubmit() {
    this.logEvent({ type: "submit" });
    this.commit();
  }
  
  /**
   * JSONifies the current event log
   * @returns JSON string of the event log
   */
  dumpLog() {
    this._init();
    return JSON.stringify(this._events);
  }

  /**
   * Commits to the environments Firestore database. Requires 
   * `window.Firebase.Firestore` to be the Firestore module, and
   * `window.Firebase.app.db` to be the current Firebase app's  
   * Firestore database.
   * @param {boolean?} silent if true, no logging or alerting (even on failure)
   * @returns {boolean} true if wrote to firestore, false if entered recovery and
   * wrote to localStorage
   */
  async commit(silent=false) {
    var FStore, db;
    try { 
      FStore = Firebase.Firestore;
      db = Firebase.app.db;
    } catch (e) {
      this._deinit();
      silent || alert("Firestore not configured. Commit aborted!");
      return false;
    }

    try {
      let docId = window.localStorage.getItem("docId");

      const rawCommitData = docId
        ? {
            log: FStore.arrayUnion(...this._events),
          }
        : {
            docTitle: document.title,
            problemHash: this._problemHash,
            userHash: this._userHash,
            usernameStr: this._usernameStr,
            log: this._events,
            sent: Date.now(),
          };

      const commitData = this.map_commit
        ? this.map_commit(rawCommitData)
        : rawCommitData;
    
      if (docId) {
        await FStore.updateDoc(FStore.doc(db, "logs", docId), commitData);
      } else {
        const docRef = await FStore.addDoc(
          FStore.collection(db, "logs"),
          commitData
        );
        docId = docRef.id;
        window.localStorage.setItem("docId", docId);
      }

      silent || console.log("Document written with ID: ", docId);
      // clear committed events so they do not get commited twice!
      this._events = [];
    } catch (e) {
      this._deinit();
      silent || alert("Error adding document:\n" + e.toString());
      return false;
    }
    
    return true;
  }
}
