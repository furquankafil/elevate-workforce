/**
 * Elevate Workforce - Core JavaScript Suite
 * Handles animations, state persistence, UI elements, and asynchronous events.
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================================================
    // 1. LOADING SCREEN REMOVAL
    // ==========================================================================
    const preloader = document.getElementById('loading-screen');
    if (preloader) {
        window.addEventListener('load', () => {
            // Smoothly fade out using standard CSS transitions
            preloader.style.opacity = '0';
            preloader.style.visibility = 'hidden';
            setTimeout(() => {
                preloader.remove();
            }, 500);
        });
        
        // Backup: Hide loader after a maximum of 4 seconds in case load triggers fail
        setTimeout(() => {
            preloader.style.opacity = '0';
            preloader.style.visibility = 'hidden';
        }, 4000);
    }

    // ==========================================================================
    // 2. THEME SWITCHER ENGINE (LIGHT / DARK)
    // ==========================================================================
    const themeToggleBtn = document.getElementById('theme-toggle');
    const darkIcon = document.querySelector('.icon-dark');
    const lightIcon = document.querySelector('.icon-light');

    // Function to apply the requested theme parameters
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);

        if (theme === 'dark') {
            darkIcon.classList.add('d-none');
            lightIcon.classList.remove('d-none');
        } else {
            lightIcon.classList.add('d-none');
            darkIcon.classList.remove('d-none');
        }
    };

    // Initialize display states based on localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const targetTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(targetTheme);
        });
    }

    // ==========================================================================
    // 3. STICKY NAV TRANSITIONS
    // ==========================================================================
    const navbar = document.querySelector('.custom-navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('shadow-lg', 'py-2');
            navbar.classList.remove('py-3');
            navbar.style.backgroundColor = 'var(--bg-gradient-glass)';
        } else {
            navbar.classList.remove('shadow-lg', 'py-2');
            navbar.classList.add('py-3');
        }
    });

    // ==========================================================================
    // 4. FLOATING INTERACTIVE TRIGGERS (BACK TO TOP)
    // ==========================================================================
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });

        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // ==========================================================================
    // 5. ANIMATIONS (AOS & GSAP INITIATION)
    // ==========================================================================
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            mirror: false
        });
    }

    // GSAP ScrollTrigger Effects (if libraries loaded successfully)
    if (typeof gsap !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);

        // Smooth landing slide-ins for elements with class .animate-on-scroll
        gsap.utils.toArray('.card-glass').forEach(card => {
            gsap.from(card, {
                scrollTrigger: {
                    trigger: card,
                    start: 'top 85%',
                    toggleActions: 'play none none none'
                },
                opacity: 0,
                y: 30,
                duration: 0.8,
                ease: 'power3.out'
            });
        });
    }

    // ==========================================================================
    // 6. SWIPER SLIDERS
    // ==========================================================================
    if (typeof Swiper !== 'undefined') {
        // Testimonials Slider configuration
        new Swiper('.testimonials-slider', {
            slidesPerView: 1,
            spaceBetween: 30,
            loop: true,
            autoplay: {
                delay: 4000,
                disableOnInteraction: false,
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            breakpoints: {
                768: {
                    slidesPerView: 2,
                },
                1024: {
                    slidesPerView: 3,
                }
            }
        });
    }

    // ==========================================================================
    // 7. ASYNCHRONOUS NEWSLETTER ENGINE
    // ==========================================================================
    const newsletterForm = document.getElementById('footer-newsletter-form');
    const newsletterMsg = document.getElementById('newsletter-message');

    if (newsletterForm && newsletterMsg) {
        newsletterForm.addEventListener('submit', function (e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[name="email"]');
            const csrfToken = this.querySelector('input[name="csrfmiddlewaretoken"]').value;
            const actionUrl = this.getAttribute('action');

            const formData = new FormData();
            formData.append('email', emailInput.value);
            formData.append('csrfmiddlewaretoken', csrfToken);

            // Fetch dynamic feedback asynchronously
            fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json().then(data => ({ status: response.status, body: data })))
            .then(res => {
                if (res.status === 200) {
                    newsletterMsg.className = 'fs-13 mt-2 text-success poppins-medium';
                    newsletterMsg.textContent = res.body.message;
                    emailInput.value = '';
                } else {
                    newsletterMsg.className = 'fs-13 mt-2 text-warning poppins-medium';
                    newsletterMsg.textContent = res.body.message || 'Submission failed.';
                }
            })
            .catch(() => {
                newsletterMsg.className = 'fs-13 mt-2 text-danger poppins-medium';
                newsletterMsg.textContent = 'An error occurred. Please try again later.';
            });
        });
    }
});

