import express from 'express';
import Wordle from './wordle';

const app = express();
const port = 3080;
const wordle = new Wordle()

app.use(express.json())

app.post('/game', (req, res) => {
    if (!req.body?.user_id || !req.body?.guess) {
        res.status(400)
        res.send({"status": "error", "message": 'user_id or guess missing from request'})
        return
    }
    const result = wordle.make_guess(req.body.user_id, req.body.guess)
    console.log(result);
    res.send(result)
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});