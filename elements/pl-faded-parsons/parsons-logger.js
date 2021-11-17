/**
 * A class that performs the funcitonality specific to ParsonsWidget logging.
 */
class ParsonsLogger extends Logger {
    constructor(widget) {
        super();
        this.widget = widget;
    }

    /**
     * Adds a record of the modified code lines to the event
     * @param {*} e incoming event
     * @returns modified event
     */
    _map_reinit(e) {
        e.lines = this.widget.modified_lines.map(line =>
            ({ id: line.id, code: line.code, indent: line.indent })
        );
        return e;
    }

    // Alter the resume and  init events before they are logged
    // so they contain a record of modified code lines at the onset.
    map_resume(e) { return this._map_reinit(e); }
    map_init(e) { return this._map_reinit(e); }

    // On commit, fetch the solution code and clean it
    map_commit(e) {
        e.solutionCode = this.widget.solutionCode().map(t => t.replaceAll('\n', ';'));
        return e;
    }
    
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
            const lineId = child.id;
            const modLine = this.widget.getLineById(lineId);
            const indent = modLine && modLine.indent;
            solLines.push({ id: lineId, indent: indent });
        }
        this.logEvent({ type: event.type, targetId: lineId, solutionLines: solLines });
    }
    
    /**
     * A callback for capturing codeline text edits
     * @param {InputEvent} event the original onInput event
     * @param {ParsonsCodeline} codeline the codeline that was editted
     */
    onTextUpdate(event, codeline) {
        super.onTextUpdate(event, codeline.name, codeline.value);
    }
}