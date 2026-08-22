document.addEventListener("DOMContentLoaded", () => {

    const loginView = document.getElementById("loginView");
    const signupView = document.getElementById("signupView");

    const showSignup = document.getElementById("showSignup");
    const showLogin = document.getElementById("showLogin");

    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");

    const forgotButton = document.getElementById("forgotButton");


    /* =========================================
       SWITCH LOGIN / SIGNUP
    ========================================= */

    showSignup.addEventListener("click", () => {

        loginView.classList.remove("active");
        signupView.classList.add("active");

        clearErrors();

    });


    showLogin.addEventListener("click", () => {

        signupView.classList.remove("active");
        loginView.classList.add("active");

        clearErrors();

    });


    /* =========================================
       PASSWORD VISIBILITY
    ========================================= */

    document.querySelectorAll(".password-toggle").forEach(button => {

        button.addEventListener("click", () => {

            const targetId = button.dataset.target;
            const input = document.getElementById(targetId);

            if (input.type === "password") {

                input.type = "text";
                button.textContent = "Hide";

            } else {

                input.type = "password";
                button.textContent = "Show";

            }

        });

    });


    /* =========================================
       LOGIN
    ========================================= */

    loginForm.addEventListener("submit", (event) => {

        event.preventDefault();

        clearErrors();

        const email = document.getElementById("loginEmail");
        const password = document.getElementById("loginPassword");

        let valid = true;


        if (!isValidEmail(email.value.trim())) {

            showError(
                email,
                "Please enter a valid email address."
            );

            valid = false;

        }


        if (password.value.length === 0) {

            showError(
                password,
                "Please enter your password."
            );

            valid = false;

        }


        if (valid) {

            showSuccess(
                "Login successful! Database authentication will be connected next."
            );

        }

    });


    /* =========================================
       SIGNUP
    ========================================= */

    signupForm.addEventListener("submit", (event) => {

        event.preventDefault();

        clearErrors();

        const name = document.getElementById("signupName");
        const email = document.getElementById("signupEmail");
        const password = document.getElementById("signupPassword");
        const confirmPassword = document.getElementById("confirmPassword");

        let valid = true;


        if (name.value.trim().length < 2) {

            showError(
                name,
                "Please enter your name."
            );

            valid = false;

        }


        if (!isValidEmail(email.value.trim())) {

            showError(
                email,
                "Please enter a valid email address."
            );

            valid = false;

        }


        if (password.value.length < 8) {

            showError(
                password,
                "Password must contain at least 8 characters."
            );

            valid = false;

        }


        if (confirmPassword.value !== password.value) {

            showError(
                confirmPassword,
                "Passwords do not match."
            );

            valid = false;

        }


        if (valid) {

            showSuccess(
                "Account details validated! Database registration will be connected next."
            );

        }

    });


    /* =========================================
       FORGOT PASSWORD
    ========================================= */

    forgotButton.addEventListener("click", () => {

        const email = document.getElementById("loginEmail");

        clearErrors();

        if (!isValidEmail(email.value.trim())) {

            showError(
                email,
                "Enter your email first to reset your password."
            );

            email.focus();

            return;

        }

        showSuccess(
            "Password reset functionality will be connected to the backend."
        );

    });


    /* =========================================
       HELPERS
    ========================================= */

    function isValidEmail(email) {

        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

    }


    function showError(input, message) {

        input.classList.add("invalid");

        const group = input.closest(".input-group");

        const error = group.querySelector(".error-message");

        error.textContent = message;

    }


    function clearErrors() {

        document.querySelectorAll(".error-message").forEach(error => {
            error.textContent = "";
        });

        document.querySelectorAll("input").forEach(input => {
            input.classList.remove("invalid");
        });

    }


    function showSuccess(message) {

        alert(message);

    }

});