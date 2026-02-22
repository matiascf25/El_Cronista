/**
 * UI Layout Logic for DnD El Cronista VTT
 * Handles collapsible panels and responsive canvas resizing.
 */

document.addEventListener('DOMContentLoaded', () => {
    const leftPanel = document.getElementById('left-panel');
    const mainContent = document.getElementById('main-content');
    const toggleBtn = document.getElementById('toggle-panel-btn');

    if (toggleBtn && leftPanel) {
        toggleBtn.addEventListener('click', () => {
            leftPanel.classList.toggle('collapsed');
            
            // Adjust main content width
            if (leftPanel.classList.contains('collapsed')) {
                mainContent.style.marginLeft = '0';
                mainContent.style.width = '100%';
                toggleBtn.innerHTML = '➤';
                toggleBtn.style.left = '10px';
            } else {
                mainContent.style.marginLeft = '25%';
                mainContent.style.width = '75%';
                toggleBtn.innerHTML = '◀';
                toggleBtn.style.left = '25%';
            }

            // Trigger window resize event to let Fabric.js know
            setTimeout(() => {
                window.dispatchEvent(new Event('resize'));
            }, 300); // Wait for CSS transition
        });
    }

    // Floating Action Bar tooltips or effects can be added here
});
