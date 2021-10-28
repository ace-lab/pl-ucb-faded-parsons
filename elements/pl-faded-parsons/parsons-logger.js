class ParsonsLogger extends Logger {
    constructor(widget) {
        super();
        this.widget = widget;
    }

    _map_reinit(e) {
        e.lines = this.widget.modified_lines.map(line =>
            ({ id: line.id, code: line.code, indent: line.indent })
        );
        return e;
    }

    map_resume(e) { return this._map_reinit(e); }

    map_init(e) { return this._map_reinit(e); }

    map_commit(data) {
        data.solutionCode = this.widget.solutionCode().map(t => t.replaceAll('\n', ';'));
        return data;
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
            solLines.push({ id: lineId, indent: indent });
        }
        this.logEvent({ type: event.type, targetId: lineId, solutionLines: solLines });
    }
    
    onTextUpdate(event, codeline) {
        super.onTextUpdate(event, codeline.name, codeline.value);
    }
}