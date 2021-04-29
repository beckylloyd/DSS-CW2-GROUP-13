//Modal shown at 9 minutes
const sessionTimeOut_Miliseconds = 540000;
//When user is logged in this is set
let sessionTimeOut_ID;
//To hold modal interval (to allow the seconds to continue to count down)
let x;

jQuery(document).ready(function ($) {
    let loggedIn = $("#loggedIn").text();
    //If the user is logged in, start tracking their last activity
    if (loggedIn === "True") {
        addEvents();
        startSession();
    }
});


function startSession() {
    sessionTimeOut_ID = window.setTimeout(endSession, sessionTimeOut_Miliseconds)
}

function endSession() {
    //stops tracking users activity
    removeEvents();
    document.getElementById("seconds-timer").innerHTML = "60";
    $('#timeoutModal').modal('show');
    let countdownTime = new Date().setSeconds(new Date().getSeconds() + 60);

    //updates every second
    x = setInterval(function () {
        let now = new Date();
        let distance = countdownTime - now;
        let seconds = Math.floor((distance % (1000 * 60)) / 1000);
        document.getElementById("seconds-timer").innerHTML = seconds.toString();

        //checks user button clicks
        jQuery(':button').click(function () {
            if (this.id === 'keepSession') {
                $('#timeoutModal').modal('hide');
                addEvents();
                resetTimer();
                extendSession();
                clearInterval(x);
            } else if (this.id === 'endSession') {
                $('#timeoutModal').modal('hide');
                logOutNow();
                clearInterval(x);
            }
        });

        //Once timer reaches 0, log out automatically
        if (distance < 1) {
            $('#timeoutModal').modal('hide');
            logOutNow();
            clearInterval(x);
        }

    }, 1000);

}


function resetTimer() {
    window.clearTimeout(sessionTimeOut_ID)
    startSession();
    clearInterval(x);
}

function logOutNow() {
    $.ajax({
        url: '/ajaxLogOut',
        type: 'POST',
        success: function (response) {
            document.location.href = '/logIn';
            console.log(response);
        },
        error: function (error) {
            console.log(error);
        }
    })
}

function extendSession() {
    $.ajax({
        url: '/ajaxExtend',
        type: 'POST',
        success: function (response) {
            console.log(response);
            document.location.reload();
        },
        error: function (error) {
            console.log(error);
        }
    });
}

function addEvents() {
    document.addEventListener("wheel", resetTimer, false);
    document.addEventListener("mousedown", resetTimer, false);
    document.addEventListener("keypress", resetTimer, false);
    document.addEventListener("touchmove", resetTimer, false);
}

function removeEvents() {
    document.removeEventListener("wheel", resetTimer, false);
    document.removeEventListener("mousedown", resetTimer, false);
    document.removeEventListener("keypress", resetTimer, false);
    document.removeEventListener("touchmove", resetTimer, false);
}