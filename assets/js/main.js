// IPRO SDK Documentation - Main JavaScript
// Enhanced Interactive Experience

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initNavigation();
    initDropdownMenus();
    initCodeHighlight();
    initTabs();
    initEnhancedCopyButtons();
    initSmoothScroll();
    initScrollAnimations();
    initActiveNavigation();
    initProgressBar();
    initThemeToggle();
    initSearchModal();
    initTooltips();
    initBackToTop();
    initTableOfContents();
    initKeyboardNavigation();
    initImageLightbox();
    initTableWrappers();
});

// Navigation Toggle
function initNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
            }
        });
        
        // Close menu when clicking a link (but not dropdown toggles)
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', function(e) {
                // Don't close if it's a dropdown toggle
                if (this.closest('.has-dropdown') && !this.getAttribute('href').startsWith('/')) {
                    return;
                }
                navMenu.classList.remove('active');
            });
        });
    }
}

// Dropdown Menus
function initDropdownMenus() {
    // New dropdown structure (.nav-dropdown)
    const dropdowns = document.querySelectorAll('.nav-dropdown');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.nav-dropdown-btn');
        const menu = dropdown.querySelector('.nav-dropdown-menu');
        
        if (!toggle || !menu) return;
        
        // Handle click for mobile
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // On mobile, toggle the dropdown
            if (window.innerWidth <= 900) {
                dropdown.classList.toggle('active');
                
                // Close other dropdowns
                dropdowns.forEach(other => {
                    if (other !== dropdown) {
                        other.classList.remove('active');
                    }
                });
            }
        });
    });
    
    // Close dropdowns when clicking outside (mobile)
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.nav-dropdown') && window.innerWidth <= 900) {
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });

    // Legacy dropdown support (.nav-item.has-dropdown)
    const legacyDropdowns = document.querySelectorAll('.nav-item.has-dropdown');
    
    legacyDropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.nav-link');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (!toggle || !menu) return;
        
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (window.innerWidth <= 768) {
                dropdown.classList.toggle('active');
                
                legacyDropdowns.forEach(other => {
                    if (other !== dropdown) {
                        other.classList.remove('active');
                    }
                });
            }
        });
    });
    
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.nav-item.has-dropdown')) {
            legacyDropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });
}

// Code Highlight
function initCodeHighlight() {
    if (typeof hljs !== 'undefined') {
        hljs.highlightAll();
    }
}

// Tabs
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const target = this.dataset.tab;
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            const targetContent = document.getElementById(target);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

// Enhanced Copy to Clipboard - Works on all code blocks
function initEnhancedCopyButtons() {
    const isEn = document.documentElement.lang?.startsWith('en');
    const copyText = isEn ? 'Copy' : '複製';
    const copiedText = isEn ? 'Copied!' : '已複製!';
    const failText = isEn ? 'Failed' : '失敗';
    const ariaLabel = isEn ? 'Copy code' : '複製程式碼';

    // Find all pre elements and code-blocks
    const codeElements = document.querySelectorAll('pre, .code-block');

    codeElements.forEach(element => {
        // Skip if already has a copy button
        if (element.querySelector('.copy-btn')) return;

        const pre = element.tagName === 'PRE' ? element : element.querySelector('pre');
        if (!pre) return;

        const code = pre.querySelector('code') || pre;
        if (!code.textContent.trim()) return;

        // Create copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i> ' + copyText;
        copyBtn.setAttribute('aria-label', ariaLabel);

        // Handle click
        copyBtn.addEventListener('click', async (e) => {
            e.stopPropagation();

            try {
                await navigator.clipboard.writeText(code.textContent);

                // Success feedback
                copyBtn.classList.add('copied');
                copyBtn.classList.add('copy-pulse');
                copyBtn.innerHTML = '<i class="fas fa-check"></i> ' + copiedText;

                setTimeout(() => {
                    copyBtn.classList.remove('copied');
                    copyBtn.classList.remove('copy-pulse');
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i> ' + copyText;
                }, 2000);
            } catch (err) {
                console.error('Copy failed:', err);
                copyBtn.innerHTML = '<i class="fas fa-times"></i> ' + failText;
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i> ' + copyText;
                }, 2000);
            }
        });

        // Add button to element
        if (element.classList.contains('code-block')) {
            element.appendChild(copyBtn);
        } else {
            // For standalone pre elements, make them relative and add button
            element.style.position = 'relative';
            element.appendChild(copyBtn);
        }
    });
}

