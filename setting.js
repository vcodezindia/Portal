// Global settings functionality
(function() {
  // Theme definitions
  const themes = {
    blue: {
      primary: '#1282a2',
      primaryLight: '#034748'
    },
    purple: {
      primary: '#8b5cf6',
      primaryLight: '#6d28d9'
    },
    green: {
      primary: '#10b981',
      primaryLight: '#047857'
    },
    red: {
      primary: '#ef4444',
      primaryLight: '#b91c1c'
    },
    orange: {
      primary: '#f59e0b',
      primaryLight: '#d97706'
    }
  };

  // Apply saved settings on page load
  function applySettings() {
    const root = document.documentElement;
    const navbar = document.querySelector('.navbar');
    const cardHeaders = document.querySelectorAll('.card-header');
    
    // Apply dark mode if enabled
    if (localStorage.getItem('dark-mode') === 'enabled') {
      document.body.classList.add('dark-mode');
    }
    
    // Apply saved color theme
    const savedColor = localStorage.getItem('theme-color') || 'blue';
    const theme = themes[savedColor];
    
    if (theme) {
      // Update CSS variables
      root.style.setProperty('--primary', theme.primary);
      root.style.setProperty('--primary-light', theme.primaryLight);
      
      // Update navbar background
      if (navbar) {
        navbar.style.background = `linear-gradient(to right, ${theme.primary}, ${theme.primaryLight})`;
      }
      
      // Update card headers
      if (cardHeaders) {
        cardHeaders.forEach(header => {
          header.style.background = `linear-gradient(to right, ${theme.primary}, ${theme.primaryLight})`;
        });
      }
    }
    
    // Apply font size
    const savedFontSize = localStorage.getItem('font-size') || 'medium';
    document.body.classList.add(`font-${savedFontSize}`);
    
    // Apply animation preference
    if (localStorage.getItem('reduce-animations') === 'enabled') {
      document.body.classList.add('reduce-animations');
    }
  }

  // Create particles background
  function initializeParticles() {
    const particlesContainer = document.getElementById('particles');
    if (!particlesContainer) return;
    
    const particleCount = 15;
    
    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div');
      particle.classList.add('particle');
      particle.style.width = Math.random() * 150 + 50 + 'px';
      particle.style.height = particle.style.width;
      particle.style.left = Math.random() * 100 + '%';
      particle.style.top = Math.random() * 100 + '%';
      particle.style.animationDelay = Math.random() * 5 + 's';
      particlesContainer.appendChild(particle);
    }
  }

  // Initialize mobile menu
  function initializeMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navLinks = document.getElementById('navLinks');
    
    if (!mobileMenuToggle || !navLinks) return;
    
    mobileMenuToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      mobileMenuToggle.innerHTML = navLinks.classList.contains('active') 
        ? '<i class="fas fa-times"></i>' 
        : '<i class="fas fa-bars"></i>';
    });
  }

  // Initialize settings page specific functionality
  function initializeSettingsPage() {
    // Tab functionality
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    if (tabs.length === 0) return; // Not on settings page
    
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const tabId = tab.getAttribute('data-tab');
        
        // Remove active class from all tabs and contents
        tabs.forEach(t => t.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        
        // Add active class to clicked tab and corresponding content
        tab.classList.add('active');
        document.getElementById(tabId).classList.add('active');
      });
    });
    
    // Color theme selection
    const colorOptions = document.querySelectorAll('.color-option');
    
    colorOptions.forEach(option => {
      option.addEventListener('click', () => {
        const color = option.getAttribute('data-color');
        
        // Update active state
        colorOptions.forEach(o => o.classList.remove('active'));
        option.classList.add('active');
        
        // Save theme preference
        localStorage.setItem('theme-color', color);
        
        // Apply theme
        applySettings();
      });
    });
    
    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    if (darkModeToggle) {
      // Set initial state
      darkModeToggle.checked = localStorage.getItem('dark-mode') === 'enabled';
      
      darkModeToggle.addEventListener('change', () => {
        if (darkModeToggle.checked) {
          localStorage.setItem('dark-mode', 'enabled');
        } else {
          localStorage.setItem('dark-mode', 'disabled');
        }
        
        // Apply settings
        applySettings();
      });
    }
    
    // Two-factor authentication toggle
    const twoFactorToggle = document.getElementById('twoFactorToggle');
    const twoFactorOptions = document.getElementById('twoFactorOptions');
    
    if (twoFactorToggle && twoFactorOptions) {
      twoFactorToggle.addEventListener('change', () => {
        twoFactorOptions.style.display = twoFactorToggle.checked ? 'block' : 'none';
      });
    }
    
    // Save settings button functionality
    const saveSettings = document.getElementById('saveSettings');
    
    if (saveSettings) {
      saveSettings.addEventListener('click', () => {
        // Get form values
        const fontSize = document.getElementById('fontSize').value;
        const reduceAnimations = document.getElementById('reduceAnimations').checked;
        
        // Save preferences
        localStorage.setItem('font-size', fontSize);
        localStorage.setItem('reduce-animations', reduceAnimations ? 'enabled' : 'disabled');
        
        // Apply settings
        applySettings();
        
        // Show success message
        alert('Settings saved successfully!');
      });
    }
    
    // Highlight active color option based on saved preference
    const savedColor = localStorage.getItem('theme-color');
    if (savedColor) {
      document.querySelector(`.color-option[data-color="${savedColor}"]`)?.classList.add('active');
    }
    
    // Set font size dropdown to saved value
    const savedFontSize = localStorage.getItem('font-size');
    if (savedFontSize && document.getElementById('fontSize')) {
      document.getElementById('fontSize').value = savedFontSize;
    }
    
    // Set reduce animations checkbox to saved state
    if (localStorage.getItem('reduce-animations') === 'enabled' && document.getElementById('reduceAnimations')) {
      document.getElementById('reduceAnimations').checked = true;
    }
  }

  // Initialize logout functionality
  function initializeLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    
    if (logoutBtn) {
      logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (confirm('Are you sure you want to logout?')) {
          // In a real application, this would call a logout API
          window.location.href = '/login';
        }
      });
    }
  }

  // Add event listeners after DOM is loaded
  document.addEventListener('DOMContentLoaded', function() {
    // Apply saved settings first
    applySettings();
    
    // Initialize components
    initializeParticles();
    initializeMobileMenu();
    initializeSettingsPage();
    initializeLogout();
    
    // Handle active navigation state
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href === currentPath) {
        link.classList.add('active');
      }
    });
  });
})();