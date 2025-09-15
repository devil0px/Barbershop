/**
 * Forms Module - handles form validation, submission, and UI interactions
 */

class FormsManager {
    constructor() {
        this.config = {
            validationDelay: 300,
            submitDelay: 1000
        };
        this.timers = new Map();
        this.init();
    }

    init() {
        this.bindFormEvents();
        this.setupRealTimeValidation();
        this.initializeRatingStars();
        this.setupFileUploads();
        this.initializeSelectCards();
    }

    bindFormEvents() {
        // Handle all form submissions
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.tagName === 'FORM' && !form.dataset.skipValidation) {
                this.handleFormSubmit(e);
            }
        });

        // Handle form resets
        document.addEventListener('reset', (e) => {
            setTimeout(() => this.clearFormValidation(e.target), 10);
        });
    }

    setupRealTimeValidation() {
        // Email validation
        document.addEventListener('input', (e) => {
            if (e.target.type === 'email') {
                this.debounceValidation(e.target, () => this.validateEmail(e.target));
            }
        });

        // Phone validation
        document.addEventListener('input', (e) => {
            if (e.target.type === 'tel') {
                this.debounceValidation(e.target, () => this.validatePhone(e.target));
            }
        });

        // Required field validation
        document.addEventListener('blur', (e) => {
            if (e.target.hasAttribute('required')) {
                this.validateRequired(e.target);
            }
        });

        // Clear validation on focus
        document.addEventListener('focus', (e) => {
            if (e.target.classList.contains('is-invalid')) {
                this.clearFieldValidation(e.target);
            }
        });
    }

    initializeRatingStars() {
        const ratingContainers = document.querySelectorAll('.rating-stars');
        
        ratingContainers.forEach(container => {
            const stars = container.querySelectorAll('.star');
            const input = container.querySelector('input[type="hidden"]');
            
            stars.forEach((star, index) => {
                star.addEventListener('click', () => {
                    const rating = index + 1;
                    this.setRating(container, rating);
                    if (input) input.value = rating;
                });

                star.addEventListener('mouseenter', () => {
                    this.highlightStars(container, index + 1);
                });
            });

            container.addEventListener('mouseleave', () => {
                const currentRating = input ? parseInt(input.value) || 0 : 0;
                this.highlightStars(container, currentRating);
            });
        });
    }

    setRating(container, rating) {
        const stars = container.querySelectorAll('.star');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
                star.innerHTML = '<i class="fas fa-star"></i>';
            } else {
                star.classList.remove('active');
                star.innerHTML = '<i class="far fa-star"></i>';
            }
        });
    }

    highlightStars(container, rating) {
        const stars = container.querySelectorAll('.star');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('hover');
            } else {
                star.classList.remove('hover');
            }
        });
    }

    setupFileUploads() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        
        fileInputs.forEach(input => {
            // Create custom file upload UI
            this.createFileUploadUI(input);
            
            input.addEventListener('change', (e) => {
                this.handleFileSelection(e.target);
            });
        });
    }

    createFileUploadUI(input) {
        const wrapper = document.createElement('div');
        wrapper.className = 'custom-file-upload';
        
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-outline-primary';
        button.innerHTML = '<i class="fas fa-upload me-2"></i>اختر ملف';
        
        const preview = document.createElement('div');
        preview.className = 'file-preview mt-2';
        
        wrapper.appendChild(button);
        wrapper.appendChild(preview);
        
        input.parentNode.insertBefore(wrapper, input);
        input.style.display = 'none';
        
        button.addEventListener('click', () => input.click());
    }

    handleFileSelection(input) {
        const wrapper = input.parentNode.querySelector('.custom-file-upload');
        const preview = wrapper.querySelector('.file-preview');
        const button = wrapper.querySelector('button');
        
        if (input.files.length > 0) {
            const file = input.files[0];
            
            // Validate file
            if (!this.validateFile(file, input)) return;
            
            // Update button text
            button.innerHTML = `<i class="fas fa-check me-2"></i>${file.name}`;
            button.classList.remove('btn-outline-primary');
            button.classList.add('btn-success');
            
            // Show preview for images
            if (file.type.startsWith('image/')) {
                this.showImagePreview(file, preview);
            } else {
                preview.innerHTML = `<small class="text-muted">تم اختيار: ${file.name}</small>`;
            }
        } else {
            // Reset UI
            button.innerHTML = '<i class="fas fa-upload me-2"></i>اختر ملف';
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-primary');
            preview.innerHTML = '';
        }
    }

    validateFile(file, input) {
        const maxSize = parseInt(input.dataset.maxSize) || 5 * 1024 * 1024; // 5MB default
        const allowedTypes = input.accept ? input.accept.split(',').map(t => t.trim()) : [];
        
        // Check file size
        if (file.size > maxSize) {
            this.showFieldError(input, `حجم الملف كبير جداً. الحد الأقصى ${this.formatFileSize(maxSize)}`);
            return false;
        }
        
        // Check file type
        if (allowedTypes.length > 0 && !allowedTypes.some(type => {
            if (type.startsWith('.')) {
                return file.name.toLowerCase().endsWith(type.toLowerCase());
            } else {
                return file.type.match(type.replace('*', '.*'));
            }
        })) {
            this.showFieldError(input, 'نوع الملف غير مدعوم');
            return false;
        }
        
        this.clearFieldValidation(input);
        return true;
    }

    showImagePreview(file, container) {
        const reader = new FileReader();
        reader.onload = (e) => {
            container.innerHTML = `
                <img src="${e.target.result}" alt="معاينة" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
            `;
        };
        reader.readAsDataURL(file);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 بايت';
        const k = 1024;
        const sizes = ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    initializeSelectCards() {
        const cardContainers = document.querySelectorAll('[data-select-cards]');
        
        cardContainers.forEach(container => {
            const cards = container.querySelectorAll('.selection-card');
            const input = container.querySelector('input[type="hidden"]');
            const isMultiple = container.dataset.multiple === 'true';
            
            cards.forEach(card => {
                card.addEventListener('click', () => {
                    if (isMultiple) {
                        this.toggleCardSelection(card, input);
                    } else {
                        this.selectSingleCard(container, card, input);
                    }
                });
            });
        });
    }

    selectSingleCard(container, selectedCard, input) {
        // Remove active class from all cards
        container.querySelectorAll('.selection-card').forEach(card => {
            card.classList.remove('active');
        });
        
        // Add active class to selected card
        selectedCard.classList.add('active');
        
        // Update input value
        if (input) {
            input.value = selectedCard.dataset.value;
        }
        
        // Trigger change event
        if (input) {
            input.dispatchEvent(new Event('change'));
        }
    }

    toggleCardSelection(card, input) {
        card.classList.toggle('active');
        
        if (input) {
            const selectedValues = Array.from(
                card.parentNode.querySelectorAll('.selection-card.active')
            ).map(c => c.dataset.value);
            
            input.value = selectedValues.join(',');
            input.dispatchEvent(new Event('change'));
        }
    }

    async handleFormSubmit(e) {
        const form = e.target;
        
        // Skip if already submitting
        if (form.dataset.submitting === 'true') {
            e.preventDefault();
            return;
        }
        
        // Validate form
        if (!this.validateForm(form)) {
            e.preventDefault();
            return;
        }
        
        // Handle AJAX forms
        if (form.dataset.ajax === 'true') {
            e.preventDefault();
            await this.submitFormAjax(form);
            return;
        }
        
        // Show loading state for regular forms
        this.setFormSubmitting(form, true);
    }

    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!this.validateRequired(field)) {
                isValid = false;
            }
        });
        
        // Custom validation rules
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value && !this.validateEmail(field)) {
                isValid = false;
            }
        });
        
        const phoneFields = form.querySelectorAll('input[type="tel"]');
        phoneFields.forEach(field => {
            if (field.value && !this.validatePhone(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    async submitFormAjax(form) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        try {
            this.setFormSubmitting(form, true);
            this.setButtonLoading(submitBtn);
            
            const response = await fetch(form.action || window.location.href, {
                method: form.method || 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.handleFormSuccess(form, data);
            } else {
                this.handleFormErrors(form, data.errors || {});
            }
            
        } catch (error) {
            console.error('Form submission error:', error);
            window.NotificationManager?.error('حدث خطأ أثناء إرسال النموذج');
        } finally {
            this.setFormSubmitting(form, false);
            this.resetButton(submitBtn);
        }
    }

    handleFormSuccess(form, data) {
        window.NotificationManager?.success(data.message || 'تم الإرسال بنجاح');
        
        if (data.redirect) {
            setTimeout(() => {
                window.location.href = data.redirect;
            }, 1000);
        } else if (data.reset !== false) {
            form.reset();
            this.clearFormValidation(form);
        }
    }

    handleFormErrors(form, errors) {
        // Clear previous errors
        this.clearFormValidation(form);
        
        // Show field errors
        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                this.showFieldError(field, errors[fieldName].join('<br>'));
            }
        });
        
        // Show general errors
        if (errors.__all__) {
            window.NotificationManager?.error(errors.__all__.join('<br>'));
        }
    }

    validateRequired(field) {
        const value = field.type === 'checkbox' ? field.checked : field.value.trim();
        
        if (!value) {
            this.showFieldError(field, 'هذا الحقل مطلوب');
            return false;
        }
        
        this.clearFieldValidation(field);
        return true;
    }

    validateEmail(field) {
        const email = field.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
            this.showFieldError(field, 'يرجى إدخال عنوان بريد إلكتروني صحيح');
            return false;
        }
        
        this.clearFieldValidation(field);
        return true;
    }

    validatePhone(field) {
        const phone = field.value.trim();
        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
        
        if (phone && !phoneRegex.test(phone)) {
            this.showFieldError(field, 'يرجى إدخال رقم هاتف صحيح');
            return false;
        }
        
        this.clearFieldValidation(field);
        return true;
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        let errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            field.parentNode.appendChild(errorDiv);
        }
        
        errorDiv.innerHTML = message;
    }

    clearFieldValidation(field) {
        field.classList.remove('is-invalid', 'is-valid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    clearFormValidation(form) {
        form.querySelectorAll('.is-invalid, .is-valid').forEach(field => {
            this.clearFieldValidation(field);
        });
    }

    setFormSubmitting(form, isSubmitting) {
        form.dataset.submitting = isSubmitting.toString();
        
        const submitBtns = form.querySelectorAll('button[type="submit"]');
        submitBtns.forEach(btn => {
            btn.disabled = isSubmitting;
        });
    }

    setButtonLoading(button, text = 'جاري الإرسال...') {
        if (!button) return;
        
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${text}`;
        button.disabled = true;
    }

    resetButton(button) {
        if (!button) return;
        
        button.innerHTML = button.dataset.originalText || button.innerHTML;
        button.disabled = false;
    }

    debounceValidation(field, validationFn) {
        const fieldId = field.id || field.name || Math.random().toString();
        
        if (this.timers.has(fieldId)) {
            clearTimeout(this.timers.get(fieldId));
        }
        
        this.timers.set(fieldId, setTimeout(validationFn, this.config.validationDelay));
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name=csrf-token]')?.content || '';
    }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
    window.FormsManager = new FormsManager();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FormsManager;
}
