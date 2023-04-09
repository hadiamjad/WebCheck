## Setting the apporpriate flag for 3P-cookie-blocking
See `sele.py` -- `line 38-39`
Allow All cookies set preference to `prefs = {"profile.cookie_controls_mode": 0}`
Block 3p cookies set preference to `{"profile.cookie_controls_mode": 1, "profile.default_content_setting_values.cookies": 0}`

## List of websites
specify list of websites in `test.csv`

## Data Collected

All the data crawled for specific website is stored in 
`server/output` directory. The schema for specific file is as follows:
#### Schema
- `request.json` -- https://chromedevtools.github.io/devtools-protocol/tot/Network/#event-requestWillBeSent

- `requestInfo.json` -- https://chromedevtools.github.io/devtools-protocol/tot/Network/#event-requestWillBeSentExtraInfo

- `responses.json` -- https://chromedevtools.github.io/devtools-protocol/tot/Network/#event-responseReceived

- `responsesInfo.json` -- https://chromedevtools.github.io/devtools-protocol/tot/Network/#event-responseReceivedExtraInfo

- `cookie_storage.json` --  local-storage and cookie getter/setter by javascript. It has complete call stack and cookie information.

- `cookieTableActivity.json` -- https://developer.chrome.com/docs/extensions/reference/cookies/#event-onChanged