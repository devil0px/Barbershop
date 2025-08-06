/**
 * Notification Module - handles all notification functionality
 */

class NotificationManager {
    constructor() {
        this.container = null;
        this.notifications = new Map();
        this.config = {
            duration: 5000,
            maxNotifications: 5,
            position: 'top-right'
        };
        this.init();
    }

    init() {
        this.createContainer();
        this.bindEvents();
        this.loadExistingNotifications();
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.className = `notification-container position-fixed ${this.config.position}`;
        this.container.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            pointer-events: none;
        `;
        document.body.appendChild(this.container);
    }

    bindEvents() {
        // Auto-hide Django messages
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                const alerts = document.querySelectorAll('.alert.alert-dismissible');
                alerts.forEach(alert => {
                    if (window.bootstrap?.Alert) {
                        new bootstrap.Alert(alert).close();
                    }
                });
            }, this.config.duration);
        });

        // Listen for custom notification events
        document.addEventListener('notification:show', (e) => {
            this.show(e.detail.message, e.detail.type, e.detail.options);
        });

        document.addEventListener('notification:clear', () => {
            this.clearAll();
        });
    }

    show(message, type = 'info', options = {}) {
        const id = this.generateId();
        const notification = this.createNotification(id, message, type, options);
        
        // Remove oldest if we exceed max notifications
        if (this.notifications.size >= this.config.maxNotifications) {
            const oldestId = this.notifications.keys().next().value;
            this.remove(oldestId);
        }

        this.container.appendChild(notification);
        this.notifications.set(id, notification);

        // Trigger entrance animation
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        // Auto-remove after duration
        if (options.duration !== 0) {
            const duration = options.duration || this.config.duration;
            setTimeout(() => this.remove(id), duration);
        }

        return id;
    }

    createNotification(id, message, type, options) {
        const notification = document.createElement('div');
        notification.id = `notification-${id}`;
        notification.className = `alert alert-${this.getBootstrapType(type)} alert-dismissible fade notification-item`;
        notification.style.cssText = `
            pointer-events: auto;
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: none;
            border-radius: 8px;
        `;

        const icon = this.getIcon(type);
        const closeBtn = options.closable !== false ? 
            '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' : '';

        notification.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="me-2">${icon}</div>
                <div class="flex-grow-1">${message}</div>
                ${closeBtn}
            </div>
        `;

        // Add click handler for close button
        const closeButton = notification.querySelector('.btn-close');
        if (closeButton) {
            closeButton.addEventListener('click', () => this.remove(id));
        }

        return notification;
    }

    remove(id) {
        const notification = this.notifications.get(id);
        if (!notification) return;

        notification.classList.remove('show');
        notification.classList.add('fade-out');

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            this.notifications.delete(id);
        }, 300);
    }

    clearAll() {
        this.notifications.forEach((_, id) => this.remove(id));
    }

    getBootstrapType(type) {
        const typeMap = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info',
            'primary': 'primary'
        };
        return typeMap[type] || 'info';
    }

    getIcon(type) {
        const icons = {
            'success': '<i class="fas fa-check-circle text-success"></i>',
            'error': '<i class="fas fa-exclamation-circle text-danger"></i>',
            'warning': '<i class="fas fa-exclamation-triangle text-warning"></i>',
            'info': '<i class="fas fa-info-circle text-info"></i>',
            'primary': '<i class="fas fa-bell text-primary"></i>'
        };
        return icons[type] || icons.info;
    }

    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    loadExistingNotifications() {
        // Load notifications from server for authenticated users
        if (document.body.dataset.authenticated === 'true') {
            this.fetchNotifications();
            // Update notifications every 30 seconds
            setInterval(() => this.fetchNotifications(), 30000);
        }
    }

    async fetchNotifications() {
        try {
            const response = await fetch('/notifications/api/unread-count/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateNotificationBadge(data.count);
                
                // Show new notifications
                data.notifications?.forEach(notification => {
                    if (!notification.is_read) {
                        this.show(notification.message, 'info', {
                            duration: 0, // Don't auto-hide
                            closable: true
                        });
                    }
                });
            }
        } catch (error) {
            console.error('Failed to fetch notifications:', error);
        }
    }

    updateNotificationBadge(count) {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        }
    }

    async markAsRead(notificationId) {
        try {
            await fetch(`/notifications/api/mark-read/${notificationId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name=csrf-token]')?.content || '';
    }

    // Public API methods
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    error(message, options = {}) {
        return this.show(message, 'error', options);
    }

    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }

    info(message, options = {}) {
        return this.show(message, 'info', options);
    }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
    window.NotificationManager = new NotificationManager();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationManager;
}
