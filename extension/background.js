const port = 3000;
// Attach the debugger to the active tab
chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
  chrome.debugger.attach({tabId: tabs[0].id}, '1.0', function() {
    // Enable the Network domain
    chrome.debugger.sendCommand({tabId: tabs[0].id}, 'Network.enable', {}, function() {
      // Set up listener for requestWillBeSent event
      chrome.debugger.onEvent.addListener(function(debuggeeId, message, params) {
        if (debuggeeId.tabId === tabs[0].id && message === 'Network.requestWillBeSent') {
          fetch(`http://localhost:${port}/request`, {
                  method: "POST",
                  body: JSON.stringify({
                    "http_req": params.request.url,
                    "request_id": params.requestId,
                    "frame_url": params.documentURL,
                    "resource_type": params.type,
                    "header": params.request.headers,
                    "timestamp": new Date().getTime(),
                    "frameId": params.frameId,
                    "hasUserGesture": params.hasUserGesture,
                    "call_stack": params.initiator
                  }),
                  mode: 'cors',
                  headers: {
                      'Access-Control-Allow-Origin': '*',
                      "Content-Type": "application/json"
                  }
      });
        }
      });
    });
  });
});
