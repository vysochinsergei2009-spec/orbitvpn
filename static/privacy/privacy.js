// Parallax эффект для фона
let ticking = false;
let parallaxStyle = null;

// Создаем style элемент один раз
document.addEventListener('DOMContentLoaded', () => {
    parallaxStyle = document.createElement('style');
    parallaxStyle.id = 'parallax-style';
    document.head.appendChild(parallaxStyle);
});

window.addEventListener('scroll', () => {
    if (!ticking) {
        window.requestAnimationFrame(() => {
            const scrolled = window.pageYOffset;
            const parallaxOffset = scrolled * 0.08; // 8% скорости скролла

            if (parallaxStyle) {
                parallaxStyle.textContent = `body::before { transform: translate3d(0, ${parallaxOffset}px, 0); }`;
            }

            ticking = false;
        });
        ticking = true;
    }
}, { passive: true });

// Smooth scroll для якорных ссылок
document.addEventListener('DOMContentLoaded', () => {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    const offset = 80; // Отступ для sticky nav
                    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
});
