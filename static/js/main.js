/**
 * Main JavaScript file for Barbershop website
 * This file coordinates all modules and provides global functionality
 */

// Global application object
window.BarbershopApp = {
    modules: {},
    config: {
        debug: false,
        apiBaseUrl: '/api/',
        csrfToken: null
    },
    
    init() {
        this.loadConfig();
        this.initGlobalFeatures();
        this.bindGlobalEvents();
        console.log('Barbershop App initialized');
    },
    
    loadConfig() {
        // Load CSRF token
        this.config.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                                document.querySelector('meta[name=csrf-token]')?.content;
        
        // Set debug mode based on Django DEBUG setting
        this.config.debug = document.body.dataset.debug === 'true';
        
        // Set user authentication status
        this.config.isAuthenticated = document.body.dataset.authenticated === 'true';
    },
    
    initGlobalFeatures() {
        this.initSmoothScrolling();
        this.initAnimations();
        this.initTooltips();
        this.initBackToTop();
        this.initLazyLoading();
    },
    
    bindGlobalEvents() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.config.isAuthenticated) {
                // Refresh notifications when page becomes visible
                window.NotificationManager?.fetchNotifications();
            }
        });
        
        // Handle network status changes
        window.addEventListener('online', () => {
            window.NotificationManager?.success('تم استعادة الاتصال بالإنترنت');
        });
        
        window.addEventListener('offline', () => {
            window.NotificationManager?.warning('تم فقدان الاتصال بالإنترنت');
        });
        
        // Handle global keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    },
    
    initSmoothScrolling() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                const targetSection = document.querySelector(targetId);
                
                if (targetSection) {
                    const headerOffset = document.querySelector('.navbar')?.offsetHeight || 0;
                    const elementPosition = targetSection.offsetTop;
                    const offsetPosition = elementPosition - headerOffset - 20;
                    
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    },
    
    initAnimations() {
        // Animate elements on scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);
        
        // Observe elements
        const animateElements = document.querySelectorAll('.haircut-card, .contact-card, .about-image-placeholder');
        animateElements.forEach(el => {
            observer.observe(el);
        });
        
        // Add CSS for animations
        const style = document.createElement('style');
        style.textContent = `
            .haircut-card, .contact-card, .about-image-placeholder {
                opacity: 0;
                transform: translateY(30px);
                transition: all 0.6s ease;
            }
            
            .animate-in {
                opacity: 1 !important;
                transform: translateY(0) !important;
            }
            
            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,.3);
                border-radius: 50%;
                border-top-color: #fff;
                animation: spin 1s ease-in-out infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            .form-control.is-invalid,
            .form-select.is-invalid {
                border-color: #dc3545;
                box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
            }
        `;
        document.head.appendChild(style);
    },
    
    initTooltips() {
        // Initialize tooltips if Bootstrap is available
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        }
    },
    
    initBackToTop() {
        // Initialize back to top button
        const backToTopButton = document.querySelector('.back-to-top');
        
        if (backToTopButton) {
            const headerHeight = document.querySelector('.navbar')?.offsetHeight || 0;
            
            window.addEventListener('scroll', () => {
                const scrollPosition = window.scrollY;
                
                if (scrollPosition > headerHeight) {
                    backToTopButton.classList.add('show');
                } else {
                    backToTopButton.classList.remove('show');
                }
            });
            
            backToTopButton.addEventListener('click', () => {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        }
    },
    
    initLazyLoading() {
        // Initialize lazy loading
        const lazyLoadImages = document.querySelectorAll('img.lazy-load');
        
        if (lazyLoadImages.length > 0) {
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };
            
            const observer = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const image = entry.target;
                        image.src = image.dataset.src;
                        image.classList.remove('lazy-load');
                        observer.unobserve(image);
                    }
                });
            }, observerOptions);
            
            lazyLoadImages.forEach(image => {
                observer.observe(image);
            });
        }
    },
    
    handleKeyboardShortcuts(e) {
        // Handle global keyboard shortcuts
        if (e.key === 'Escape') {
            // Close any open modals
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
            });
        }
    },
    
    // Utility functions for backward compatibility
    getCSRFToken() {
        return this.config.csrfToken;
    },
    
    showNotification(message, type = 'info') {
        if (window.NotificationManager) {
            window.NotificationManager.show(message, type);
        } else {
            // Fallback notification
            const notification = document.createElement('div');
            notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            notification.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 5000);
        }
    }
};

// Initialize Barbershop App
document.addEventListener('DOMContentLoaded', () => {
    window.BarbershopApp.init();
});

// Global utility functions for backward compatibility
function showNotification(message, type = 'info') {
    window.BarbershopApp.showNotification(message, type);
}

function getCSRFToken() {
    return window.BarbershopApp.getCSRFToken();
}