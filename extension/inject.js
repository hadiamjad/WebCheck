checkMonkeyPatching = function() {
    fetch("http://localhost:3000/cookiestorage", {
            method: "POST",
            body: JSON.stringify({
                "top_level_url": window.location.href,
                "cookie_getter": document.__lookupGetter__("cookie").toString(),
                "cookie_setter": document.__lookupSetter__("cookie").toString(),
                "storage_getter": window.Storage.prototype.getItem.toString(),
                "storage_setter": window.Storage.prototype.setItem.toString(),
            }),
            mode: 'cors',
            headers: {
                'Access-Control-Allow-Origin': '*',
                "Content-Type": "application/json"
            }
        }).then(res => {
            console.log("CookieStorage collected");
        });
}

setInterval(checkMonkeyPatching, 5000);