document.addEventListener("DOMContentLoaded", function() {
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirmPassword");
    const passwordMatchError = document.getElementById("password-match-error");

    confirmPasswordInput.addEventListener("input", function() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (password === confirmPassword) {
            passwordMatchError.textContent = "";
        } else {
            passwordMatchError.textContent = "Passwords do not match.";
        }
    });

    document.getElementById("signup-form").addEventListener("submit", function(event) {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (password !== confirmPassword) {
            passwordMatchError.textContent = "Passwords do not match.";
            event.preventDefault(); // Prevent form submission
        }
    });
});