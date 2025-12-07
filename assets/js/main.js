// IPRO SDK Documentation - Main JavaScript
// Enhanced Interactive Experience

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initNavigation();
    initCodeHighlight();
    initTabs();
    initCopyButtons();
    initSmoothScroll();
    initScrollAnimations();
    initActiveNavigation();
    initParticleBackground();
    initTypingEffect();
    initProgressBar();
    initThemeToggle();
    initSearchModal();
    initTooltips();
    initBackToTop();
    initCountUpAnimations();
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
        
        // Close menu when clicking a link
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
            });
        });
    }
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

// Copy to Clipboard
function initCopyButtons() {
    document.querySelectorAll('.code-copy-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const codeBlock = this.closest('.code-block');
            const code = codeBlock.querySelector('code').textContent;
            
            try {
                await navigator.clipboard.writeText(code);
                
                // Visual feedback
                const originalIcon = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i>';
                this.style.color = '#10b981';
                
                setTimeout(() => {
                    this.innerHTML = originalIcon;
                    this.style.color = '';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
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

// Intersection Observer for animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.feature-card, .app-card, .stat-item').forEach(el => {
        observer.observe(el);
    });
}

// Active nav link based on scroll position
function initActiveNavigation() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.sidebar-link');
    
    window.addEventListener('scroll', () => {
        let current = '';
        const navbarHeight = document.querySelector('.navbar').offsetHeight;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop - navbarHeight - 100;
            const sectionHeight = section.offsetHeight;
            
            if (window.pageYOffset >= sectionTop && window.pageYOffset < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });
}

// Particle Background Effect
function initParticleBackground() {
    const hero = document.querySelector('.hero');
    if (!hero) return;
    
    const canvas = document.createElement('canvas');
    canvas.className = 'particle-canvas';
    canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;';
    hero.insertBefore(canvas, hero.firstChild);
    
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;
    
    function resizeCanvas() {
        canvas.width = hero.offsetWidth;
        canvas.height = hero.offsetHeight;
    }
    
    function createParticle() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * 2 + 1,
            speedX: (Math.random() - 0.5) * 0.5,
            speedY: (Math.random() - 0.5) * 0.5,
            opacity: Math.random() * 0.5 + 0.2
        };
    }
    
    function initParticles() {
        particles = [];
        const particleCount = Math.floor((canvas.width * canvas.height) / 15000);
        for (let i = 0; i < particleCount; i++) {
            particles.push(createParticle());
        }
    }
    
    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach((p, i) => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(99, 102, 241, ${p.opacity})`;
            ctx.fill();
            
            // Draw connections
            particles.slice(i + 1).forEach(p2 => {
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < 100) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(99, 102, 241, ${0.1 * (1 - dist / 100)})`;
                    ctx.stroke();
                }
            });
            
            // Update position
            p.x += p.speedX;
            p.y += p.speedY;
            
            // Wrap around edges
            if (p.x < 0) p.x = canvas.width;
            if (p.x > canvas.width) p.x = 0;
            if (p.y < 0) p.y = canvas.height;
            if (p.y > canvas.height) p.y = 0;
        });
        
        animationId = requestAnimationFrame(drawParticles);
    }
    
    resizeCanvas();
    initParticles();
    drawParticles();
    
    window.addEventListener('resize', () => {
        resizeCanvas();
        initParticles();
    });
}

