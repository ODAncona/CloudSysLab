const express = require('express');
const request = require('request');

const app = express();
const port = 80;

app.get('/getImage', (req, res) => {
  
  
  // Fetch image from object storage and pipe to response
  res.sendFile('image.jpg');
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});

