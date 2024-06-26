
// Message/Notification timer

var message_timeout = document.getElementById("message-timer");

if (message_timeout) {
    setTimeout(function() {
      message_timeout.style.display = "none";
    }, 5000);
  } else {
    // console.log("Element not found");
  }



/*!
* Start Bootstrap - Stylish Portfolio v6.0.5 (https://startbootstrap.com/theme/stylish-portfolio)
* Copyright 2013-2022 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-stylish-portfolio/blob/master/LICENSE)
*/
document.addEventListener('DOMContentLoaded', event => {

    const sidebarWrapper = document.getElementById('sidebar-wrapper');
    let scrollToTopVisible = false;
    // Closes the sidebar menu
    const menuToggle = document.body.querySelector('.menu-toggle');

    if (menuToggle){
        menuToggle.addEventListener('click', event => {
            event.preventDefault();
            sidebarWrapper.classList.toggle('active');
            _toggleMenuIcon();
            menuToggle.classList.toggle('active');
        })
    }
    

    // Closes responsive menu when a scroll trigger link is clicked
    var scrollTriggerList = [].slice.call(document.querySelectorAll('#sidebar-wrapper .js-scroll-trigger'));
    scrollTriggerList.map(scrollTrigger => {
        scrollTrigger.addEventListener('click', () => {
            sidebarWrapper.classList.remove('active');
            menuToggle.classList.remove('active');
            _toggleMenuIcon();
        })
    });

    function _toggleMenuIcon() {
        const menuToggleBars = document.body.querySelector('.menu-toggle > .fa-bars');
        const menuToggleTimes = document.body.querySelector('.menu-toggle > .fa-xmark');
        if (menuToggleBars) {
            menuToggleBars.classList.remove('fa-bars');
            menuToggleBars.classList.add('fa-xmark');
        }
        if (menuToggleTimes) {
            menuToggleTimes.classList.remove('fa-xmark');
            menuToggleTimes.classList.add('fa-bars');
        }
    }

    // Scroll to top button appear
    document.addEventListener('scroll', () => {
        const scrollToTop = document.body.querySelector('.scroll-to-top');
        if (document.documentElement.scrollTop > 100) {
            if (!scrollToTopVisible) {
                fadeIn(scrollToTop);
                scrollToTopVisible = true;
            }
        } else {
            if (scrollToTopVisible) {
                fadeOut(scrollToTop);
                scrollToTopVisible = false;
            }
        }
    })
})

function fadeOut(el) {
    if (!el || !(el instanceof Element)) {
        // console.error('Invalid DOM element provided.');
        return;
      }

    el.style.setProperty('opacity', 1);
    (function fade() {
        if ((el.style.opacity -= .1) < 0) {
            el.style.display = "none";
        } else {
            requestAnimationFrame(fade);
        }
    })();
};

function fadeIn(el, display) {

    if (!el || !(el instanceof Element)) {
        // console.error('Invalid DOM element provided.');
        return;
      }
    el.style.setProperty('opacity','0');
    el.style.display = display || "block";
    (function fade() {
        var val = parseFloat(el.style.opacity) || 0;
        if (!((val += .1) > 1)) {
            el.style.opacity = val;
            requestAnimationFrame(fade);
        }
    })();
};


$(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })

function animateProgressBar(progressBarId, currentValue, targetValue, duration) {
    var progressBar = document.querySelector(`#${progressBarId} .progress-bar`);

    
    if (isNaN(targetValue)) {
        
        progressBar.style.width = '0%';
        progressBar.setAttribute('aria-valuenow', 0);
        progressBar.setAttribute('aria-valuemin', 0);
        progressBar.setAttribute('aria-valuemax', 100);
        progressBar.textContent = '0%';
        return; 
    }

    var start = null;
    var step = function (timestamp) {
        if (!start) start = timestamp;
        var progress = timestamp - start;
        var percentage = Math.min(currentValue + (progress / duration) * (targetValue - currentValue), targetValue);
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
        progressBar.textContent = percentage.toFixed(0) + '%';
        if (progress < duration) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}


// for register password view
function togglePasswordVisibility(inputId) {
    const passwordInput = document.getElementById(inputId);
    const passwordToggleIcon = passwordInput.parentElement.querySelector('.password-toggle-icon i');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        passwordToggleIcon.classList.remove('fa-eye');
        passwordToggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        passwordToggleIcon.classList.remove('fa-eye-slash');
        passwordToggleIcon.classList.add('fa-eye');
    }
}






