var pageX = 0;
var pageY = 0;

var imageNo = 0;
var ready = true;

jQuery(document).ready(function ($) {
    $('#captchaModal').modal('show');
    document.getElementById("dismissButton").style.display = "none";
    document.getElementById('target').style.display = "block";
    document.getElementById('message').style.display = "block";
    if (ready) {
        ready = false;
        getCaptcha();
    }

});


function getCaptcha() {
    $.ajax({
        url: '/getCaptcha',
        type: 'POST',
        success: function (response) {
            let res = JSON.parse(response);
            if (res.status === 'OK') {
                imageNo = res.image;
                document.getElementById('captcha').src = 'static/CAPTCHA/' + res.image + '.png';
            } else {
                document.getElementById('target').style.display = "none";
                document.getElementById('message').style.display = "none";
                document.getElementById("dismissButton").style.display = "block";
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
}


function getImageCoords(event, img) {
    var posX = event.offsetX ? (event.offsetX) : event.pageX - img.offsetLeft;
    var posY = event.offsetY ? (event.offsetY) : event.pageY - img.offsetTop;

    $.ajax({
        url: '/validateCaptcha',
        data: {y: posY, x: posX, imageNumber: imageNo},
        type: 'POST',
        success: function (response) {
            let res = JSON.parse(response);
            if (res.status === 'validation failed') {
                document.getElementById('captcha').src = 'static/CAPTCHA/' + imageNo + '.png';
            } else {
                getCaptcha();
            }
            console.log(response);
        },
        error: function (error) {
            console.log(error);
            return;
        }
    });
}


function buttonClick() {
    $('#captchaModal').modal('hide');
    $.ajax({
        url: '/userLogIn',
        type: 'POST',
        success: function (response) {
            let res = JSON.parse(response);
            if (res.status === 'error') {
                document.location.href = '/logIn'
            } else {
                document.location.href = '/'
            }
        },
        error: function (error) {
            console.log(error);
            document.location.href = '/logIn'
        }
    });

}

