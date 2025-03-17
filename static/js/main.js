document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    feather.replace();

    // Listen for storage events
    window.addEventListener('storage', (e) => {
        if (e.key === 'breakEnded') {
            clearInterval(timerInterval);
            startBreakBtn.style.display = 'block';
            endBreakBtn.style.display = 'none';
            timerDisplay.textContent = '00:00:00';
            showStatus('¡Descanso finalizado en otra ventana!', 'info');
        }
    });

    // Check for active break
    fetch('/check-break-status')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'active') {
                startTime = new Date(data.start_timestamp * 1000);
                timerInterval = setInterval(updateTimer, 1000);
                startBreakBtn.style.display = 'none';
                endBreakBtn.style.display = 'block';
                showStatus('Descanso en progreso', 'info');
            }
        });

    // Elements
    const startBreakBtn = document.getElementById('startBreakBtn');
    const endBreakBtn = document.getElementById('endBreakBtn');
    const timerDisplay = document.getElementById('timerDisplay');
    const reasonModal = new bootstrap.Modal(document.getElementById('reasonModal'));
    const breakReasonInput = document.getElementById('breakReason');
    const submitReasonBtn = document.getElementById('submitReason');
    const statusMessage = document.getElementById('statusMessage');

    let startTime;
    let timerInterval;

    // Update timer display
    function updateTimer() {
        const now = new Date();
        const diff = now - startTime;
        const hours = Math.floor(diff / 3600000);
        const minutes = Math.floor((diff % 3600000) / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        
        timerDisplay.textContent = 
            String(hours).padStart(2, '0') + ':' +
            String(minutes).padStart(2, '0') + ':' +
            String(seconds).padStart(2, '0');
    }

    // Show status message
    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = `alert alert-${type} mt-3`;
        statusMessage.style.display = 'block';
        setTimeout(() => {
            statusMessage.style.display = 'none';
        }, 3000);
    }

    // Start break handler
    startBreakBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/start-break', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.status === 'success') {
                startTime = new Date();
                timerInterval = setInterval(updateTimer, 1000);
                
                startBreakBtn.style.display = 'none';
                endBreakBtn.style.display = 'block';
                showStatus('¡Descanso iniciado!', 'success');
            } else {
                showStatus('Fallo al iniciar el descanso', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showStatus('Fallo al iniciar el descanso', 'danger');
        }
    });

    // End break handler
    endBreakBtn.addEventListener('click', () => {
        clearInterval(timerInterval);
        reasonModal.show();
    });

    // Submit reason handler
    submitReasonBtn.addEventListener('click', async () => {
        const reason = breakReasonInput.value.trim();
        
        if (!reason) {
            showStatus('Por favor, introduce un motivo para el descanso', 'warning');
            return;
        }

        try {
            const response = await fetch('/end-break', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ reason })
            });
            const data = await response.json();

            if (data.status === 'success') {
                reasonModal.hide();
                startBreakBtn.style.display = 'block';
                endBreakBtn.style.display = 'none';
                timerDisplay.textContent = '00:00:00';
                breakReasonInput.value = '';
                // Notify other windows
                localStorage.setItem('breakEnded', Date.now().toString());
                showStatus('¡Hora de descanso logueada con exito!', 'success');
            } else {
                showStatus(data.message || 'Failed to log break', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showStatus('Error al loguear la hora', 'danger');
        }
    });
});
