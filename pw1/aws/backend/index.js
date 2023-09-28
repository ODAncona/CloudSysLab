const express = require('express');
const request = require('request');

const app = express();
const port = 80;

app.get('/getImage', (req, res) => {
  const imageUrl = req.query.url; // Assuming URL is passed as a query parameter
  if (!imageUrl) {
    return res.status(400).send('URL is required');
  }
  
  // Fetch image from object storage and pipe to response
  request(imageUrl).pipe(res);
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});