// Smooth Scroll
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            
            if (target) {
                const navbarHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navbarHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Scroll-triggered reveal animations
function initScrollAnimations() {
    // Legacy: make old scroll-fade-in elements visible
    document.querySelectorAll('.scroll-fade-in').forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
    });

    // New: IntersectionObserver-based reveal for cards and sections
    const revealTargets = document.querySelectorAll(
        '.feature-card, .app-card, .stat-item, .section-header, ' +
        '.architecture-layers .layer, .protocol-stack .stack-layer, ' +
        '.comparison-card, .spec-card, .tutorial-card'
    );

    if (!revealTargets.length) return;

    revealTargets.forEach(el => el.classList.add('reveal-on-scroll'));

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px'
    });

    revealTargets.forEach(el => revealObserver.observe(el));
}

// Active nav link based on scroll position
function initActiveNavigation() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.sidebar-link');

    if (!sections.length || !navLinks.length) return;

    const navbarHeight = document.querySelector('.navbar')?.offsetHeight || 70;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                navLinks.forEach(link => {
                    link.classList.toggle('active', link.getAttribute('href') === '#' + id);
                });
            }
        });
    }, {
        rootMargin: `-${navbarHeight + 20}px 0px -60% 0px`,
        threshold: 0
    });

    sections.forEach(section => observer.observe(section));
}



// Reading Progress Bar
function initProgressBar() {
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    progressBar.innerHTML = '<div class="progress-bar"></div>';
    document.body.appendChild(progressBar);
    
    const bar = progressBar.querySelector('.progress-bar');
    
    window.addEventListener('scroll', () => {
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight - windowHeight;
        const scrolled = window.scrollY;
        const progress = (scrolled / documentHeight) * 100;
        
        bar.style.width = `${progress}%`;
    });
}

// Theme Toggle (Dark/Light)
function initThemeToggle() {
    // Check for existing toggle button or create one
    let themeToggle = document.querySelector('.theme-toggle');
    if (!themeToggle) {
        themeToggle = document.createElement('button');
        themeToggle.className = 'theme-toggle';
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        themeToggle.setAttribute('aria-label', 'Toggle theme');
        
        const navbar = document.querySelector('.nav-container');
        if (navbar) {
            navbar.appendChild(themeToggle);
        }
    }
    
    // Check saved preference
    const savedTheme = localStorage.getItem('theme') || document.documentElement.getAttribute('data-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(themeToggle, savedTheme);
    
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(themeToggle, newTheme);
    });
}

function updateThemeIcon(button, theme) {
    button.innerHTML = theme === 'dark' 
        ? '<i class="fas fa-sun"></i>' 
        : '<i class="fas fa-moon"></i>';
}

// Search Modal
function initSearchModal() {
    // Superseded by the inline navbar search (#nav-search-input).
    // Keep the Cmd/Ctrl+K shortcut as a focus accelerator.
    const input = document.getElementById('nav-search-input');
    if (!input) return;
    document.addEventListener('keydown', function (e) {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            input.focus();
        }
    });
}

function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(el => {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = el.dataset.tooltip;
        
        el.style.position = 'relative';
        el.appendChild(tooltip);
        
        el.addEventListener('mouseenter', () => {
            tooltip.classList.add('visible');
        });
        
        el.addEventListener('mouseleave', () => {
            tooltip.classList.remove('visible');
        });
    });
}

// Back to Top Button
function initBackToTop() {
    const button = document.createElement('button');
    button.className = 'back-to-top';
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(button);
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            button.classList.add('visible');
        } else {
            button.classList.remove('visible');
        }
    });
    
    button.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}


