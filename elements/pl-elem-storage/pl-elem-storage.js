window.PlElemStorage ||= {
    stores: {},
    getStore: function(uuid) {
        if (uuid in this.stores) return this.stores[uuid];
        throw new Error(`No pl-elem-storage is regestered to uuid: ${uuid}`);
    },
    _registerStore: function(uuid) {
        if (!uuid) throw new Error(`Invalid uuid: '${uuid}'`);
        if (uuid in this.stores) throw new Error(`A store already exists for uuid` + uuid);
        const query = $('#elmstr-input-' + uuid);
        this.stores[uuid] = contents => {
            if (contents == null) { // retrieve current value and decode
                // the pl-rich-text-editor implementation does not call he.decode on retrieval
                // because the stored input is supposed to be valid html or JSON.
                return atob(query.val());
            }
            if (typeof contents !== 'string') throw new Error('Store contents must be string');
            return query.val(btoa(
                he.encode( // process non-ascii characters
                    contents, { allowUnsafeSymbols: true, useNamedReferences: true }
                )
            ));
        };
        return this.stores[uuid];
    }
};