// Typing Effect for Hero Title
function initTypingEffect() {
    const typingElements = document.querySelectorAll('.typing-effect');
    
    typingElements.forEach(el => {
        const text = el.textContent;
        el.textContent = '';
        el.style.borderRight = '2px solid var(--primary)';
        
        let i = 0;
        function type() {
            if (i < text.length) {
                el.textContent += text.charAt(i);
                i++;
                setTimeout(type, 50);
            } else {
                el.style.borderRight = 'none';
            }
        }
        
        // Start typing when element is visible
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    type();
                    observer.unobserve(el);
                }
            });
        });
        observer.observe(el);
    });
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
    const savedTheme = localStorage.getItem('theme') || 'dark';
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
    // Create search trigger
    const searchTrigger = document.createElement('button');
    searchTrigger.className = 'search-trigger';
    searchTrigger.innerHTML = '<i class="fas fa-search"></i><span class="search-shortcut">⌘K</span>';
    
    const navbar = document.querySelector('.nav-container');
    if (navbar) {
        const themeToggle = navbar.querySelector('.theme-toggle');
        if (themeToggle) {
            navbar.insertBefore(searchTrigger, themeToggle);
        } else {
            navbar.appendChild(searchTrigger);
        }
    }
    
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'search-modal';
    modal.innerHTML = `
        <div class="search-modal-content">
            <div class="search-header">
                <i class="fas fa-search"></i>
                <input type="text" class="search-input" placeholder="搜尋文件...">
                <kbd>ESC</kbd>
            </div>
            <div class="search-results"></div>
            <div class="search-footer">
                <span><kbd>↑</kbd><kbd>↓</kbd> 導航</span>
                <span><kbd>↵</kbd> 開啟</span>
                <span><kbd>ESC</kbd> 關閉</span>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    const searchInput = modal.querySelector('.search-input');
    const searchResults = modal.querySelector('.search-results');
    
    // Search data
    const searchData = [
        { title: '快速開始', url: '/getting-started', category: '入門' },
        { title: '架構概覽', url: '/architecture', category: '架構' },
        { title: 'BLE 開發指南', url: '/ble-development', category: 'BLE' },
        { title: 'Zephyr RTOS', url: '/zephyr-rtos', category: 'RTOS' },
        { title: '應用範例', url: '/applications', category: '範例' },
        { title: 'VS Code Extension', url: '/vscode-extension', category: '工具' },
        { title: 'API 參考', url: '/api-reference', category: 'API' },
        { title: '更新日誌', url: '/changelog', category: '更新' },
        { title: 'BLE 初始化', url: '/ble-development#getting-started', category: 'BLE' },
        { title: 'GAP 操作', url: '/ble-development#gap-operations', category: 'BLE' },
        { title: 'GATT 服務', url: '/ble-development#gatt-services', category: 'BLE' },
        { title: 'ipro_ble_demo', url: '/applications#ipro-ble-demo', category: '範例' },
        { title: 'ipro_zephyr_demo', url: '/applications#ipro-zephyr-demo', category: '範例' },
        { title: 'ipro7_demo', url: '/applications#ipro7-demo', category: '範例' },
    ];
    
    function showModal() {
        modal.classList.add('active');
        searchInput.focus();
        document.body.style.overflow = 'hidden';
    }
    
    function hideModal() {
        modal.classList.remove('active');
        searchInput.value = '';
        searchResults.innerHTML = '';
        document.body.style.overflow = '';
    }
    
    function search(query) {
        if (!query) {
            searchResults.innerHTML = '<div class="search-hint">輸入關鍵字搜尋文件...</div>';
            return;
        }
        
        const results = searchData.filter(item => 
            item.title.toLowerCase().includes(query.toLowerCase()) ||
            item.category.toLowerCase().includes(query.toLowerCase())
        );
        
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="search-no-results">找不到相關結果</div>';
            return;
        }
        
        searchResults.innerHTML = results.map((item, index) => `
            <a href="${item.url}" class="search-result-item ${index === 0 ? 'selected' : ''}">
                <span class="search-result-category">${item.category}</span>
                <span class="search-result-title">${item.title}</span>
                <i class="fas fa-arrow-right"></i>
            </a>
        `).join('');
    }
    
    // Event listeners
    searchTrigger.addEventListener('click', showModal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) hideModal();
    });
    
    searchInput.addEventListener('input', (e) => {
        search(e.target.value);
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Cmd/Ctrl + K to open
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            showModal();
        }
        
        // ESC to close
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            hideModal();
        }
        
        // Navigate results
        if (modal.classList.contains('active')) {
            const items = searchResults.querySelectorAll('.search-result-item');
            const selected = searchResults.querySelector('.search-result-item.selected');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                const next = selected?.nextElementSibling || items[0];
                items.forEach(i => i.classList.remove('selected'));
                next?.classList.add('selected');
            }
            
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                const prev = selected?.previousElementSibling || items[items.length - 1];
                items.forEach(i => i.classList.remove('selected'));
                prev?.classList.add('selected');
            }
            
            if (e.key === 'Enter' && selected) {
                window.location.href = selected.href;
            }
        }
    });
}

// Tooltips
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

// Count Up Animations for Stats
function initCountUpAnimations() {
    const stats = document.querySelectorAll('.stat-value');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const text = el.textContent;
                const match = text.match(/[\d.]+/);
                
                if (match) {
                    const target = parseFloat(match[0]);
                    const suffix = text.replace(match[0], '');
                    const duration = 2000;
                    const start = performance.now();
                    
                    function animate(currentTime) {
                        const elapsed = currentTime - start;
                        const progress = Math.min(elapsed / duration, 1);
                        
                        // Easing function
                        const eased = 1 - Math.pow(1 - progress, 3);
                        const current = target * eased;
                        
                        if (target % 1 === 0) {
                            el.textContent = Math.floor(current) + suffix;
                        } else {
                            el.textContent = current.toFixed(1) + suffix;
                        }
                        
                        if (progress < 1) {
                            requestAnimationFrame(animate);
                        } else {
                            el.textContent = text;
                        }
                    }
                    
                    requestAnimationFrame(animate);
                }
                
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.5 });
    
    stats.forEach(stat => observer.observe(stat));
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