// TRUE CARBON Landing Page Interactive Functionality
document.addEventListener('DOMContentLoaded', function() {
    
    // ============================================
    // MODAL FUNCTIONALITY - Handles login/signup popup
    // ============================================
    const modal = document.getElementById('auth-modal');
    const loginBtn = document.getElementById('login-btn');
    const signupBtn = document.getElementById('signup-btn');
    const heroSignupBtn = document.getElementById('hero-signup');
    const finalSignupBtn = document.getElementById('final-signup');
    const demoBtn = document.getElementById('demo-btn');
    const closeModalBtn = document.querySelector('.close-modal');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const switchTabLinks = document.querySelectorAll('.switch-tab');
    
    // Function to open modal with specific tab
    function openModal(tabName) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling
        
        // Switch to the correct tab
        switchTab(tabName);
    }
    
    // Function to close modal
    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto'; // Restore scrolling
    }
    
    // Function to switch between login and signup tabs
    function switchTab(tabName) {
        // Update active tab button
        tabBtns.forEach(btn => {
            if (btn.getAttribute('data-tab') === tabName) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            if (content.id === `${tabName}-tab`) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
    }
    
    // Event listeners for opening modal
    loginBtn.addEventListener('click', () => openModal('login'));
    signupBtn.addEventListener('click', () => openModal('signup'));
    heroSignupBtn.addEventListener('click', () => openModal('signup'));
    finalSignupBtn.addEventListener('click', () => openModal('signup'));
    demoBtn.addEventListener('click', () => {
        alert('Thank you for your interest! Our team will contact you within 24 hours to schedule a demo.');
    });
    
    // Event listeners for closing modal
    closeModalBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Event listeners for tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Event listeners for switch links inside modal
    switchTabLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = link.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // ============================================
    // FORM HANDLING - Manages form submissions
    // ============================================
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const newsletterForm = document.getElementById('newsletter-form');
    
    // Login form submission
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Mock authentication with provided credentials
        if (email === 'nakija540@gmail.com' && password === 'nakija540@gmail.com') {
            alert('Login successful! Welcome to TRUE CARBON.');
            closeModal();
            
            // In a real app, you would redirect to dashboard here
            // window.location.href = 'dashboard.html';
        } else {
            alert('Invalid credentials. Please try again.\n\nDemo credentials:\nEmail: nakija540@gmail.com\nPassword: nakija540@gmail.com');
        }
    });
    
    // Signup form submission
    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const name = document.getElementById('signup-name').value;
        const company = document.getElementById('signup-company').value;
        
        alert(`Thank you ${name} from ${company}! Your 15-day free trial has been activated. Check your email for login instructions.`);
        closeModal();
    });
    
    // Newsletter form submission
    newsletterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const email = newsletterForm.querySelector('input[type="email"]').value;
        alert(`Thank you for subscribing with ${email}! You'll receive our carbon insights newsletter soon.`);
        newsletterForm.reset();
    });
    
    // ============================================
    // CHART VISUALIZATIONS - Creates pollution/carbon data charts
    // ============================================
    // Global CO2 Emissions Chart
    const co2Ctx = document.getElementById('co2Chart').getContext('2d');
    const co2Chart = new Chart(co2Ctx, {
        type: 'line',
        data: {
            labels: ['2020', '2021', '2022', '2023', '2024'],
            datasets: [{
                label: 'CO2 Emissions (Gt)',
                data: [34.8, 36.3, 36.6, 37.1, 37.4],
                borderColor: '#0a7c5f',
                backgroundColor: 'rgba(10, 124, 95, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Gigatons of CO2'
                    }
                }
            }
        }
    });
    
    // Carbon Credit Project Types Chart
    const projectCtx = document.getElementById('projectChart').getContext('2d');
    const projectChart = new Chart(projectCtx, {
        type: 'doughnut',
        data: {
            labels: ['Reforestation', 'Renewable Energy', 'Methane Capture', 'Soil Carbon', 'Blue Carbon'],
            datasets: [{
                data: [35, 25, 20, 15, 5],
                backgroundColor: [
                    '#0a7c5f',
                    '#1a3c34',
                    '#34d399',
                    '#065c46',
                    '#2a5298'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // Deforestation vs Reforestation Chart
    const forestCtx = document.getElementById('forestChart').getContext('2d');
    const forestChart = new Chart(forestCtx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [
                {
                    label: 'Deforestation (Ha)',
                    data: [120, 190, 300, 500, 200, 300],
                    backgroundColor: 'rgba(220, 53, 69, 0.7)',
                    borderColor: 'rgb(220, 53, 69)',
                    borderWidth: 1
                },
                {
                    label: 'Reforestation (Ha)',
                    data: [200, 220, 350, 400, 300, 450],
                    backgroundColor: 'rgba(10, 124, 95, 0.7)',
                    borderColor: 'rgb(10, 124, 95)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Hectares'
                    }
                }
            }
        }
    });
    
    // ============================================
    // SMOOTH SCROLLING - For navigation links
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // ============================================
    // NAVBAR SCROLL EFFECT - Changes navbar on scroll
    // ============================================
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 5px 20px rgba(0, 0, 0, 0.1)';
            navbar.style.padding = '10px 0';
        } else {
            navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.05)';
            navbar.style.padding = '15px 0';
        }
    });
    
    // ============================================
    // ANIMATION ON SCROLL - Adds fade-in effect for elements
    // ============================================
    function animateOnScroll() {
        const elements = document.querySelectorAll('.feature-card, .step, .solution-card, .chart-box');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.2;
            
            if (elementPosition < screenPosition) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    }
    
    // Set initial state for animated elements
    document.querySelectorAll('.feature-card, .step, .solution-card, .chart-box').forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });
    
    // Run on load and scroll
    window.addEventListener('load', animateOnScroll);
    window.addEventListener('scroll', animateOnScroll);
    
    // ============================================
    // CONSOLE WELCOME MESSAGE
    // ============================================
    console.log('%c🚀 TRUE CARBON MRV Platform', 'color: #0a7c5f; font-size: 18px; font-weight: bold;');
    console.log('%cWelcome to the future of carbon credit verification!', 'color: #1a3c34; font-size: 14px;');
    console.log('%cDemo login: nakija540@gmail.com | Password: nakija540@gmail.com', 'color: #065c46; font-size: 12px;');
});