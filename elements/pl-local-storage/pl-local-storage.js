$(function() {
  window['PlLocalStorage'] ||= {
    stores: {},
    registerStore: function(uuid, selector) {
      const query = $(selector);
      if (!query.length) throw new Error(`No element exists for selector '${selector}' (attepmting to register to uuid ${uuid})`);
      this.stores[uuid] = query;
      return contents =>
        query.val(btoa(he.encode(
              contents,
              {
                allowUnsafeSymbols: true, // HTML tags should be kept
                useNamedReferences: true,
              }
            )));
    },
    getStore: function(uuid) {
      if (uuid in this.stores) return this.stores[uuid];
      throw new Error(`No pl-local-storage is regestered to uuid: ${uuid}`);
    },
    getVal: function(uuid) {
      return this.getStore(uuid).val()
    },
    setVal: function(uuid, contents) {
      return this.getStore(uuid).val(contents);
    }
  }
})
