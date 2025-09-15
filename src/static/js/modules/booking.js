/**
 * Booking Module - handles all booking-related functionality
 */

class BookingManager {
    constructor() {
        this.elements = {};
        this.init();
    }

    init() {
        this.cacheElements();
        this.bindEvents();
        this.setupDateTimeConstraints();
    }

    cacheElements() {
        this.elements = {
            dateInput: document.querySelector('input[type="date"]'),
            timeInput: document.querySelector('input[type="time"]'),
            form: document.querySelector('form[data-booking-form]'),
            barbershopInput: document.querySelector('input[name="barbershop"]'),
            serviceInput: document.querySelector('input[name="service"]'),
            selectionCards: document.querySelectorAll('.selection-card'),
            submitBtn: document.querySelector('button[type="submit"]')
        };
    }

    bindEvents() {
        // Event delegation for selection cards
        document.addEventListener('click', (e) => this.handleCardSelection(e));
        
        // Form submission
        if (this.elements.form) {
            this.elements.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Real-time validation
        ['dateInput', 'timeInput'].forEach(input => {
            if (this.elements[input]) {
                this.elements[input].addEventListener('change', () => this.validateDateTime());
            }
        });
    }

    handleCardSelection(e) {
        const card = e.target.closest('.selection-card');
        if (!card) return;
        
        const container = card.closest('.row');
        const inputName = container.dataset.inputName;
        const hiddenInput = document.querySelector(`input[name="${inputName}"]`);
        
        if (!hiddenInput) return;

        // Remove active class from all cards in this container
        container.querySelectorAll('.selection-card').forEach(c => 
            c.classList.remove('active')
        );
        
        // Add active class to selected card
        card.classList.add('active');
        
        // Update hidden input value
        hiddenInput.value = card.dataset.value;
        
        // Trigger custom event
        this.triggerEvent('cardSelected', {
            type: inputName,
            value: card.dataset.value,
            card: card
        });
    }

    setupDateTimeConstraints() {
        if (this.elements.dateInput) {
            const today = new Date().toISOString().split('T')[0];
            this.elements.dateInput.setAttribute('min', today);
            
            const maxDate = new Date();
            maxDate.setMonth(maxDate.getMonth() + 3);
            this.elements.dateInput.setAttribute('max', maxDate.toISOString().split('T')[0]);
        }
        
        if (this.elements.timeInput) {
            this.elements.timeInput.setAttribute('min', '08:00');
            this.elements.timeInput.setAttribute('max', '22:00');
        }
    }

    validateDateTime() {
        const date = this.elements.dateInput?.value;
        const time = this.elements.timeInput?.value;
        
        if (!date || !time) return true;

        const selectedDate = new Date(date);
        const selectedTime = new Date(selectedDate.toDateString() + ' ' + time);
        const now = new Date();
        
        // Check if booking is in the past
        if (selectedDate.toDateString() === now.toDateString() && selectedTime <= now) {
            this.showError('لا يمكن حجز موعد في وقت سابق من الوقت الحالي');
            return false;
        }

        // Check if booking is on weekend (Friday/Saturday in Arabic context)
        const dayOfWeek = selectedDate.getDay();
        if (dayOfWeek === 5 || dayOfWeek === 6) { // Friday = 5, Saturday = 6
            this.showWarning('تنبيه: قد تكون بعض الصالونات مغلقة في عطلة نهاية الأسبوع');
        }

        return true;
    }

    validateForm() {
        const requiredFields = [
            { element: this.elements.dateInput, name: 'التاريخ' },
            { element: this.elements.timeInput, name: 'الوقت' },
            { element: this.elements.serviceInput, name: 'الخدمة' },
            { element: this.elements.barbershopInput, name: 'الصالون' }
        ];

        const errors = [];

        requiredFields.forEach(field => {
            if (!field.element?.value) {
                errors.push(`يرجى اختيار ${field.name}`);
                field.element?.classList.add('is-invalid');
            } else {
                field.element?.classList.remove('is-invalid');
            }
        });

        if (errors.length > 0) {
            this.showError(errors.join('<br>'));
            return false;
        }

        return this.validateDateTime();
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (!this.validateForm()) return;

        const submitBtn = this.elements.submitBtn;
        const originalText = submitBtn?.innerHTML;
        
        try {
            // Show loading state
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>جاري الحجز...';
                submitBtn.disabled = true;
            }

            // Collect form data
            const formData = new FormData(this.elements.form);
            
            // Submit form
            const response = await fetch(this.elements.form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                this.showSuccess('تم إرسال طلب الحجز بنجاح! سنتواصل معك قريباً.');
                this.elements.form.reset();
                this.clearSelections();
            } else {
                throw new Error('فشل في إرسال الطلب');
            }

        } catch (error) {
            this.showError('حدث خطأ أثناء إرسال الطلب. يرجى المحاولة مرة أخرى.');
            console.error('Booking submission error:', error);
        } finally {
            // Restore button state
            if (submitBtn && originalText) {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        }
    }

    clearSelections() {
        this.elements.selectionCards.forEach(card => 
            card.classList.remove('active')
        );
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    showError(message) {
        window.NotificationManager?.show(message, 'error');
    }

    showSuccess(message) {
        window.NotificationManager?.show(message, 'success');
    }

    showWarning(message) {
        window.NotificationManager?.show(message, 'warning');
    }

    triggerEvent(eventName, data) {
        const event = new CustomEvent(`booking:${eventName}`, { detail: data });
        document.dispatchEvent(event);
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('[data-booking-form]')) {
        window.BookingManager = new BookingManager();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BookingManager;
}
