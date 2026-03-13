document.addEventListener('DOMContentLoaded', () => {
    const gridContainer = document.getElementById('computer-grid');
    const loadingState = document.getElementById('loading-state');
    const refreshBtn = document.getElementById('refresh-btn');
    const statusFilter = document.getElementById('status-filter');
    
    const statAvailable = document.getElementById('stat-available');
    const statInUse = document.getElementById('stat-inuse');
    
    let computersData = [];
    let isInitialLoad = true;

    // Fetch data from the python backend
    async function fetchStatuses() {
        try {
            // Because the frontend is served via the same python server
            const response = await fetch('/api/computers');
            if (!response.ok) throw new Error('Network error');
            computersData = await response.json();
            
            // Sort to ensure consistent ordering (e.g. by MachineId)
            computersData.sort((a, b) => a.machineId.localeCompare(b.machineId));
            
            renderGrid();
            updateStats();
            
            if (isInitialLoad) {
                loadingState.classList.add('hidden');
                isInitialLoad = false;
            }
        } catch (err) {
            console.error('Failed to fetch statuses:', err);
            // Optionally show error state to user here
        }
    }

    function updateStats() {
        const availableCount = computersData.filter(c => c.status === 'Available').length;
        const inUseCount = computersData.filter(c => c.status === 'In-Use').length;
        
        statAvailable.textContent = availableCount;
        statInUse.textContent = inUseCount;
    }

    // Format absolute time from heartbeat timestamp
    function formatTimeAgo(timestamp) {
        if (!timestamp) return 'Never';
        const now = Date.now();
        const diffInSeconds = Math.floor((now - timestamp) / 1000);
        
        if (diffInSeconds < 60) return `${diffInSeconds}s ago`;
        
        const diffInMinutes = Math.floor(diffInSeconds / 60);
        if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
        
        const diffInHours = Math.floor(diffInMinutes / 60);
        return `${diffInHours}h ago`;
    }

    function renderGrid() {
        const filterValue = statusFilter.value;
        const filteredData = filterValue === 'All' 
            ? computersData 
            : computersData.filter(c => c.status === filterValue);

        gridContainer.innerHTML = '';

        if (filteredData.length === 0 && !isInitialLoad) {
            gridContainer.innerHTML = `<div class="state-container"><p>No computers match the selected filter.</p></div>`;
            return;
        }

        filteredData.forEach((comp, index) => {
            const card = document.createElement('div');
            card.className = 'computer-card card-appear';
            card.style.animationDelay = `${index * 0.05}s`; // Staggered animation
            card.setAttribute('data-status', comp.status);

            card.innerHTML = `
                <div class="card-header">
                    <h3 class="pc-name">${comp.machineId}</h3>
                    <div class="status-badge">
                        <span class="status-dot"></span>
                        ${comp.status}
                    </div>
                </div>
                <div class="card-footer">
                    <div class="last-seen">
                        <ion-icon class="icon-sub" name="time-outline"></ion-icon>
                        Updated ${formatTimeAgo(comp.lastHeartbeat)}
                    </div>
                    ${comp.status === 'In-Use' ? `
                    <button class="notify-btn" onclick="alert('Notification setup for ${comp.machineId}. You will be pinged when it is free!')">
                        <ion-icon name="notifications-outline"></ion-icon> Notify
                    </button>
                    ` : ''}
                </div>
            `;
            gridContainer.appendChild(card);
        });
    }

    // Event Listeners
    refreshBtn.addEventListener('click', () => {
        // Spin the icon temporarily to give feedback
        const icon = refreshBtn.querySelector('ion-icon');
        icon.style.transition = 'transform 0.5s';
        icon.style.transform = `rotate(360deg)`;
        
        fetchStatuses().then(() => {
            setTimeout(() => {
                icon.style.transition = 'none';
                icon.style.transform = 'rotate(0deg)';
            }, 500);
        });
    });

    statusFilter.addEventListener('change', renderGrid);

    // Initial fetch and set interval for constant live updates
    fetchStatuses();
    setInterval(fetchStatuses, 5000); // Polling every 5 seconds for live feel
});
