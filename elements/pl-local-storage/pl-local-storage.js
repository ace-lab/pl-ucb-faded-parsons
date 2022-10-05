window['PlLocalStorage'] ||= {
  stores: {},
  registerStore: function(uuid) {
    if (uuid in this.stores) throw new Error(`A store already exists for uuid` + uuid);
    const query = $('#rte-input-' + uuid);
    this.stores[uuid] = contents => {
      if (contents == null) return atob(query.val());
      query.val(
        btoa(he.encode(contents, { allowUnsafeSymbols: true, useNamedReferences: true }))
      );
    }
    return this.stores[uuid];
  },
  getStore: function(uuid) {
    if (uuid in this.stores) return this.stores[uuid];
    throw new Error(`No pl-local-storage is regestered to uuid: ${uuid}`);
  },
  getVal: function(uuid) {
    return this.getStore(uuid)()
  },
  setVal: function(uuid, contents) {
    return this.getStore(uuid)(contents);
  }
};