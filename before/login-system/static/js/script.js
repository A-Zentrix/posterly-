document.addEventListener('DOMContentLoaded', function () {
    const signUpButton = document.getElementById('signUp');
    const signInButton = document.getElementById('signIn');
    const container = document.getElementById('container');
    const backToLogin = document.getElementById('backToLogin');
    const registrationForm = document.getElementById('registrationForm');

    signUpButton.addEventListener('click', () => {
        container.style.display = 'none';
        registrationForm.style.display = 'block';
    });

    signInButton.addEventListener('click', () => {
        container.classList.remove("right-panel-active");
    });

    backToLogin.addEventListener('click', () => {
        container.style.display = 'flex';
        registrationForm.style.display = 'none';
    });

    // Show error message for 5 seconds
    const alert = document.querySelector('.alert');
    if (alert) {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    }

    // Toggle password visibility
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        const eyeIcon = document.createElement('i');
        eyeIcon.className = 'fas fa-eye';
        eyeIcon.style.position = 'absolute';
        eyeIcon.style.right = '25px';
        eyeIcon.style.top = '50%';
        eyeIcon.style.transform = 'translateY(-50%)';
        eyeIcon.style.cursor = 'pointer';

        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(eyeIcon);

        eyeIcon.addEventListener('click', () => {
            if (input.type === 'password') {
                input.type = 'text';
                eyeIcon.className = 'fas fa-eye-slash';
            } else {
                input.type = 'password';
                eyeIcon.className = 'fas fa-eye';
            }
        });
    });

    // ✅ Google Sign-Up Handler
    window.handleGoogleSignUp = function (response) {
        fetch('/google-register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ credential: response.credential })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                container.style.display = 'flex'; // Show main container
                registrationForm.style.display = 'none'; // Hide registration form
                window.location.href = '/'; // Redirect to home
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Google Sign-Up Error:', error);
            alert('An unexpected error occurred. Please try again.');
        });
    };
});
// Add this to your static JS file
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.querySelector('.register-form form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = this.elements.password.value;
            const confirmPassword = this.elements.confirm_password.value;
            
            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
            
            return true;
        });
    }
});