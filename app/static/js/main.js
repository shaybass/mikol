/**
 * MIKOL Main JavaScript
 * Version 2.0
 */

document.addEventListener('DOMContentLoaded', function() {
    initMobileDrawer();
    initTabs();
    initFlashMessages();
    initModals();
    initCopyButtons();
    initFollowButtons();
    initShareButtons();
});

/**
 * Mobile Drawer Navigation
 */
function initMobileDrawer() {
    const menuBtn = document.getElementById('mobile-menu-btn');
    const drawer = document.getElementById('mobile-drawer');
    const backdrop = document.getElementById('mobile-menu-backdrop');
    const closeBtn = document.getElementById('mobile-drawer-close');

    if (!menuBtn || !drawer) return;

    function openDrawer() {
        drawer.classList.add('active');
        backdrop.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeDrawer() {
        drawer.classList.remove('active');
        backdrop.classList.remove('active');
        document.body.style.overflow = '';
    }

    menuBtn.addEventListener('click', openDrawer);
    closeBtn?.addEventListener('click', closeDrawer);
    backdrop?.addEventListener('click', closeDrawer);

    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && drawer.classList.contains('active')) {
            closeDrawer();
        }
    });
}

/**
 * Tab Navigation
 */
function initTabs() {
    const tabContainers = document.querySelectorAll('.tabs');

    tabContainers.forEach(container => {
        const tabs = container.querySelectorAll('.tab');
        const parent = container.parentElement;
        const contents = parent.querySelectorAll('.tab-content');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.tab;

                // Update tabs
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                // Update content
                contents.forEach(content => {
                    content.classList.remove('active');
                    if (content.id === target) {
                        content.classList.add('active');
                    }
                });
            });
        });
    });
}

/**
 * Flash Messages Auto-hide
 */
function initFlashMessages() {
    const flashContainer = document.getElementById('flash-container');
    if (!flashContainer) return;

    const flashes = flashContainer.querySelectorAll('.flash');

    flashes.forEach((flash, index) => {
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(100%)';
            flash.style.transition = 'all 0.3s ease-out';

            setTimeout(() => {
                flash.remove();
                if (flashContainer.children.length === 0) {
                    flashContainer.remove();
                }
            }, 300);
        }, 5000 + (index * 500));
    });
}

/**
 * Modal System
 */
function initModals() {
    // Open modal buttons
    document.querySelectorAll('[data-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modalId = btn.dataset.modal;
            openModal(modalId);
        });
    });

    // Close modal buttons
    document.querySelectorAll('.modal-close, [data-modal-close]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal');
            if (modal) closeModal(modal.id);
        });
    });

    // Close on backdrop click
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) {
                const modal = document.querySelector('.modal.active');
                if (modal) closeModal(modal.id);
            }
        });
    });

    // Close on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.querySelector('.modal.active');
            if (modal) closeModal(modal.id);
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    const backdrop = document.querySelector('.modal-backdrop');

    if (!modal) return;

    backdrop?.classList.add('active');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    const backdrop = document.querySelector('.modal-backdrop');

    if (!modal) return;

    backdrop?.classList.remove('active');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// Expose globally
window.openModal = openModal;
window.closeModal = closeModal;

/**
 * Copy to Clipboard
 */
function initCopyButtons() {
    document.querySelectorAll('[data-copy]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const targetId = btn.dataset.copy;
            const target = document.getElementById(targetId);
            const text = target?.value || target?.textContent;

            if (!text) return;

            try {
                await navigator.clipboard.writeText(text);

                // Visual feedback
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                btn.classList.add('copied');

                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.classList.remove('copied');
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    });
}

/**
 * Follow/Unfollow Buttons
 */
function initFollowButtons() {
    document.querySelectorAll('.btn-follow').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();

            const userId = btn.dataset.userId;
            const isFollowing = btn.classList.contains('following');
            const url = isFollowing ? `/profiles/${userId}/unfollow` : `/profiles/${userId}/follow`;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    }
                });

                if (response.ok) {
                    btn.classList.toggle('following');

                    // Update button text
                    const followText = btn.querySelector('.follow-text');
                    if (followText) {
                        followText.textContent = btn.classList.contains('following') ? 'Following' : 'Follow';
                    }

                    // Update follower count if visible
                    const followerCount = document.querySelector('[data-followers-count]');
                    if (followerCount) {
                        const count = parseInt(followerCount.textContent);
                        followerCount.textContent = isFollowing ? count - 1 : count + 1;
                    }
                }
            } catch (err) {
                console.error('Follow action failed:', err);
            }
        });
    });
}

/**
 * Share Buttons
 */
function initShareButtons() {
    document.querySelectorAll('[data-share]').forEach(btn => {
        btn.addEventListener('click', () => {
            const platform = btn.dataset.share;
            const url = btn.dataset.url || window.location.href;
            const title = btn.dataset.title || document.title;

            let shareUrl;

            switch (platform) {
                case 'facebook':
                    shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
                    break;
                case 'linkedin':
                    shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
                    break;
                case 'twitter':
                    shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`;
                    break;
                case 'whatsapp':
                    shareUrl = `https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}`;
                    break;
                case 'copy':
                    navigator.clipboard.writeText(url).then(() => {
                        showToast('Link copied to clipboard!');
                    });
                    return;
            }

            if (shareUrl) {
                window.open(shareUrl, '_blank', 'width=600,height=400');
            }
        });
    });
}

/**
 * Get CSRF Token from meta tag or cookie
 */
function getCSRFToken() {
    // Try meta tag first
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.content;

    // Try cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrf_token') return value;
    }

    // Try hidden input
    const input = document.querySelector('input[name="csrf_token"]');
    if (input) return input.value;

    return '';
}

/**
 * Show Toast Notification
 */
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');

    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'flash-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `flash flash-${type}`;
    toast.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease-out';

        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

window.showToast = showToast;

/**
 * Confirm Delete
 */
function confirmDelete(message = 'Are you sure you want to delete this?') {
    return confirm(message);
}

window.confirmDelete = confirmDelete;

/**
 * Relative Time Formatting
 */
function formatRelativeTime(date) {
    const now = new Date();
    const diff = now - new Date(date);
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (seconds < 60) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return new Date(date).toLocaleDateString();
}

window.formatRelativeTime = formatRelativeTime;

/**
 * Lazy Load Images
 */
function initLazyLoad() {
    const images = document.querySelectorAll('img[data-src]');

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => observer.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

// Initialize lazy loading when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLazyLoad);
} else {
    initLazyLoad();
}
