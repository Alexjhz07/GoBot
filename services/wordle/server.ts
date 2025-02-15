import express from 'express';
import Wordle from './wordle';
import Longdle from './longdle';

const app = express();
const port = 3915;
const wordle = new Wordle()
const longdle = new Longdle()

app.use(express.json())

app.post('/wordle', (req, res) => {
    if (!req.body?.user_id || !req.body?.guess) {
        res.status(400)
        res.send({"status": "error", "message": 'user_id or guess missing from request'})
        return
    }
    wordle.make_guess(req.body.user_id, req.body.guess).then((result) => {
        res.send(result)  
    })
});

app.post('/longdle', (req, res) => {
    if (!req.body?.user_id || !req.body?.guess) {
        res.status(400)
        res.send({"status": "error", "message": 'user_id or guess missing from request'})
        return
    }
    longdle.make_guess(req.body.user_id, req.body.guess).then((result) => {
        res.send(result)  
    })
});

app.listen(port, () => {
    console.log(`Wordle is running on port ${port}`);
});