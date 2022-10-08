window.PlElemStorage ||= {
    stores: {},
    _registerStore: function(uuid) {
        if (uuid in this.stores) throw new Error(`A store already exists for uuid` + uuid);
        const query = $('#elmstr-input-' + uuid);
        this.stores[uuid] = contents =>
            contents == null
            ? atob(query.val())         // retrieve current value and decode
            : query.val(btoa(he.encode( // safely store html and encode
                contents,
                { allowUnsafeSymbols: true, useNamedReferences: true }
            )));
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
    }
};