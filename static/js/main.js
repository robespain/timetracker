document.addEventListener('DOMContentLoaded', function() {
  // Initialize Feather icons
  feather.replace();

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

  // Function to save timer state
  function saveTimerState(state) {
    localStorage.setItem('timerState', JSON.stringify(state));
  }

  // Function to get timer state
  function getTimerState() {
    const state = localStorage.getItem('timerState');
    return state ? JSON.parse(state) : null;
  }

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

  // Function to update timer display based on state
  function updateTimerDisplay(state) {
    if (state.isRunning) {
      startTime = new Date(state.startTime);
      timerInterval = setInterval(updateTimer, 1000);
      startBreakBtn.style.display = 'none';
      endBreakBtn.style.display = 'block';
      showStatus('Descanso en progreso', 'info');
    } else {
      clearInterval(timerInterval);
      startBreakBtn.style.display = 'block';
      endBreakBtn.style.display = 'none';
      timerDisplay.textContent = '00:00:00';
      showStatus('Descanso finalizado', 'info');
    }
  }

  // Listen for storage events
  window.addEventListener('storage', (e) => {
    if (e.key === 'timerState') {
      const state = JSON.parse(e.newValue);
      updateTimerDisplay(state);
    }
  });

  // Check for active break
  fetch('/check-break-status')
    .then(response => response.json())
    .then(data => {
      if (data.status === 'active') {
        const state = {
          isRunning: true,
          startTime: data.start_timestamp * 1000
        };
        saveTimerState(state);
        updateTimerDisplay(state);
      }
    });

  // Start break handler
  startBreakBtn.addEventListener('click', async () => {
    try {
      const response = await fetch('/start-break', {
        method: 'POST'
      });
      const data = await response.json();
      if (data.status === 'success') {
        startTime = new Date();
        const state = {
          isRunning: true,
          startTime: startTime.getTime()
        };
        saveTimerState(state);
        updateTimerDisplay(state);
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
        const state = {
          isRunning: false,
          elapsedTime: 0
        };
        saveTimerState(state);
        updateTimerDisplay(state);
        breakReasonInput.value = '';
        showStatus('¡Hora de descanso logueada con éxito!', 'success');
      } else {
        showStatus(data.message || 'Failed to log break', 'danger');
      }
    } catch (error) {
      console.error('Error:', error);
      showStatus('Error al loguear la hora', 'danger');
    }
  });

  // Load saved state on page load
  const savedState = getTimerState();
  if (savedState) {
    updateTimerDisplay(savedState);
  }
});
