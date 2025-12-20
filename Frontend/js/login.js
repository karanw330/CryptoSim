// State management
        let currentForm = 'login'; // 'login', 'signup', 'otp-email', 'otp-verify'
        let otpUserEmail = '';
        let resendTimer = null;
        let resendCountdown = 30;

        // Backend simulation functions
        async function checkEmailExists(email) {
            // Simulate API call to check if email exists in database
            // Return true if email exists (for login), false if not
            return new Promise((resolve) => {
                setTimeout(() => {
                    // For demo: emails ending with @test.com exist
                    resolve(email.endsWith('@test.com'));
                }, 500);
            });
        }

        async function sendOTP(email) {
            // Simulate API call to send OTP to email
            return new Promise((resolve) => {
                setTimeout(() => {
                    console.log(`OTP sent to ${email}`);
                    resolve({ success: true, message: 'OTP sent successfully' });
                }, 1000);
            });
        }

        async function verifyOTP(email, otp) {
            // Simulate API call to verify OTP
            // For demo: OTP "123456" is always correct
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({ success: otp === '123456', message: otp === '123456' ? 'OTP verified' : 'Invalid OTP' });
                }, 800);
            });
        }

        async function registerUser(name, email, password) {
            // Simulate API call to register new user
            return new Promise((resolve) => {
                setTimeout(() => {
                    console.log(`User registered: ${name}, ${email}`);
                    resolve({ success: true, message: 'User registered successfully' });
                }, 1000);
            });
        }

        async function loginUser(email, password) {
            // Simulate API call to login user
            return new Promise((resolve) => {
                setTimeout(() => {
                    // For demo: password "password123" is correct
                    resolve({ success: password === 'password123', message: 'Login successful' });
                }, 800);
            });
        }

        // Form switching functions
        function showForm(formName) {
            const loginForm = document.getElementById('loginForm');
            const signupForm = document.getElementById('signupForm');
            const otpEmailForm = document.getElementById('otpEmailForm');
            const otpVerifyForm = document.getElementById('otpVerifyForm');

            // Hide all forms
            loginForm.classList.remove('active');
            loginForm.classList.add('hidden');
            signupForm.classList.remove('active');
            otpEmailForm.classList.remove('active');
            otpVerifyForm.classList.remove('active');

            // Show requested form
            setTimeout(() => {
                switch(formName) {
                    case 'login':
                        loginForm.classList.remove('hidden');
                        loginForm.classList.add('active');
                        currentForm = 'login';
                        break;
                    case 'signup':
                        signupForm.classList.add('active');
                        currentForm = 'signup';
                        break;
                    case 'otp-email':
                        otpEmailForm.classList.add('active');
                        currentForm = 'otp-email';
                        break;
                    case 'otp-verify':
                        otpVerifyForm.classList.add('active');
                        currentForm = 'otp-verify';
                        startResendTimer();
                        break;
                }
            }, 300);
        }

        // Navigation event listeners
        document.getElementById('showSignup').addEventListener('click', (e) => {
            e.preventDefault();
            showForm('signup');
        });

        document.getElementById('backToLogin').addEventListener('click', () => {
            showForm('login');
        });

        document.getElementById('showLoginFromSignup').addEventListener('click', (e) => {
            e.preventDefault();
            showForm('login');
        });

        document.getElementById('backFromOTPEmail').addEventListener('click', () => {
            showForm('login');
        });

        // OTP Login buttons
        document.getElementById('otpLoginBtn').addEventListener('click', () => {
            showForm('otp-email');
        });

        document.getElementById('signupOtpLoginBtn').addEventListener('click', () => {
            showForm('otp-email');
        });

        document.getElementById('backToLoginFromOTP').addEventListener('click', (e) => {
            e.preventDefault();
            showForm('login');
        });

        document.getElementById('backFromOTPVerify').addEventListener('click', () => {
            showForm('otp-email');
            clearInterval(resendTimer);
        });

        // OTP Login initiation
        function initiateOTPLogin() {
            showForm('otp-email');
        }

        // Slideshow functionality
        const slides = document.querySelectorAll('.slide');
        const indicators = document.querySelectorAll('.indicator');
        const backgrounds = [
            'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            'linear-gradient(135deg, #0f3460 0%, #0d47a1 100%)',
            'linear-gradient(135deg, #2e1065 0%, #6a1b9a 100%)',
            'linear-gradient(135deg, #b71c1c 0%, #d32f2f 100%)'
        ];

        let currentSlide = 0;
        const leftPanel = document.querySelector('.login-left');

        function showSlide(index) {
            // Add stagger effect for smoother transition
            slides.forEach((slide, i) => {
                slide.classList.remove('active');
                // Add slight delay for non-active slides
                if (i !== index) {
                    setTimeout(() => {
                        slide.style.transform = 'translateY(30px) scale(0.95)';
                    }, 50);
                }
            });

            // Remove active from all indicators with stagger
            indicators.forEach((indicator, i) => {
                setTimeout(() => {
                    indicator.classList.remove('active');
                }, i * 50);
            });

            // Show current slide with delay for smooth transition
            setTimeout(() => {
                slides[index].classList.add('active');
                indicators[index].classList.add('active');

                // Smooth background transition
                leftPanel.style.transition = 'background 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
                leftPanel.style.background = backgrounds[index];
            }, 100);

            currentSlide = index;
        }

        function nextSlide() {
            const next = (currentSlide + 1) % slides.length;
            showSlide(next);
        }

        // Auto-advance slideshow with smoother timing
        let slideInterval = setInterval(nextSlide, 5000);

        // Pause on hover for better UX
        leftPanel.addEventListener('mouseenter', () => {
            clearInterval(slideInterval);
        });

        leftPanel.addEventListener('mouseleave', () => {
            slideInterval = setInterval(nextSlide, 5000);
        });

        // Manual slide navigation with smooth reset
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                // Reset auto-advance timer when manually navigating
                clearInterval(slideInterval);
                showSlide(index);
                slideInterval = setInterval(nextSlide, 5000);
            });
        });

        // Password toggle functionality
        const passwordToggles = [
            { toggle: 'passwordToggle', input: 'password' },
            { toggle: 'signupPasswordToggle', input: 'signupPassword' },
            { toggle: 'signupConfirmPasswordToggle', input: 'signupConfirmPassword' }
        ];

        passwordToggles.forEach(({ toggle, input }) => {
            const toggleBtn = document.getElementById(toggle);
            const passwordInput = document.getElementById(input);

            if (toggleBtn && passwordInput) {
                toggleBtn.addEventListener('click', function() {
                    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                    passwordInput.setAttribute('type', type);
                    this.textContent = type === 'password' ? '👁️' : '🙈';
                });
            }
        });

        // Form validation
        function validateEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        }

        function validatePassword(password) {
            return password.length >= 6;
        }

        function showError(inputId, message) {
            const errorElement = document.getElementById(inputId + 'Error');
            errorElement.textContent = message;
            errorElement.style.display = 'block';
            document.getElementById(inputId).style.borderColor = '#ff6b6b';
        }

        function hideError(inputId) {
            const errorElement = document.getElementById(inputId + 'Error');
            errorElement.style.display = 'none';
            document.getElementById(inputId).style.borderColor = '#3a3a4a';
        }

        function showSuccess(message) {
            const successElement = document.getElementById('successMessage');
            successElement.textContent = message;
            successElement.style.display = 'block';
        }

        // Real-time validation
        document.getElementById('email').addEventListener('input', function() {
            const email = this.value;
            if (email && !validateEmail(email)) {
                showError('email', 'Please enter a valid email address');
            } else {
                hideError('email');
            }
        });

        document.getElementById('password').addEventListener('input', function() {
            const password = this.value;
            if (password && !validatePassword(password)) {
                showError('password', 'Password must be at least 6 characters long');
            } else {
                hideError('password');
            }
        });

        // Form submission
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const rememberMe = document.getElementById('rememberMe').checked;

            let isValid = true;

            // Validate email
            if (!email) {
                showError('email', 'Email is required');
                isValid = false;
            } else if (!validateEmail(email)) {
                showError('email', 'Please enter a valid email address');
                isValid = false;
            } else {
                hideError('email');
            }

            // Validate password
            if (!password) {
                showError('password', 'Password is required');
                isValid = false;
            } else if (!validatePassword(password)) {
                showError('password', 'Password must be at least 6 characters long');
                isValid = false;
            } else {
                hideError('password');
            }

            if (isValid) {
                const loginBtn = this.querySelector('.login-btn');
                loginBtn.textContent = 'Signing In...';
                loginBtn.disabled = true;

                try {
                    const result = await loginUser(email, password);

                    if (result.success) {
                        showSuccess('Login successful! Redirecting to dashboard...');

                        const userData = {
                            email: email,
                            rememberMe: rememberMe,
                            loginTime: new Date().toISOString()
                        };

                        console.log('Login successful:', userData);

                        setTimeout(() => {
                            redirectToHomePage();
                        }, 2000);
                    } else {
                        showError('password', 'Invalid email or password');
                        loginBtn.textContent = 'Sign In';
                        loginBtn.disabled = false;
                    }
                } catch (error) {
                    showError('password', 'An error occurred. Please try again.');
                    loginBtn.textContent = 'Sign In';
                    loginBtn.disabled = false;
                }
            }
        });

        // Signup form submission
        document.getElementById('signupForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const name = document.getElementById('signupName').value;
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;
            const confirmPassword = document.getElementById('signupConfirmPassword').value;

            let isValid = true;

            // Validate name
            if (!name || name.trim().length < 2) {
                showError('signupName', 'Please enter your full name');
                isValid = false;
            } else {
                hideError('signupName');
            }

            // Validate email
            if (!email) {
                showError('signupEmail', 'Email is required');
                isValid = false;
            } else if (!validateEmail(email)) {
                showError('signupEmail', 'Please enter a valid email address');
                isValid = false;
            } else {
                hideError('signupEmail');
            }

            // Validate password
            if (!password) {
                showError('signupPassword', 'Password is required');
                isValid = false;
            } else if (password.length < 8) {
                showError('signupPassword', 'Password must be at least 8 characters long');
                isValid = false;
            } else {
                hideError('signupPassword');
            }

            // Validate confirm password
            if (!confirmPassword) {
                showError('signupConfirmPassword', 'Please confirm your password');
                isValid = false;
            } else if (password !== confirmPassword) {
                showError('signupConfirmPassword', 'Passwords do not match');
                isValid = false;
            } else {
                hideError('signupConfirmPassword');
            }

            if (isValid) {
                const signupBtn = this.querySelector('.login-btn');
                signupBtn.textContent = 'Creating Account...';
                signupBtn.disabled = true;

                try {
                    const result = await registerUser(name, email, password);

                    if (result.success) {
                        document.getElementById('signupSuccessMessage').style.display = 'block';

                        setTimeout(() => {
                            redirectToHomePage();
                        }, 2000);
                    } else {
                        showError('signupEmail', 'Email already exists or registration failed');
                        signupBtn.textContent = 'Create Account';
                        signupBtn.disabled = false;
                    }
                } catch (error) {
                    showError('signupEmail', 'An error occurred. Please try again.');
                    signupBtn.textContent = 'Create Account';
                    signupBtn.disabled = false;
                }
            }
        });

        // OTP Email form submission
        document.getElementById('otpEmailForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const email = document.getElementById('otpEmail').value;

            if (!email) {
                showError('otpEmail', 'Email is required');
                return;
            } else if (!validateEmail(email)) {
                showError('otpEmail', 'Please enter a valid email address');
                return;
            }

            const submitBtn = this.querySelector('.login-btn');
            submitBtn.textContent = 'Checking...';
            submitBtn.disabled = true;

            try {
                const emailExists = await checkEmailExists(email);

                if (emailExists) {
                    hideError('otpEmail');
                    otpUserEmail = email;

                    submitBtn.textContent = 'Sending OTP...';
                    const result = await sendOTP(email);

                    if (result.success) {
                        document.getElementById('otpSentMessage').textContent = `Enter the 6-digit code sent to ${email}`;
                        showForm('otp-verify');
                    }
                } else {
                    showError('otpEmail', 'Email not registered. Please sign up first.');
                }
            } catch (error) {
                showError('otpEmail', 'An error occurred. Please try again.');
            } finally {
                submitBtn.textContent = 'Send OTP';
                submitBtn.disabled = false;
            }
        });

        // OTP input handling
        const otpInputs = document.querySelectorAll('.otp-input');

        otpInputs.forEach((input, index) => {
            input.addEventListener('input', function(e) {
                const value = e.target.value;

                if (value.length === 1 && index < otpInputs.length - 1) {
                    otpInputs[index + 1].focus();
                }

                hideError('otpVerify');
            });

            input.addEventListener('keydown', function(e) {
                if (e.key === 'Backspace' && !e.target.value && index > 0) {
                    otpInputs[index - 1].focus();
                }
            });

            input.addEventListener('paste', function(e) {
                e.preventDefault();
                const pastedData = e.clipboardData.getData('text').slice(0, 6);

                pastedData.split('').forEach((char, i) => {
                    if (otpInputs[i]) {
                        otpInputs[i].value = char;
                    }
                });

                if (otpInputs[5]) {
                    otpInputs[5].focus();
                }
            });
        });

        // OTP Verify form submission
        document.getElementById('otpVerifyForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const otpValues = Array.from(otpInputs).map(input => input.value);
            const otp = otpValues.join('');

            if (otp.length !== 6) {
                showError('otpVerify', 'Please enter complete 6-digit OTP');
                return;
            }

            const submitBtn = this.querySelector('.login-btn');
            submitBtn.textContent = 'Verifying...';
            submitBtn.disabled = true;

            try {
                const result = await verifyOTP(otpUserEmail, otp);

                if (result.success) {
                    hideError('otpVerify');
                    submitBtn.textContent = 'Success!';

                    setTimeout(() => {
                        redirectToHomePage();
                    }, 1000);
                } else {
                    showError('otpVerify', 'Invalid OTP. Please try again.');
                    otpInputs.forEach(input => input.value = '');
                    otpInputs[0].focus();
                }
            } catch (error) {
                showError('otpVerify', 'An error occurred. Please try again.');
            } finally {
                if (!result || !result.success) {
                    submitBtn.textContent = 'Verify & Login';
                    submitBtn.disabled = false;
                }
            }
        });

        // Resend OTP functionality
        function startResendTimer() {
            resendCountdown = 30;
            const resendBtn = document.getElementById('resendOTPBtn');
            const timerDiv = document.getElementById('resendTimer');

            resendBtn.disabled = true;

            resendTimer = setInterval(() => {
                resendCountdown--;
                timerDiv.textContent = `Resend available in ${resendCountdown}s`;

                if (resendCountdown <= 0) {
                    clearInterval(resendTimer);
                    resendBtn.disabled = false;
                    timerDiv.textContent = '';
                }
            }, 1000);
        }

        document.getElementById('resendOTPBtn').addEventListener('click', async function() {
            this.disabled = true;
            this.textContent = 'Sending...';

            try {
                const result = await sendOTP(otpUserEmail);

                if (result.success) {
                    this.textContent = 'Resend OTP';
                    startResendTimer();

                    // Show temporary success message
                    const timer = document.getElementById('resendTimer');
                    timer.textContent = 'OTP sent successfully!';
                    timer.style.color = '#51cf66';

                    setTimeout(() => {
                        timer.style.color = '#808080';
                    }, 3000);
                }
            } catch (error) {
                this.textContent = 'Resend OTP';
                this.disabled = false;
            }
        });

        // Redirect to home page
        function redirectToHomePage() {
            // Create and show home page
            document.body.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%); color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                    <div style="text-align: center; padding: 40px;">
                        <h1 style="font-size: 3rem; margin-bottom: 20px;">📊 Welcome to TradeSnap</h1>
                        <p style="font-size: 1.2rem; color: #b0b0b0; margin-bottom: 40px;">Your trading dashboard will be here</p>
                        <div style="display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin: 10px;">
                            Logged in successfully! ✓
                        </div>
                    </div>
                </div>
            `;
        }

        // Social login function
        function socialLogin(provider) {
            if (provider === 'google') {
                console.log('Initiating Google login...');
                // Here you would integrate with Google OAuth
                // Example: window.location.href = 'https://accounts.google.com/oauth/authorize?...'
                alert('Google OAuth integration would be implemented here');
            }
        }

        // Add smooth animations on page load
        window.addEventListener('load', function() {
            const loginContainer = document.querySelector('.login-container');
            loginContainer.style.opacity = '0';
            loginContainer.style.transform = 'translateY(50px)';

            setTimeout(() => {
                loginContainer.style.transition = 'all 0.8s ease';
                loginContainer.style.opacity = '1';
                loginContainer.style.transform = 'translateY(0)';
            }, 100);
        });

        // Add focus effects
        const inputs = document.querySelectorAll('.form-input');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });

            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
            });
        });