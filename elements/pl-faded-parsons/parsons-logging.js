var ParsonsLogger = function(parson) {
    this.parson = parson;
};

ParsonsLogger.prototype.onSortableUpdate = function(event, ui) {
    console.log(event);
};

ParsonsLogger.prototype.onBlankUpdate = function(event, codeline) {
    console.log(event, codeline);
}