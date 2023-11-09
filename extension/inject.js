var cookieGetter = document.__lookupGetter__("cookie").bind(document);
var cookieSetter = document.__lookupSetter__("cookie").bind(document);

Object.defineProperty(document, 'cookie', {
    get: function() {
        var storedCookieStr = cookieGetter();
        fetch("http://localhost:3000/cookiestorage", {
            method: "POST",
            body: JSON.stringify({
                "top_level_url": window.location.href,
                "function": "cookie_getter",
                "cookie": storedCookieStr,
                "stack": new Error().stack
            }),
            mode: 'cors',
            headers: {
                'Access-Control-Allow-Origin': '*',
                "Content-Type": "application/json"
            }
        }).then(res => {
            console.log("CookieStorage collected");
        });
        return cookieGetter();
    },

    set: function(cookieString) {
        fetch("http://localhost:3000/cookiestorage", {
            method: "POST",
            body: JSON.stringify({
                "top_level_url": window.location.href,
                "function": "cookie_setter",
                "cookie": cookieString,
                "stack": new Error().stack
            }),
            mode: 'cors',
            headers: {
                'Access-Control-Allow-Origin': '*',
                "Content-Type": "application/json"
            }
        }).then(res => {
            console.log("CookieStorage collected");
        });
        return cookieSetter(cookieString);
    }
});