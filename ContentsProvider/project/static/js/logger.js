//Vue.http.options.emulateJSON = true; // send as 

var data = {name: "abc", rank: "MID RANGE"};
var vue = new Vue();
vue.$http.post('http://localhost:8000/log', JSON.stringify(data))
