// Dashboard functionality

document.addEventListener('DOMContentLoaded', () => {
    const exportBtn = document.getElementById('export-btn');
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    const clearFiltersBtn = document.getElementById('clear-filters-btn');
    
    // Export logs as CSV
    exportBtn.addEventListener('click', async () => {
        const source = document.getElementById('filter-source').value;
        const label = document.getElementById('filter-label').value;
        const startDate = document.getElementById('filter-start-date').value;
        const endDate = document.getElementById('filter-end-date').value;
        
        // Build query params
        const params = new URLSearchParams();
        if (source) params.append('source', source);
        if (label) params.append('label', label);
        if (startDate) params.append('start_date', startDate + 'T00:00:00');
        if (endDate) params.append('end_date', endDate + 'T23:59:59');
        
        // Download CSV
        const url = `/api/logs/export.csv?${params.toString()}`;
        window.location.href = url;
    });
    
    // Apply filters (reload page with filters)
    applyFiltersBtn.addEventListener('click', async () => {
        const source = document.getElementById('filter-source').value;
        const label = document.getElementById('filter-label').value;
        const startDate = document.getElementById('filter-start-date').value;
        const endDate = document.getElementById('filter-end-date').value;
        
        // Build query params
        const params = new URLSearchParams();
        if (source) params.append('source', source);
        if (label) params.append('label', label);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const query = params.toString();
        window.location.href = query ? `/dashboard?${query}` : '/dashboard';
    });
    
    // Clear filters
    clearFiltersBtn.addEventListener('click', () => {
        window.location.href = '/dashboard';
    });
    
    // Auto-refresh stats every 30 seconds
    setInterval(async () => {
        try {
            const response = await fetch('/api/stats');
            if (response.ok) {
                const stats = await response.json();
                // Update stat cards (if needed)
                console.log('Stats refreshed:', stats);
            }
        } catch (error) {
            console.error('Failed to refresh stats:', error);
        }
    }, 30000);
});
