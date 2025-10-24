// Premium Parallax effect with enhanced smoothness
let ticking = false;
let parallaxStyle = null;

document.addEventListener('DOMContentLoaded', () => {
    parallaxStyle = document.createElement('style');
    parallaxStyle.id = 'parallax-style';
    document.head.appendChild(parallaxStyle);

    // Initialize scroll reveal animations
    initScrollReveal();

    // Add subtle mouse move effect for hero
    initMouseParallax();

    // Add intersection observer for staggered animations
    initIntersectionObserver();
});

// Enhanced parallax with smoother motion
window.addEventListener('scroll', () => {
    if (!ticking) {
        window.requestAnimationFrame(() => {
            const scrolled = window.pageYOffset;
            const parallaxOffset = scrolled * 0.08; // Slightly slower for premium feel

            if (parallaxStyle) {
                parallaxStyle.textContent = `body::before {
                    transform: translate3d(0, ${parallaxOffset}px, 0);
                    transition: transform 0.05s ease-out;
                }`;
            }

            ticking = false;
        });
        ticking = true;
    }
}, { passive: true });

// Smooth scroll for anchor links
document.addEventListener('DOMContentLoaded', () => {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});

// Scroll reveal animations
function initScrollReveal() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements that should animate on scroll
    const elementsToAnimate = document.querySelectorAll('.cta-section, .quick-links');
    elementsToAnimate.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1), transform 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
        observer.observe(el);
    });
}

// Subtle mouse parallax for hero section
function initMouseParallax() {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    let mouseX = 0;
    let mouseY = 0;
    let currentX = 0;
    let currentY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX - window.innerWidth / 2) / 100;
        mouseY = (e.clientY - window.innerHeight / 2) / 100;
    });

    function animate() {
        currentX += (mouseX - currentX) * 0.05;
        currentY += (mouseY - currentY) * 0.05;

        hero.style.transform = `translate(${currentX}px, ${currentY}px)`;
        requestAnimationFrame(animate);
    }

    animate();
}

// Intersection observer for enhanced scroll effects
function initIntersectionObserver() {
    const observerOptions = {
        threshold: [0, 0.25, 0.5, 0.75, 1],
        rootMargin: '0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && entry.intersectionRatio > 0.3) {
                entry.target.classList.add('in-view');
            }
        });
    }, observerOptions);

    const cards = document.querySelectorAll('.feature-card, .quick-link');
    cards.forEach(card => observer.observe(card));
}

// Add premium button hover sound effect (visual feedback)
document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.cta-button, .quick-link');

    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
        });
    });
});
