document.addEventListener('DOMContentLoaded', function() {
    feather.replace();

    const startBreakBtn = document.getElementById('startBreakBtn');
    const endBreakBtn = document.getElementById('endBreakBtn');
    const timerDisplay = document.getElementById('timerDisplay');
    const reasonModal = new bootstrap.Modal(document.getElementById('reasonModal'));
    const breakReasonInput = document.getElementById('breakReason');
    const submitReasonBtn = document.getElementById('submitReason');
    const statusMessage = document.getElementById('statusMessage');

    let startTime;
    let timerInterval;

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

    function startTimer() {
        if (timerInterval) clearInterval(timerInterval);  // Evita intervalos duplicados
        timerInterval = setInterval(updateTimer, 1000);
    }

    function stopTimer() {
        clearInterval(timerInterval);
        timerDisplay.textContent = '00:00:00';
        startBreakBtn.style.display = 'block';
        endBreakBtn.style.display = 'none';
        localStorage.removeItem('breakActive');
        localStorage.removeItem('startTime');
    }

    function checkBreakStatus() {
        fetch('/check-break-status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'active') {
                    startTime = new Date(data.start_timestamp * 1000);
                    localStorage.setItem('breakActive', 'true');
                    localStorage.setItem('startTime', startTime.getTime().toString());
                    startTimer();
                    startBreakBtn.style.display = 'none';
                    endBreakBtn.style.display = 'block';
                    showStatus('Descanso en progreso', 'info');
                } else {
                    stopTimer();
                }
            });
    }

    if (localStorage.getItem('breakActive') === 'true') {
        startTime = new Date(parseInt(localStorage.getItem('startTime')));
        startTimer();
        startBreakBtn.style.display = 'none';
        endBreakBtn.style.display = 'block';
    }

    window.addEventListener('storage', (e) => {
        if (e.key === 'breakEnded') {
            stopTimer();
            showStatus('¡Descanso finalizado en otra ventana!', 'info');
        }
    });

    startBreakBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/start-break', { method: 'POST' });
            const data = await response.json();

            if (data.status === 'success') {
                startTime = new Date();
                localStorage.setItem('breakActive', 'true');
                localStorage.setItem('startTime', startTime.getTime().toString());
                startTimer();
                
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

    endBreakBtn.addEventListener('click', () => {
        clearInterval(timerInterval);
        reasonModal.show();
    });

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
                stopTimer();
                breakReasonInput.value = '';
                
                localStorage.setItem('breakEnded', Date.now().toString());

                showStatus('¡Hora de descanso logueada con éxito!', 'success');
            } else {
                showStatus(data.message || 'Fallo al loguear el descanso', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showStatus('Error al loguear la hora', 'danger');
        }
    });

    checkBreakStatus();
});
