const express = require('express')
const app = express();
const bodyParser = require('body-parser');
const port = 3000;
const cors = require('cors');
const fs = require('fs');

const jsonfile = require('jsonfile');
let clickTrigger = ['null'];

app.use(cors({
    credentials: true,
    origin: true
}));
app.use(bodyParser.urlencoded({
    extended: true
}));
app.use(bodyParser.json());


fs.mkdir('output', (err) => {
  if (err) {
    console.error(err);
  } 
});

async function insertRequest(newHttpReq) {
    const file = 'output/request.json';
    jsonfile.writeFile(file, newHttpReq, {
        flag: 'a'
    }, function(err) {
        if (err) console.error(err);
    })
}

async function insertClicked(newHttpReq) {
    const file = 'output/click.json';
    jsonfile.writeFile(file, newHttpReq, {
        flag: 'a'
    }, function(err) {
        if (err) console.error(err);
    })
}


app.post('/request', (req, res) => {
    timeDiff = new Date().getTime() - clickTrigger[0];
    // collects request info if the click was within 5 seconds of the request
    if (timeDiff < 5000) {
        insertRequest(req.body);
    }
    res.send("request-success");
})

app.post('/clicked', (req, res) => {
    clickTrigger[0] = req.body.timestamp;
    insertClicked(req.body);
    res.send("clicked-success");
})

app.listen(port, () => {
    console.log(`Example app listening at http://localhost:${port}`);
})