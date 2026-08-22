/* Login / Registration — client-side validation only.
   When the form is valid it submits normally (form POST -> redirect -> flash);
   the server is the real authority on whether the credentials are good. */

document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    var loginView = document.getElementById("loginView");
    var signupView = document.getElementById("signupView");
    var loginForm = document.getElementById("loginForm");
    var signupForm = document.getElementById("signupForm");
    var authWrap = document.querySelector(".auth-wrap");

    /* ---------- view toggle ---------- */

    function show(view) {
        var signup = view === "signup";
        loginView.hidden = signup;
        signupView.hidden = !signup;
        if (authWrap) {
            authWrap.style.maxWidth = signup ? "560px" : "420px";
        }
        clearErrors();
        window.scrollTo(0, 0);
    }

    document.getElementById("showSignup").addEventListener("click", function (e) {
        e.preventDefault();
        show("signup");
    });

    document.getElementById("showLogin").addEventListener("click", function (e) {
        e.preventDefault();
        show("login");
    });

    // if the server bounced a signup back, reopen the registration view
    if (window.location.hash === "#register") {
        show("signup");
    }

    /* ---------- photo preview ---------- */

    var photoInput = document.getElementById("signupPhoto");
    var photoPreview = document.getElementById("photoPreview");

    photoInput.addEventListener("input", function () {
        var url = photoInput.value.trim();
        if (url) {
            photoPreview.style.backgroundImage = 'url("' + url + '")';
            photoPreview.classList.add("has-image");
        } else {
            photoPreview.style.backgroundImage = "";
            photoPreview.classList.remove("has-image");
        }
    });

    /* ---------- login ---------- */

    loginForm.addEventListener("submit", function (event) {
        clearErrors();

        var username = document.getElementById("loginUsername");
        var password = document.getElementById("loginPassword");
        var valid = true;

        if (username.value.trim().length === 0) {
            showError(username, "Enter your username or email.");
            valid = false;
        }
        if (password.value.length === 0) {
            showError(password, "Enter your password.");
            valid = false;
        }

        if (!valid) {
            event.preventDefault();
        }
    });

    /* ---------- signup ---------- */

    signupForm.addEventListener("submit", function (event) {
        clearErrors();

        var first = document.getElementById("firstName");
        var last = document.getElementById("lastName");
        var email = document.getElementById("signupEmail");
        var password = document.getElementById("signupPassword");
        var confirm = document.getElementById("confirmPassword");
        var valid = true;

        if (first.value.trim().length < 2) {
            showError(first, "Enter your first name.");
            valid = false;
        }
        if (last.value.trim().length < 1) {
            showError(last, "Enter your last name.");
            valid = false;
        }
        if (!isValidEmail(email.value.trim())) {
            showError(email, "Enter a valid email address.");
            valid = false;
        }
        if (password.value.length < 8) {
            showError(password, "Password must be at least 8 characters.");
            valid = false;
        }
        if (confirm.value !== password.value) {
            showError(confirm, "Passwords do not match.");
            valid = false;
        }

        if (!valid) {
            event.preventDefault();
        }
    });

    /* ---------- helpers ---------- */

    function isValidEmail(value) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    }

    function showError(input, message) {
        input.classList.add("invalid");
        var slot = document.querySelector('.error-message[data-for="' + input.id + '"]');
        if (slot) {
            slot.textContent = message;
        }
    }

    function clearErrors() {
        document.querySelectorAll(".error-message").forEach(function (el) {
            el.textContent = "";
        });
        document.querySelectorAll(".input").forEach(function (el) {
            el.classList.remove("invalid");
        });
    }
});
