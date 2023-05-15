const port = 3000;

// Attach the debugger to the active tab
function attachDebugger(tabId) {
  chrome.debugger.attach({tabId: tabId}, '1.0', function() {
    // Enable the Network domain
    chrome.debugger.sendCommand({tabId: tabId}, 'Network.enable', {}, function() {
      // Set up listener for requestWillBeSent event
      chrome.debugger.onEvent.addListener(function(debuggeeId, message, params) {
        if (debuggeeId.tabId === tabId && message === 'Network.requestWillBeSent') {
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

    chrome.debugger.sendCommand({tabId: tabId}, 'Page.enable', {}, function() {
      // Set up listener for Page.windowOpen event
      chrome.debugger.onEvent.addListener(function(debuggeeId, message, params) {
        if (debuggeeId.tabId === tabId && message === 'Page.windowOpen') {
          console.log("url", params.url, "windowName", params.windowName, "userGesture", params.userGesture);
        }
      });
    });


  });
}

// Listen for new tab created events
chrome.tabs.onCreated.addListener(function(tab) {
  attachDebugger(tab.id);
});

// Attach the debugger to the active tab when the extension is first installed
chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
  attachDebugger(tabs[0].id);
});
