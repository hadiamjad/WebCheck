// Store the original document.cookie as soon as the script is loaded
// This ensures that we capture the original cookie before any scripts have a chance to modify it
var originalDocumentCookie = document.__lookupGetter__("cookie").bind(document).toString();

// Function to check monkey patching
function checkMonkeyPatching(scriptUrl) {
    if (document.__lookupGetter__("cookie").bind(document).toString() !== originalDocumentCookie) {
        console.log('document.cookie has been monkey patched!', document.cookie.toString(), originalDocumentCookie);
    }
    else {
        console.log('document.cookie is safe');
    }
}

// Observer for detecting new script elements
var observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        for (var i = 0; i < mutation.addedNodes.length; i++) {
            var node = mutation.addedNodes[i];
            // Check for monkey patching and print script URL
            var scriptUrl = node.src || 'inline script';
            console.log('Script URL: ', node);
            checkMonkeyPatching(scriptUrl);
        }
    });
});

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    originalDocumentCookie = document.__lookupGetter__("cookie").bind(document).toString();

    // Configuration of the observer:
    var config = { childList: true, subtree: true };

    // Start observing the document body for added nodes
    observer.observe(document.body, config);
});
