console.log(document.__lookupGetter__("cookie").bind(document).toString());
console.log(document.__lookupSetter__("cookie").bind(document).toString());
console.log(window.Storage.prototype.setItem.toString());
console.log(window.Storage.prototype.getItem.toString());
