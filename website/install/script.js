let ticking = false;
let parallaxStyle = null;

document.addEventListener('DOMContentLoaded', () => {
    parallaxStyle = document.createElement('style');
    parallaxStyle.id = 'parallax-style';
    document.head.appendChild(parallaxStyle);
});

window.addEventListener('scroll', () => {
    if (!ticking) {
        window.requestAnimationFrame(() => {
            const scrolled = window.pageYOffset;
            const parallaxOffset = scrolled * 0.1;

            if (parallaxStyle) {
                parallaxStyle.textContent = `body::before { transform: translate3d(0, ${parallaxOffset}px, 0); }`;
            }

            ticking = false;
        });
        ticking = true;
    }
}, { passive: true });

const observerOptions = {
    threshold: 0.15,
    rootMargin: '0px 0px -10% 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            entry.target.classList.remove('hidden');
        } else {
            entry.target.classList.remove('visible');
            entry.target.classList.add('hidden');
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.nav, .section, .step, .app-list, .important');

    animatedElements.forEach(element => {
        element.classList.add('fade-element');
        observer.observe(element);
    });
});
