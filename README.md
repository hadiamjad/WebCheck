# Click-Hijacking
This chrome extension in `/extension` will intercept all click events such as 'click', 'mouseup', mousedown'
#### Steps
1. Clone this repository and move inside the repo directory using `cd` command
2. Open `two` terminals inside repository directory
---- First Terminal ----
3. In first terminal, run `cd server` and then `node server.js` -- this will start the local-host server at `Port:3000` which communicates with chrome-extension to save the captured data inside `server/output` directory. 
---- Second Terminal ----
1. Now crawl using selenium run `python automation.py` which is will open soccer-streams.io for 40 seconds. Interact with the pages by clicking.
2. This will collect all the clicks data (location, timestamp, stack) in `server/output/click.json`
3. Whereas, it will collect all the network requests info if the click was within 5 seconds of the request, secondly, you can verify it using 'hasUserGesture' in `server/output/request.json`

## Contact
Please contact [Hadi Amjad](https://hadiamjad.github.io/) if you run into any problems running the code or if you have any questions.