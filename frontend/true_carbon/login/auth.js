// Authentication client logic
// This file contains frontend-only mock behavior and detailed comments
// showing where to integrate your backend API (FastAPI) endpoints.
//
// Key notes for beginners:
// - The frontend submits credentials to the backend (example: POST /auth/jwt/login)
// - The backend should return a token (JWT) and user info on success
// - Store the token in localStorage (or cookies with HttpOnly in production)
// - Send the token on subsequent API requests in the Authorization header
//
// Sample commented fetch examples are provided below in the login and signup handlers.

document.addEventListener('DOMContentLoaded', function () {
    // Helper: support two naming styles (original project and merged modal)
    const loginForm = document.getElementById('loginForm') || document.getElementById('login-form');
    const signupForm = document.getElementById('signupForm') || document.getElementById('signup-form');

    // Elements for the standalone modal-style forms (existing in index.html)
    const modalLoginForm = document.getElementById('login-form');
    const modalSignupForm = document.getElementById('signup-form');

    // Generic error/success elements used by both layouts (if present)
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const signupError = document.getElementById('signupError');
    const signupSuccess = document.getElementById('signupSuccess');

    // -------------------------
    // LOGIN HANDLER (mock + integration guidance)
    // -------------------------
    const attachLogin = (form) => {
        if (!form) return;

        form.addEventListener('submit', async function (e) {
            e.preventDefault();

            const email = (document.getElementById('email') || {}).value || '';
            const password = (document.getElementById('password') || {}).value || '';

            // MOCK CHECK (for local demo only) - use these credentials for testing:
            // Email: nakija540@gmail.com
            // Password: 123456
            if (email === 'nakija540@gmail.com' && password === '123456') {
                if (errorMessage) errorMessage.style.display = 'none';
                // Simulate successful login
                alert('Login successful! (mock) Redirecting to dashboard...');
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('userEmail', email);
                setTimeout(() => { window.location.href = 'dashboard.html'; }, 800);
                return;
            }

            // PRODUCTION / REAL BACKEND EXAMPLE (commented)
            // Replace the mock block above with code like this to call your FastAPI backend:
            /*
            try {
                const res = await fetch('/auth/jwt/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: email, password })
                });

                if (!res.ok) throw new Error('Invalid credentials');

                const data = await res.json();
                // Example response: { access_token: '...', token_type: 'bearer', user: { email: '...' } }
                // Store token (for demo we store in localStorage; in production prefer secure cookies)
                localStorage.setItem('authToken', data.access_token);
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('userEmail', data.user?.email || email);
                window.location.href = 'dashboard.html';
            } catch (err) {
                if (errorMessage) { errorMessage.style.display = 'block'; errorMessage.innerText = 'Login failed. ' + err.message; }
            }
            */

            // Default failure UX for mock
            if (errorMessage) errorMessage.style.display = 'block';
            if (successMessage) successMessage.style.display = 'none';

            // Add temporary shake animation if form exists
            form.style.animation = 'shake 0.5s';
            setTimeout(() => { form.style.animation = ''; }, 500);
        });
    };

    // attach to any found login forms
    attachLogin(loginForm);
    attachLogin(modalLoginForm);

    // -------------------------
    // SIGNUP HANDLER (mock + integration guidance)
    // -------------------------
    const attachSignup = (form) => {
        if (!form) return;

        // Optional password validation used by original signup UI
        function validatePassword(password) {
            const minLength = 8;
            const hasUpperCase = /[A-Z]/.test(password);
            const hasLowerCase = /[a-z]/.test(password);
            const hasNumbers = /\d/.test(password);
            return { isValid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers };
        }

        form.addEventListener('submit', async function (e) {
            e.preventDefault();

            const name = (document.getElementById('signupName') || document.getElementById('signup-name') || {}).value || '';
            const email = (document.getElementById('signupEmail') || document.getElementById('signup-email') || {}).value || '';
            const password = (document.getElementById('signupPassword') || document.getElementById('signup-password') || {}).value || '';
            const confirmPassword = (document.getElementById('confirmPassword') || {}).value || '';
            const termsAccepted = (document.getElementById('terms') || {}).checked || false;

            const errors = [];
            if (!name.trim()) errors.push('Full name is required');
            if (!email.trim()) errors.push('Email is required');
            if (!validatePassword(password).isValid) errors.push('Password must be at least 8 chars with upper/lower/number');
            if (password !== confirmPassword) errors.push('Passwords do not match');
            if (!termsAccepted) errors.push('You must accept the terms');

            if (errors.length > 0) {
                if (signupError) { signupError.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${errors.join('<br>')}`; signupError.style.display = 'block'; }
                return;
            }

            // Mock signup: store and redirect
            localStorage.setItem('userName', name);
            localStorage.setItem('userEmail', email);
            localStorage.setItem('isLoggedIn', 'true');
            if (signupSuccess) signupSuccess.style.display = 'block';
            setTimeout(() => { window.location.href = 'dashboard.html'; }, 1200);

            // PRODUCTION / REAL BACKEND EXAMPLE (commented)
            /*
            try {
                const res = await fetch('/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password, name })
                });

                if (!res.ok) throw new Error('Signup failed');
                const data = await res.json();
                // store token if provided
                localStorage.setItem('authToken', data.access_token);
                localStorage.setItem('isLoggedIn', 'true');
                window.location.href = 'dashboard.html';
            } catch (err) {
                if (signupError) { signupError.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${err.message}`; signupError.style.display = 'block'; }
            }
            */
        });
    };

    attachSignup(signupForm);
    attachSignup(modalSignupForm);

    // -------------------------
    // DASHBOARD ACCESS CHECK
    // -------------------------
    // If the user opens dashboard.html directly we check localStorage
    if (window.location.pathname.includes('dashboard.html')) {
        const isLoggedIn = localStorage.getItem('isLoggedIn');
        if (isLoggedIn !== 'true') {
            // Redirect to the landing page (which now contains the login modal)
            window.location.href = 'index.html';
        }
    }

    // -------------------------
    // SHAKE ANIMATION (re-used)
    // -------------------------
    const style = document.createElement('style');
    style.textContent = `
        @keyframes shake { 0%,100%{ transform: translateX(0); } 10%,30%,50%,70%,90%{ transform: translateX(-5px);} 20%,40%,60%,80%{ transform: translateX(5px);} }
    `;
    document.head.appendChild(style);
});