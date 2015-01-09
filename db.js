var r = require('rethinkdb');
var assert = require('assert');
var connection = {
	conn : null
};


function call(callback) {
	r.connect({
		host : 'localhost',
		port : '28015'
	},function(err,conn){
		assert.ok(err == null, err);
		callback(err,conn);
	});
}

var conn = 
r.connect({
	host: 'localhost',
	port: '28015',
	db  : 'resultsdb',
	authkey: ''
},function(err,conn){
	if(err) throw err;
	connection.conn = conn;
	_conn = connection.conn
	console.log("connected to db");	
});

/* Table 1 results
   Table 2 gpa
   Table 3 students
*/   
call(function(err,conn){
	if (err) throw err;

	r.db("resultsdb").table("results").run(conn,function(err,result){
		if(err) throw err;
		console.log(result);

	});
});











