console.log("Hello!")
var chp_number = 1;
$("button").click(function() {
   $("#list").append("<br><label> Chapter Title: </label>");
   var chp_title = "chp_title" + chp_number;
   $("#list").append("<input type=\"text\" name=" + chp_title + " /><br><br>");
   $("#list").append("<label> Chapter Description: </label>");
   var chp_description = "chp_description" + chp_number;
   $("#list").append("<textarea name=" + chp_description + " ></textarea><br><br>");
   $("#list").append("<label> Chapter Video: </label>");
   var chp_video = "chp_video" + chp_number;
   $("#list").append('<input type="file" name=' + chp_video + ' /><br><br><br>');
   ++chp_number;
});