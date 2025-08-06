/**
 * Authentication Module - handles login, registration, and Google OAuth
 */

class AuthManager {
    constructor() {
        this.config = {
            googleClientId: null,
            redirectUri: window.location.origin + '/accounts/google/login/callback/'
        };
        this.init();
    }

    init() {
        this.initGoogleSignIn();
        this.bindFormEvents();
        this.setupPasswordToggle();
        this.setupFormValidation();
    }

    async initGoogleSignIn() {
        // Initialize Google Sign-In if available
        if (typeof google !== 'undefined' && google.accounts) {
            try {
                const clientId = document.querySelector('meta[name="google-signin-client_id"]')?.content;
                if (clientId) {
                    this.config.googleClientId = clientId;
                    this.setupGoogleOneTap();
                    this.setupGoogleSignInButton();
                }
            } catch (error) {
                console.error('Google Sign-In initialization failed:', error);
            }
        }
    }

    setupGoogleOneTap() {
        if (!this.config.googleClientId) return;

        google.accounts.id.initialize({
            client_id: this.config.googleClientId,
            callback: (response) => this.handleGoogleResponse(response),
            auto_select: false,
            cancel_on_tap_outside: true
        });

        // Show One Tap on login page only
        if (document.querySelector('.login-form')) {
            google.accounts.id.prompt((notification) => {
                if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
                    console.log('Google One Tap not displayed:', notification.getNotDisplayedReason());
                }
            });
        }
    }

    setupGoogleSignInButton() {
        const googleBtn = document.getElementById('google-signin-btn');
        if (googleBtn && this.config.googleClientId) {
            google.accounts.id.renderButton(googleBtn, {
                theme: 'outline',
                size: 'large',
                text: 'signin_with',
                shape: 'rectangular',
                locale: 'ar'
            });
        }
    }

    async handleGoogleResponse(response) {
        try {
            // Show loading state
            this.showLoadingState('جاري تسجيل الدخول...');

            // Send credential to Django backend
            const formData = new FormData();
            formData.append('credential', response.credential);
            formData.append('csrfmiddlewaretoken', this.getCSRFToken());

            const result = await fetch('/accounts/google/login/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (result.ok) {
                const data = await result.json();
                if (data.success) {
                    window.NotificationManager?.success('تم تسجيل الدخول بنجاح');
                    window.location.href = data.redirect_url || '/';
                } else {
                    throw new Error(data.error || 'فشل في تسجيل الدخول');
                }
            } else {
                throw new Error('فشل في الاتصال بالخادم');
            }

        } catch (error) {
            console.error('Google Sign-In error:', error);
            window.NotificationManager?.error('حدث خطأ أثناء تسجيل الدخول: ' + error.message);
        } finally {
            this.hideLoadingState();
        }
    }

    bindFormEvents() {
        // Login form
        const loginForm = document.querySelector('.login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Registration form
        const registerForm = document.querySelector('.register-form');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // Password reset form
        const resetForm = document.querySelector('.password-reset-form');
        if (resetForm) {
            resetForm.addEventListener('submit', (e) => this.handlePasswordReset(e));
        }
    }

    setupPasswordToggle() {
        const toggleButtons = document.querySelectorAll('.password-toggle');
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const input = button.previousElementSibling;
                const icon = button.querySelector('i');
                
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        });
    }

    setupFormValidation() {
        // Real-time validation for email fields
        const emailInputs = document.querySelectorAll('input[type="email"]');
        emailInputs.forEach(input => {
            input.addEventListener('blur', () => this.validateEmail(input));
            input.addEventListener('input', () => this.clearValidationError(input));
        });

        // Real-time validation for password fields
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            if (input.name === 'password1' || input.name === 'password') {
                input.addEventListener('input', () => this.validatePassword(input));
            }
        });

        // Password confirmation validation
        const confirmPasswordInput = document.querySelector('input[name="password2"]');
        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('blur', () => this.validatePasswordConfirmation());
        }
    }

    validateEmail(input) {
        const email = input.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
            this.showFieldError(input, 'يرجى إدخال عنوان بريد إلكتروني صحيح');
            return false;
        }
        
        this.clearFieldError(input);
        return true;
    }

    validatePassword(input) {
        const password = input.value;
        const minLength = 8;
        const errors = [];

        if (password.length < minLength) {
            errors.push(`كلمة المرور يجب أن تكون ${minLength} أحرف على الأقل`);
        }

        if (!/(?=.*[a-z])/.test(password)) {
            errors.push('يجب أن تحتوي على حرف صغير واحد على الأقل');
        }

        if (!/(?=.*[A-Z])/.test(password)) {
            errors.push('يجب أن تحتوي على حرف كبير واحد على الأقل');
        }

        if (!/(?=.*\d)/.test(password)) {
            errors.push('يجب أن تحتوي على رقم واحد على الأقل');
        }

        if (errors.length > 0) {
            this.showFieldError(input, errors.join('<br>'));
            return false;
        }

        this.clearFieldError(input);
        return true;
    }

    validatePasswordConfirmation() {
        const password1 = document.querySelector('input[name="password1"]')?.value;
        const password2 = document.querySelector('input[name="password2"]')?.value;
        const confirmInput = document.querySelector('input[name="password2"]');

        if (password1 && password2 && password1 !== password2) {
            this.showFieldError(confirmInput, 'كلمات المرور غير متطابقة');
            return false;
        }

        this.clearFieldError(confirmInput);
        return true;
    }

    showFieldError(input, message) {
        input.classList.add('is-invalid');
        
        let errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            input.parentNode.appendChild(errorDiv);
        }
        
        errorDiv.innerHTML = message;
    }

    clearFieldError(input) {
        input.classList.remove('is-invalid');
        const errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    clearValidationError(input) {
        if (input.classList.contains('is-invalid')) {
            this.clearFieldError(input);
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        try {
            this.setButtonLoading(submitBtn, 'جاري تسجيل الدخول...');
            
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                window.NotificationManager?.success('تم تسجيل الدخول بنجاح');
                window.location.href = data.redirect_url || '/';
            } else {
                this.handleFormErrors(form, data.errors);
            }

        } catch (error) {
            console.error('Login error:', error);
            window.NotificationManager?.error('حدث خطأ أثناء تسجيل الدخول');
        } finally {
            this.resetButton(submitBtn, 'تسجيل الدخول');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        
        if (!this.validatePasswordConfirmation()) return;
        
        const form = e.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        try {
            this.setButtonLoading(submitBtn, 'جاري إنشاء الحساب...');
            
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                window.NotificationManager?.success('تم إنشاء الحساب بنجاح. يرجى التحقق من بريدك الإلكتروني');
                form.reset();
            } else {
                this.handleFormErrors(form, data.errors);
            }

        } catch (error) {
            console.error('Registration error:', error);
            window.NotificationManager?.error('حدث خطأ أثناء إنشاء الحساب');
        } finally {
            this.resetButton(submitBtn, 'إنشاء حساب');
        }
    }

    handleFormErrors(form, errors) {
        // Clear previous errors
        form.querySelectorAll('.is-invalid').forEach(input => {
            this.clearFieldError(input);
        });

        // Show new errors
        Object.keys(errors).forEach(fieldName => {
            const input = form.querySelector(`[name="${fieldName}"]`);
            if (input) {
                this.showFieldError(input, errors[fieldName].join('<br>'));
            }
        });

        // Show general errors
        if (errors.__all__) {
            window.NotificationManager?.error(errors.__all__.join('<br>'));
        }
    }

    setButtonLoading(button, text) {
        if (!button) return;
        
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${text}`;
        button.disabled = true;
    }

    resetButton(button, text) {
        if (!button) return;
        
        button.innerHTML = button.dataset.originalText || text;
        button.disabled = false;
    }

    showLoadingState(message) {
        // You can implement a global loading overlay here
        console.log('Loading:', message);
    }

    hideLoadingState() {
        // Hide global loading overlay
        console.log('Loading complete');
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name=csrf-token]')?.content || '';
    }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
    window.AuthManager = new AuthManager();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthManager;
}
