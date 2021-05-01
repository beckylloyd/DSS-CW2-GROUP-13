var total = 0;
var pageX = 0;
var pageY = 0;

var flag1Clicked = false;
var flag2Clicked = true;
var flag3Clicked = true;
var flag4Clicked = true;
var flag5Clicked = true;




jQuery(document).ready(function ($) {
	$('#captchaModal').modal('show');
    document.getElementById("target").addEventListener('mousedown', logDown);
});

function logDown(mousePos)
{
	pageX = mousePos.pageX;
	pageY = mousePos.pageY;
	
	closeWindowClickChecker();
	flag1ClickChecker();
	flag2ClickChecker();
	flag3ClickChecker();
	flag4ClickChecker();
	flag5ClickChecker();
	
	document.getElementById('mouseLocation').innerHTML = "X = " + pageX + "<br>" + "Y = " + pageY;
};

function flag1ClickChecker()
{
	if(pageX < 1098 && pageX > 1059 && 
	   pageY > 475  && pageY < 507  && flag1Clicked == false)
	{
		document.getElementById('captcha').src = '.../CAPTCHA/2.png';
		flag1Clicked = true;
		flag2Clicked = false;
	}
};

function flag2ClickChecker()
{
	if(pageX < 861 && pageX > 832  && 
	   pageY > 539  && pageY < 571 && flag2Clicked == false)
	{
		document.getElementById('captcha').src = '.../CAPTCHA/3.png';
		flag2Clicked = true;
		flag3Clicked = false;
	}
};

function flag3ClickChecker()
{
	if(pageX < 984 && pageX > 945  && 
	   pageY > 696  && pageY < 728 && flag3Clicked == false)
	{
		document.getElementById('captcha').src = '.../CAPTCHA/4.png';
		flag3Clicked = true;
		flag4Clicked = false;
	}
};

function flag4ClickChecker()
{
	if(pageX < 907 && pageX > 869  && 
	   pageY > 696  && pageY < 728 && flag4Clicked == false)
	{
		document.getElementById('captcha').src = '.../CAPTCHA/5.png';
		flag4Clicked = true;
		flag5Clicked = false;
	}
};

function flag5ClickChecker()
{
	if(pageX < 1135 && pageX > 1098 && 
	   pageY > 571  && pageY < 602  && flag5Clicked == false)
	{
		flag5Clicked = true;
		document.getElementById('mouseLocation').innerHTML = "";
		document.getElementById('text').innerHTML = "";
		document.getElementById('usscac').innerHTML = "";
		document.getElementById('message').style.fontSize = '50px';
		document.getElementById('message').style.fontcolor = 'red';
		document.getElementById('message').innerHTML = "Nice job rook, you passed my Universally Secure, Security Checking, Authentication Captcha !";
		document.getElementById('captcha').src = 'bouncer.png';
		document.getElementById('captcha').height = '600';
		document.getElementById('captcha').width = '900';
	}
};

function closeWindowClickChecker()
{
	if(pageX < 1155 && pageX > 1049 && 
	   pageY > 245  && pageY < 286)
	{
		alert("Hey! You can not close... Mr Security's - Universally Secure, Security Checking, Authentication Captcha");
	}
};

function next(){  //this is declares the function. If the function had paramaters, these would be included in the brackets
		
	alert('Hello!');  //this is an alert. It brings up a message box
	
	total += 1;  //add one to the variable '0'
	
	var noun;  //create an empty variable called 'noun'
	
	if (total === 1) {  //this is your classic if/else statement
		noun = " time";
	} else {
		noun = " times";
	};
	
	document.getElementById('text').innerHTML = "The button has been pressed " + total + noun;  //change the text inside the 'text' div 
};