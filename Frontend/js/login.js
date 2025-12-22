let currentForm = 'login';
        let otpUserEmail = '';
        let resendTimer = null;
        let resendCountdown = 30;

        // Backend simulation functions
        async function checkEmailExists(email) {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve(email.endsWith('@test.com'));
                }, 500);
            });
        }

        async function sendOTP(email) {
            return new Promise((resolve) => {
                setTimeout(() => {
                    console.log(`OTP sent to ${email}`);
                    resolve({ success: true, message: 'OTP sent successfully' });
                }, 1000);
            });
        }

        async function verifyOTP(email, otp) {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({ success: otp === '123456', message: otp === '123456' ? 'OTP verified' : 'Invalid OTP' });
                }, 800);
            });
        }

        async function registerUser(name, email, password) {
            // const mail = document.getElementById("signupEmail").value;
            // const pass = document.getElementById("signupPassword").value;
            const username = document.getElementById("signupName").value;
            const res = await fetch('http://localhost:8000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password
                })
            })

            const data = await res.json();
            // console.log(data.detail);

            // if (!res.ok) {
            //     showError('signupEmail', data.detail);
            //     throw new Error(data.detail || 'Login failed');
            // }
            // if(JSON.parse(data.detail)){
            //     console.log("shabash");
            // }

            return data;
        }

        async function loginUser(email, password) {
            const res = await fetch('http://localhost:8000/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                email: email,
                password: password
                })
            })
            const data = await res.json();

            // if (!res.ok) {
            //     throw new Error(data.detail.content || 'Login failed');
            // }

            return data;

        }

        // Form switching
        function showForm(formName) {
            const forms = ['loginForm', 'signupForm', 'otpEmailForm', 'otpVerifyForm'];

            forms.forEach(form => {
                const formElement = document.getElementById(form);
                if (formElement) {
                    formElement.classList.add('hidden');
                }
            });

            setTimeout(() => {
                const targetForm = document.getElementById(formName);
                if (targetForm) {
                    targetForm.classList.remove('hidden');
                    currentForm = formName;

                    if (formName === 'otpVerifyForm') {
                        startResendTimer();
                    }
                }
            }, 300);
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
        const leftPanel = document.getElementById('leftPanel');

        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.remove('active');
            });

            indicators.forEach((indicator, i) => {
                indicator.classList.remove('active');
            });

            setTimeout(() => {
                slides[index].classList.add('active');
                indicators[index].classList.add('active');
                leftPanel.style.background = backgrounds[index];
            }, 100);

            currentSlide = index;
        }

        function nextSlide() {
            const next = (currentSlide + 1) % slides.length;
            showSlide(next);
        }

        let slideInterval = setInterval(nextSlide, 5000);

        leftPanel.addEventListener('mouseenter', () => {
            clearInterval(slideInterval);
        });

        leftPanel.addEventListener('mouseleave', () => {
            slideInterval = setInterval(nextSlide, 5000);
        });

        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                clearInterval(slideInterval);
                showSlide(index);
                slideInterval = setInterval(nextSlide, 5000);
            });
        });

        // Password toggle functionality
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('password-toggle')) {
                const targetId = e.target.getAttribute('data-target');
                const passwordInput = document.getElementById(targetId);

                if (passwordInput) {
                    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                    passwordInput.setAttribute('type', type);
                    e.target.textContent = type === 'password' ? '👁️' : '🙈';
                }
            }
        });

        // Validation functions
        function validateEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        }

        function validatePassword(password) {
            return password.length >= 6;
        }

        function showError(inputId, message) {
            const errorElement = document.getElementById(inputId + 'Error');
            if (errorElement) {
                errorElement.textContent = message;
                errorElement.style.display = 'block';
                const input = document.getElementById(inputId);
                if (input) {
                    input.style.borderColor = '#ff6b6b';
                }
            }
        }

        function hideError(inputId) {
            const errorElement = document.getElementById(inputId + 'Error');
            if (errorElement) {
                errorElement.style.display = 'none';
                const input = document.getElementById(inputId);
                if (input) {
                    input.style.borderColor = '#3a3a4a';
                }
            }
        }

        function showSuccess(elementId, message) {
            const successElement = document.getElementById(elementId);
            if (successElement) {
                successElement.textContent = message;
                successElement.style.display = 'block';
            }
        }

        // Navigation
        document.getElementById('showSignupBtn').addEventListener('click', (e) => {
            e.preventDefault();
            showForm('signupForm');
        });

        document.getElementById('backToLoginBtn').addEventListener('click', () => {
            showForm('loginForm');
        });

        document.getElementById('showLoginBtn').addEventListener('click', (e) => {
            e.preventDefault();
            showForm('loginForm');
        });

        document.getElementById('otpLoginBtn').addEventListener('click', () => {
            showForm('otpEmailForm');
        });

        document.getElementById('otpSignupBtn').addEventListener('click', () => {
            showForm('otpEmailForm');
        });

        // document.getElementById('googleLoginBtn').addEventListener('click', () => {
        //     console.log('Initiating Google login...');
        //     alert('Google OAuth integration would be implemented here.\n\nIn production, this would:\n1. Open Google login popup\n2. Handle OAuth authentication\n3. Redirect to dashboard on success');
        // });

        // document.getElementById('googleSignupBtn').addEventListener('click', () => {
        //     console.log('Initiating Google signup...');
        //     alert('Google OAuth integration would be implemented here.\n\nIn production, this would:\n1. Open Google login popup\n2. Handle OAuth authentication\n3. Create account and redirect to dashboard');
        // });

        document.getElementById('backFromOTPEmailBtn').addEventListener('click', () => {
            showForm('loginForm');
        });

        document.getElementById('backToLoginFromOTPBtn').addEventListener('click', (e) => {
            e.preventDefault();
            showForm('loginForm');
        });

        document.getElementById('backFromOTPVerifyBtn').addEventListener('click', () => {
            showForm('otpEmailForm');
            if (resendTimer) clearInterval(resendTimer);
        });

        // Login form submission
        document.getElementById('loginFormElement').addEventListener('submit', async function(e) {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            let isValid = true;

            if (!email) {
                showError('email', 'Please enter a valid email address');
                isValid = false;
            } else {
                hideError('email');
            }

            if (!password || !validatePassword(password)) {
                showError('password', 'Password must be at least 6 characters long');
                isValid = false;
            } else {
                hideError('password');
            }

            if (isValid) {
                // const loginBtn = this.querySelector('.login-btn');
                // loginBtn.textContent = 'Signing In...';
                // loginBtn.disabled = true;
                //
                // try {
                //     const result = await loginUser(email, password);
                //
                //     if ("access_token" in result) {
                //         showSuccess('successMessage', 'Login successful! Redirecting...');
                //         setTimeout(() => redirectToHomePage(), 2000);
                //     } else {
                //         if(result.detail.type === "user") {
                //             showError('email', result.detail.content);
                //         }
                //         else{
                //             showError('password', result.detail.content);
                //         }
                //         loginBtn.textContent = 'Sign In';
                //         loginBtn.disabled = false;
                //     }
                // } catch (error) {
                //     showError('password', 'An error occurred');
                //     loginBtn.textContent = 'Sign In';
                //     loginBtn.disabled = false;
                // }
                // DO NOT rely on `this` unless this function is bound to a form element
                const loginBtn = document.querySelector('.login-btn');
                loginBtn.textContent = 'Signing In...';
                loginBtn.disabled = true;

                try {
                    const result = await loginUser(email, password);

                    // ---- SUCCESS ----
                    if ("access_token" in result) {
                        showSuccess('successMessage', 'Login successful! Redirecting...');
                        setTimeout(() => redirectToHomePage(), 2000);
                        return;
                    }

                    // ---- ERROR FROM BACKEND ----
                    if (result.detail?.type === "user") {
                        showError('email', result.detail.content);
                    } else if (result.detail?.type === "password") {
                        showError('password', result.detail.content);
                    } else {
                        showError('email', 'Login failed');
                    }

                    loginBtn.textContent = 'Sign In';
                    loginBtn.disabled = false;

                } catch (error) {
                    console.error(error);
                    showError('password', 'An error occurred');
                    loginBtn.textContent = 'Sign In';
                    loginBtn.disabled = false;
                }

            }
        });

        // Signup form submission
        document.getElementById('signupFormElement').addEventListener('submit', async function(e) {
            e.preventDefault();

            const name = document.getElementById('signupName').value;
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;
            const confirmPassword = document.getElementById('signupConfirmPassword').value;

            let isValid = true;

            if (!name || name.trim().length < 2) {
                showError('signupName', 'Please enter your full name');
                isValid = false;
            } else {
                hideError('signupName');
            }

            if (!email || !validateEmail(email)) {
                showError('signupEmail', 'Please enter a valid email address');
                isValid = false;
            } else {
                hideError('signupEmail');
            }

            if (!password || password.length < 8) {
                showError('signupPassword', 'Password must be at least 8 characters long');
                isValid = false;
            } else {
                hideError('signupPassword');
            }

            if (password !== confirmPassword) {
                showError('signupConfirmPassword', 'Passwords do not match');
                isValid = false;
            } else {
                hideError('signupConfirmPassword');
            }

            if (isValid) {
                const signupBtn = this.querySelector('.login-btn');
                signupBtn.textContent = 'Creating Account...';
                signupBtn.disabled = true;
                const result = await registerUser(name, email, password);
                try {
                    if (result.username) {
                        showSuccess('signupSuccessMessage', 'Account created! Redirecting...');
                        setTimeout(() => redirectToHomePage(), 2000);
                    } else {
                        showError('signupEmail', 'Registration failed');
                        signupBtn.textContent = 'Create Account';
                        signupBtn.disabled = false;
                    }
                } catch (error) {
                    showError('signupEmail', result.detail);
                    signupBtn.textContent = 'Create Account';
                    signupBtn.disabled = false;
                }
            }
        });

        // OTP Email form submission
        document.getElementById('otpEmailFormElement').addEventListener('submit', async function(e) {
            e.preventDefault();

            const email = document.getElementById('otpEmail').value;

            if (!email || !validateEmail(email)) {
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
                    await sendOTP(email);

                    document.getElementById('otpSentMessage').textContent = `Enter the 6-digit code sent to ${email}`;
                    showForm('otpVerifyForm');
                } else {
                    showError('otpEmail', 'Email not registered. Please sign up first.');
                }
            } catch (error) {
                showError('otpEmail', 'An error occurred');
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
        document.getElementById('otpVerifyFormElement').addEventListener('submit', async function(e) {
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

                    setTimeout(() => redirectToHomePage(), 1000);
                } else {
                    showError('otpVerify', 'Invalid OTP. Please try again.');
                    otpInputs.forEach(input => input.value = '');
                    otpInputs[0].focus();
                    submitBtn.textContent = 'Verify & Login';
                    submitBtn.disabled = false;
                }
            } catch (error) {
                showError('otpVerify', 'An error occurred');
                submitBtn.textContent = 'Verify & Login';
                submitBtn.disabled = false;
            }
        });

        // Resend OTP functionality
        function startResendTimer() {
            resendCountdown = 30;
            const resendBtn = document.getElementById('resendOTPBtn');
            const timerDiv = document.getElementById('resendTimer');

            if (!resendBtn || !timerDiv) return;

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
                await sendOTP(otpUserEmail);

                this.textContent = 'Resend OTP';
                startResendTimer();

                const timer = document.getElementById('resendTimer');
                timer.textContent = 'OTP sent successfully!';
                timer.style.color = '#51cf66';

                setTimeout(() => {
                    timer.style.color = '#808080';
                }, 3000);
            } catch (error) {
                this.textContent = 'Resend OTP';
                this.disabled = false;
            }
        });

        // Redirect to home page
        function redirectToHomePage() {
            window.location.replace("./home.html")
        }

        // Page load animation
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








         function decodeJWT(token) {

        let base64Url = token.split(".")[1];
        let base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
        let jsonPayload = decodeURIComponent(
          atob(base64)
            .split("")
            .map(function (c) {
              return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
            })
            .join("")
        );
        return JSON.parse(jsonPayload);
      }

        async function handleCredentialResponse(response) {
    const responsePayload = decodeJWT(response.credential);

    try {
        // ---------------- LOGIN ----------------
        if (currentForm === 'login') {
            const loginBtn = document.querySelector('#loginForm .login-btn');
            loginBtn.textContent = 'Signing In...';
            loginBtn.disabled = true;

            const res = await fetch('http://localhost:8000/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: responsePayload.email,
                    sub: String(responsePayload.sub)
                })
            });

            const data = await res.json();

            // ---- ERROR ----
            if (!res.ok) {
                if (data.detail?.type === "user") {
                    showError('email', data.detail.content);
                } else if (data.detail?.type === "password") {
                    showError('password', data.detail.content);
                } else {
                    showError('email', 'Login failed');
                }

                loginBtn.textContent = 'Sign In';
                loginBtn.disabled = false;
                return;
            }

            // ---- SUCCESS ----
            if ("access_token" in data) {
                showSuccess('successMessage', 'Login successful! Redirecting...');
                setTimeout(() => redirectToHomePage(), 2000);
                return;
            }

            // Fallback (should never happen)
            showError('email', 'Unexpected response');
            loginBtn.textContent = 'Sign In';
            loginBtn.disabled = false;
        }

        // ---------------- SIGNUP ----------------
        else if (currentForm === 'signupForm') {
            const signupBtn = document.querySelector('#signupForm .login-btn');
            signupBtn.textContent = 'Creating Account...';
            signupBtn.disabled = true;

            const res = await fetch('http://localhost:8000/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: responsePayload.name,
                    email: responsePayload.email,
                    sub: String(responsePayload.sub),
                })
            });

            const data = await res.json();

            // ---- ERROR ----
            if (!res.ok) {
                showError('signupEmail', data.detail?.content || 'Registration failed');
                signupBtn.textContent = 'Create Account';
                signupBtn.disabled = false;
                return;
            }

            // ---- SUCCESS ----
            showSuccess('signupSuccessMessage', 'Account created! Redirecting...');
            setTimeout(() => redirectToHomePage(), 2000);
        }

    } catch (err) {
        console.error(err);
        showError('email', 'Something went wrong. Please try again.');
    }
}




      // }
      //   console.log("Decoded JWT ID token fields:");
      //   console.log("  Full Name: " + responsePayload.name);
      //   console.log("  Given Name: " + responsePayload.given_name);
      //   console.log("  Family Name: " + responsePayload.family_name);
      //   console.log("  Unique ID: " + responsePayload.sub);
      //   console.log("  Profile image URL: " + responsePayload.picture);
      //   console.log("  Email: " + responsePayload.email);
      // }