// ==========================================
// Table of Contents (TOC)
// ==========================================
function initTableOfContents() {
    // Skip TOC if page already has a sidebar (doc-sidebar) or is a landing page (hero)
    if (document.querySelector('.doc-sidebar') || document.querySelector('.hero')) {
        return;
    }
    
    // Only show TOC on pages with enough headings
    const headings = document.querySelectorAll('.doc-content h2, .doc-content h3, .content h2, .content h3, main h2, main h3');
    
    if (headings.length < 3) return;
    
    // Create TOC container
    const toc = document.createElement('div');
    toc.className = 'toc-container';
    toc.innerHTML = `
        <div class="toc-title">
            <i class="fas fa-list"></i>
            目錄導航
        </div>
        <ul class="toc-list"></ul>
        <div class="toc-progress">
            <div class="toc-progress-bar"></div>
        </div>
    `;
    
    const tocList = toc.querySelector('.toc-list');
    const progressBar = toc.querySelector('.toc-progress-bar');
    
    // Build TOC list
    headings.forEach((heading, index) => {
        // Add ID to heading if not present
        if (!heading.id) {
            heading.id = `heading-${index}`;
        }
        
        const li = document.createElement('li');
        const link = document.createElement('a');
        link.href = `#${heading.id}`;
        link.className = `toc-link toc-${heading.tagName.toLowerCase()}`;
        link.textContent = heading.textContent;
        link.dataset.target = heading.id;
        
        li.appendChild(link);
        tocList.appendChild(li);
        
        // Smooth scroll on click
        link.addEventListener('click', (e) => {
            e.preventDefault();
            heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
    
    document.body.appendChild(toc);
    
    // Track scroll position and highlight active section
    const updateActiveLink = () => {
        const scrollPos = window.scrollY + 150;
        let activeHeading = null;
        
        headings.forEach(heading => {
            if (heading.offsetTop <= scrollPos) {
                activeHeading = heading;
            }
        });
        
        tocList.querySelectorAll('.toc-link').forEach(link => {
            link.classList.remove('active');
            if (activeHeading && link.dataset.target === activeHeading.id) {
                link.classList.add('active');
            }
        });
        
        // Update progress bar
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollProgress = (window.scrollY / docHeight) * 100;
        progressBar.style.width = `${Math.min(scrollProgress, 100)}%`;
    };
    
    window.addEventListener('scroll', updateActiveLink);
    updateActiveLink();
}

// ==========================================
// Keyboard Navigation
// ==========================================
function initKeyboardNavigation() {
    // Define page navigation order
    const pages = [
        { key: 'h', name: '首頁', url: '/' },
        { key: 'g', name: '快速開始', url: '/getting-started' },
        { key: 'a', name: '架構', url: '/architecture' },
        { key: 'b', name: 'BLE 開發', url: '/ble-development' },
        { key: 'z', name: 'Zephyr RTOS', url: '/zephyr-rtos' },
        { key: 'p', name: '應用範例', url: '/applications' },
        { key: 'v', name: 'VS Code', url: '/vscode-extension' },
        { key: 'r', name: 'API', url: '/api-reference' },
        { key: 'c', name: '更新日誌', url: '/changelog' }
    ];
    
    // Create navigation overlay
    const overlay = document.createElement('div');
    overlay.className = 'page-nav-overlay';
    overlay.innerHTML = `
        <div class="page-nav-modal">
            <div class="page-nav-title">
                <i class="fas fa-compass"></i>
                快速導航 <kbd>G</kbd>
            </div>
            <div class="page-nav-list">
                ${pages.map(p => `
                    <a href="${p.url}" class="page-nav-item" data-key="${p.key}">
                        <span class="nav-key">${p.key.toUpperCase()}</span>
                        <span>${p.name}</span>
                    </a>
                `).join('')}
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    
    // Create keyboard hint
    const hint = document.createElement('div');
    hint.className = 'keyboard-nav-hint';
    hint.innerHTML = `
        <div class="nav-item"><kbd>G</kbd> 導航</div>
        <div class="nav-item"><kbd>←</kbd><kbd>→</kbd> 上下頁</div>
        <div class="nav-item"><kbd>/</kbd> 搜尋</div>
        <div class="nav-item"><kbd>T</kbd> 主題</div>
    `;
    document.body.appendChild(hint);
    
    let showHintTimeout;
    let isNavOpen = false;
    let selectedIndex = 0;
    
    // Show hint on first visit
    if (!localStorage.getItem('keyboard-hint-shown')) {
        setTimeout(() => {
            hint.classList.add('visible');
            setTimeout(() => {
                hint.classList.remove('visible');
            }, 5000);
            localStorage.setItem('keyboard-hint-shown', 'true');
        }, 2000);
    }
    
    // Get current page index
    const currentPath = window.location.pathname.replace(/\/$/, '') || '/';
    const currentIndex = pages.findIndex(p => {
        const pagePath = p.url.replace(/\/$/, '') || '/';
        return currentPath === pagePath || currentPath.endsWith(pagePath);
    });
    
    // Keyboard event handler
    document.addEventListener('keydown', (e) => {
        // Ignore if typing in input/textarea
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        // Toggle navigation overlay with 'G'
        if (e.key.toLowerCase() === 'g' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            isNavOpen = !isNavOpen;
            overlay.classList.toggle('visible', isNavOpen);
            selectedIndex = 0;
            updateSelectedItem();
        }
        
        // Close overlay with Escape
        if (e.key === 'Escape' && isNavOpen) {
            isNavOpen = false;
            overlay.classList.remove('visible');
        }
        
        // Navigate in overlay
        if (isNavOpen) {
            const items = overlay.querySelectorAll('.page-nav-item');
            
            if (e.key === 'ArrowDown' || e.key === 'j') {
                e.preventDefault();
                selectedIndex = (selectedIndex + 1) % items.length;
                updateSelectedItem();
            }
            
            if (e.key === 'ArrowUp' || e.key === 'k') {
                e.preventDefault();
                selectedIndex = (selectedIndex - 1 + items.length) % items.length;
                updateSelectedItem();
            }
            
            if (e.key === 'Enter') {
                e.preventDefault();
                items[selectedIndex]?.click();
            }
            
            // Direct key navigation
            const pressedKey = e.key.toLowerCase();
            const targetPage = pages.find(p => p.key === pressedKey);
            if (targetPage) {
                window.location.href = targetPage.url;
            }
        }
        
        // Previous/Next page with arrow keys (when overlay closed)
        if (!isNavOpen && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
            // Don't interfere with other focused elements
            if (document.activeElement !== document.body) return;
            
            if (e.key === 'ArrowLeft' && currentIndex > 0) {
                window.location.href = pages[currentIndex - 1].url;
            }
            if (e.key === 'ArrowRight' && currentIndex < pages.length - 1) {
                window.location.href = pages[currentIndex + 1].url;
            }
        }
        
        // Theme toggle with 'T'
        if (e.key.toLowerCase() === 't' && !e.ctrlKey && !e.metaKey && !e.altKey && !isNavOpen) {
            const themeToggle = document.querySelector('.theme-toggle');
            if (themeToggle) themeToggle.click();
        }
        
        // Search with '/'
        if (e.key === '/' && !isNavOpen) {
            e.preventDefault();
            const searchModal = document.querySelector('.search-modal');
            if (searchModal) {
                searchModal.classList.add('active');
                searchModal.querySelector('input')?.focus();
            }
        }
        
        // Show keyboard hint with '?'
        if (e.key === '?' && !isNavOpen) {
            hint.classList.add('visible');
            clearTimeout(showHintTimeout);
            showHintTimeout = setTimeout(() => {
                hint.classList.remove('visible');
            }, 3000);
        }
    });
    
    function updateSelectedItem() {
        const items = overlay.querySelectorAll('.page-nav-item');
        items.forEach((item, i) => {
            item.classList.toggle('selected', i === selectedIndex);
        });
    }
    
    // Close overlay on click outside
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            isNavOpen = false;
            overlay.classList.remove('visible');
        }
    });
}

// ==========================================
// Image Lightbox
// ==========================================
function initImageLightbox() {
    // Collect all zoomable images
    const images = document.querySelectorAll('.doc-content img, .content img, main img:not(.logo-img):not([class*="logo"])');
    
    if (images.length === 0) return;
    
    // Create lightbox overlay
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox-overlay';
    lightbox.innerHTML = `
        <button class="lightbox-close" aria-label="關閉">
            <i class="fas fa-times"></i>
        </button>
        <button class="lightbox-nav prev" aria-label="上一張">
            <i class="fas fa-chevron-left"></i>
        </button>
        <button class="lightbox-nav next" aria-label="下一張">
            <i class="fas fa-chevron-right"></i>
        </button>
        <div class="lightbox-counter"></div>
        <div class="lightbox-content">
            <img class="lightbox-image" src="" alt="">
        </div>
        <div class="lightbox-caption"></div>
    `;
    document.body.appendChild(lightbox);
    
    const lightboxImg = lightbox.querySelector('.lightbox-image');
    const lightboxCaption = lightbox.querySelector('.lightbox-caption');
    const lightboxCounter = lightbox.querySelector('.lightbox-counter');
    const closeBtn = lightbox.querySelector('.lightbox-close');
    const prevBtn = lightbox.querySelector('.lightbox-nav.prev');
    const nextBtn = lightbox.querySelector('.lightbox-nav.next');
    
    let currentIndex = 0;
    const imageArray = Array.from(images);
    
    function openLightbox(index) {
        currentIndex = index;
        updateLightbox();
        lightbox.classList.add('visible');
        document.body.style.overflow = 'hidden';
    }
    
    function closeLightbox() {
        lightbox.classList.remove('visible');
        document.body.style.overflow = '';
    }
    
    function updateLightbox() {
        const img = imageArray[currentIndex];
        lightboxImg.src = img.src;
        lightboxImg.alt = img.alt;
        lightboxCaption.textContent = img.alt || img.title || '';
        lightboxCaption.style.display = lightboxCaption.textContent ? 'block' : 'none';
        
        // Update counter
        if (imageArray.length > 1) {
            lightboxCounter.textContent = `${currentIndex + 1} / ${imageArray.length}`;
            lightboxCounter.style.display = 'block';
            prevBtn.style.display = 'flex';
            nextBtn.style.display = 'flex';
        } else {
            lightboxCounter.style.display = 'none';
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
        }
    }
    
    function navigate(direction) {
        currentIndex = (currentIndex + direction + imageArray.length) % imageArray.length;
        updateLightbox();
    }
    
    // Add click handlers to images
    imageArray.forEach((img, index) => {
        img.style.cursor = 'zoom-in';
        img.addEventListener('click', () => openLightbox(index));
    });
    
    // Lightbox controls
    closeBtn.addEventListener('click', closeLightbox);
    prevBtn.addEventListener('click', (e) => { e.stopPropagation(); navigate(-1); });
    nextBtn.addEventListener('click', (e) => { e.stopPropagation(); navigate(1); });
    
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox || e.target === lightbox.querySelector('.lightbox-content')) {
            closeLightbox();
        }
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (!lightbox.classList.contains('visible')) return;
        
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') navigate(-1);
        if (e.key === 'ArrowRight') navigate(1);
    });
    
    // Touch swipe support
    let touchStartX = 0;
    let touchEndX = 0;
    
    lightbox.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    
    lightbox.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > 50) {
            if (diff > 0) navigate(1);
            else navigate(-1);
        }
    }, { passive: true });
}

// Enhanced Code Block Interactions
function initEnhancedCodeBlocks() {
    document.querySelectorAll('.code-block').forEach(block => {
        // Add line numbers
        const code = block.querySelector('code');
        if (code) {
            const lines = code.textContent.split('\n');
            const lineNumbers = document.createElement('div');
            lineNumbers.className = 'line-numbers';
            lineNumbers.innerHTML = lines.map((_, i) => `<span>${i + 1}</span>`).join('');
            block.insertBefore(lineNumbers, code.parentElement);
        }
        
        // Add language badge
        const pre = block.querySelector('pre');
        if (pre) {
            const codeEl = pre.querySelector('code');
            const lang = codeEl?.className.match(/language-(\w+)/)?.[1];
            if (lang) {
                const badge = document.createElement('span');
                badge.className = 'code-lang-badge';
                badge.textContent = lang.toUpperCase();
                block.appendChild(badge);
            }
        }
    });
}



// Auto-wrap tables for mobile scroll
function initTableWrappers() {
    document.querySelectorAll('.doc-content table').forEach(table => {
        if (table.parentElement.classList.contains('table-wrapper')) return;
        const wrapper = document.createElement('div');
        wrapper.className = 'table-wrapper';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
}

// Smooth Image Loading
function initImageLazyLoad() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}
// ==========================================
// Site search (client-side, CJK-safe substring match)
// ==========================================
document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('nav-search-input');
    const results = document.getElementById('nav-search-results');
    if (!input || !results) return;

    const lang = results.dataset.lang || 'zh-TW';
    const indexUrl = results.dataset.index;
    const emptyText = lang === 'en' ? 'No results' : '沒有符合的結果';
    let index = null;
    let loading = false;
    let selected = -1;

    function loadIndex() {
        if (index || loading) return;
        loading = true;
        fetch(indexUrl)
            .then(r => r.json())
            .then(data => { index = data.filter(p => p.lang === lang && p.title); })
            .catch(() => { loading = false; });
    }

    function escapeHtml(s) {
        return s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    }

    function snippet(text, q) {
        const i = text.toLowerCase().indexOf(q);
        if (i < 0) return '';
        const start = Math.max(0, i - 30);
        const end = Math.min(text.length, i + q.length + 50);
        let s = (start > 0 ? '…' : '') + text.slice(start, end) + (end < text.length ? '…' : '');
        const safe = escapeHtml(s);
        const qi = safe.toLowerCase().indexOf(escapeHtml(q).toLowerCase());
        if (qi < 0) return safe;
        return safe.slice(0, qi) + '<mark>' + safe.slice(qi, qi + q.length) + '</mark>' + safe.slice(qi + q.length);
    }

    function render(q) {
        if (!index || !q) { results.classList.remove('open'); results.innerHTML = ''; selected = -1; return; }
        const ql = q.toLowerCase();
        const hits = [];
        for (const p of index) {
            const inTitle = p.title.toLowerCase().includes(ql);
            const occurrences = p.text.toLowerCase().split(ql).length - 1;
            if (inTitle || occurrences > 0) {
                hits.push({ p, score: (inTitle ? 100 : 0) + Math.min(occurrences, 30) });
            }
        }
        hits.sort((a, b) => b.score - a.score);
        const top = hits.slice(0, 8);
        if (!top.length) {
            results.innerHTML = '<div class="search-empty">' + emptyText + '</div>';
        } else {
            results.innerHTML = top.map(h =>
                '<a class="search-result-item" href="' + h.p.url + '">' +
                '<span class="search-result-title">' + escapeHtml(h.p.title) + '</span>' +
                '<span class="search-result-snippet">' + snippet(h.p.text, q) + '</span>' +
                '</a>'
            ).join('');
        }
        selected = -1;
        results.classList.add('open');
    }

    input.addEventListener('focus', loadIndex);
    let debounce = null;
    input.addEventListener('input', function () {
        clearTimeout(debounce);
        const q = input.value.trim();
        debounce = setTimeout(() => render(q), 120);
    });

    input.addEventListener('keydown', function (e) {
        const items = results.querySelectorAll('.search-result-item');
        if (e.key === 'Escape') { results.classList.remove('open'); input.blur(); return; }
        if (!items.length) return;
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault();
            selected = e.key === 'ArrowDown'
                ? Math.min(selected + 1, items.length - 1)
                : Math.max(selected - 1, 0);
            items.forEach((el, i) => el.classList.toggle('selected', i === selected));
            items[selected].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'Enter') {
            e.preventDefault();
            (items[selected >= 0 ? selected : 0]).click();
        }
    });

    document.addEventListener('click', function (e) {
        if (!e.target.closest('.nav-search')) results.classList.remove('open');
    });
});
