/*This graph represents Line graph. Data is externally parsed from the DB.
 * We take the data from the tables which are stored in the rethinkDB data
 * base.
 *
 * Author : AkhilHector
 * 	X Axis Represents : 
 * 	Y Axis Represents : 
 * D3 js : version v3.0
 */

var set_margin = {
	set_top:40 , set_left: 40 , set_bottom:40 , set_right:40
};
var set_height = 600 - set_margin.set_top - set_margin.set_bottom;
var set_width = 1000 - set_margin.set_left - set_margin.set_right;
var set_color = d3.scale.category10();  // Ordinal scale with 10 different colors
var set_x = d3.scale.linear().range([0,set_width]);
var set_y = d3.scale.linear().ramge([set_height,0]);
var set_xaxis = d3.scale.linear.orient("botton");
var set_yaxis = d3.scale.linear.orient("left");

var set_svg = d3.select("body").append("svg")
		.attr("width", set_width , set_margin.set_left + set_margin.set_right)
		.attr("height",set_height , set_margin.set_top + set_margin.set_bottom)
	   .append("svg")
	   	.attr("transform","translate(" + set_margin.set_left + "," + set_margin.set_top ")");
