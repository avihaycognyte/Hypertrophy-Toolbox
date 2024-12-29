export function initializeNavHighlighting() {
    // Get current path
    const currentPath = window.location.pathname;
    
    // Remove any existing active classes
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Map paths to nav items
    const pathMap = {
        '/': 'nav-home',
        '/workout_plan': 'nav-workout-plan',
        '/weekly_summary': 'nav-weekly-summary',
        '/session_summary': 'nav-session-summary',
        '/workout_log': 'nav-workout-log'
    };
    
    // Add active class to current page's nav item
    const navId = pathMap[currentPath];
    if (navId) {
        const navItem = document.getElementById(navId);
        if (navItem) {
            navItem.classList.add('active');
        }
    }
    
    // Add click handlers for smooth transitions
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't add active class if it's just a regular link
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
            }
            
            // Remove active class from all links
            document.querySelectorAll('.nav-link').forEach(l => {
                l.classList.remove('active');
            });
            
            // Add active class to clicked link
            this.classList.add('active');
        });
    });
} 