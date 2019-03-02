const express = require("express");
var app = express();
app.listen(3000, function () {
  console.log("server running on port 3000");
})


app.get("/testpython", callPython);
function callPython(req, res) {
  // using spawn instead of exec, prefer a stream over a buffer
  // to avoid maxBuffer issue
  var spawn = require('child_process').spawn;
  var process = spawn("python", ['./testpython.py',
    req.query.int, // starting int
  ]);
  process.stdout.on("data", function (data) {
    res.send(data.toString());
  });
}
