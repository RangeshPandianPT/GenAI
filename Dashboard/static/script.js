// Add a subtle follow-mouse effect to the cards
document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);
    });
});

// Health Check Logic
async function checkServicesHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        for (const [service, isUp] of Object.entries(data)) {
            const indicator = document.getElementById(`status-${service}`);
            if (indicator) {
                if (isUp) {
                    indicator.className = 'status-indicator up';
                    indicator.innerHTML = '<span class="dot"></span> Online';
                } else {
                    indicator.className = 'status-indicator down';
                    indicator.innerHTML = '<span class="dot"></span> Offline';
                }
            }
        }
    } catch (error) {
        console.error('Failed to check health', error);
    }
}

// Check on load and every 5 seconds
checkServicesHealth();
setInterval(checkServicesHealth, 5000);
