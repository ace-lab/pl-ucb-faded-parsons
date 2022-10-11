window.PlElemStorage ||= {
    stores: {},
    _registerStore: function(uuid) {
        if (!uuid) throw new Error(`Invalid uuid: '${uuid}'`);
        if (uuid in this.stores) throw new Error(`A store already exists for uuid` + uuid);
        const query = $('#elmstr-input-' + uuid);
        this.stores[uuid] = contents => {
            if (contents == null) return atob(query.val()); // retrieve current value and decode
            if (!this._isNode(contents) && typeof contents !== 'string')
                throw new Error('Store contents must be string or Node');
            return query.val(btoa(he.encode( // safely store html and encode
                contents,
                { allowUnsafeSymbols: true, useNamedReferences: true }
            )));
        };
        return this.stores[uuid];
    },
    getStore: function(uuid) {
        if (uuid in this.stores) return this.stores[uuid];
        throw new Error(`No pl-elem-storage is regestered to uuid: ${uuid}`);
    },
    getVal: function(uuid) {
        return this.getStore(uuid)();
    },
    setVal: function(uuid, contents) {
        return this.getStore(uuid)(contents);
    },
    // https://stackoverflow.com/questions/384286/how-do-you-check-if-a-javascript-object-is-a-dom-object
    _isNode: function(o) {
        return typeof Node === "object"
            ? o instanceof Node
            : o && typeof o === "object" && typeof o.nodeType === "number" && typeof o.nodeName === "string";
    }
};