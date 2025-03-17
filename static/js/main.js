document.addEventListener('DOMContentLoaded', function() {
    feather.replace();

    // Elementos de la interfaz
    const startBreakBtn = document.getElementById('startBreakBtn');
    const endBreakBtn = document.getElementById('endBreakBtn');
    const timerDisplay = document.getElementById('timerDisplay');

    let startTime;
    let timerInterval;

    // Función para actualizar el temporizador en pantalla
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

    // Escuchar eventos de almacenamiento para sincronizar ventanas
    window.addEventListener('storage', (e) => {
        if (e.key === 'breakStart') {
            startTime = new Date(parseInt(localStorage.getItem('breakStart')));
            startBreakBtn.style.display = 'none';
            endBreakBtn.style.display = 'block';
            clearInterval(timerInterval);
            timerInterval = setInterval(updateTimer, 1000);
        }

        if (e.key === 'breakEnded') {
            clearInterval(timerInterval);
            startBreakBtn.style.display = 'block';
            endBreakBtn.style.display = 'none';
            timerDisplay.textContent = '00:00:00';
        }
    });

    // Verificar si hay un descanso activo al cargar la página
    const savedStart = localStorage.getItem('breakStart');
    if (savedStart) {
        startTime = new Date(parseInt(savedStart));
        startBreakBtn.style.display = 'none';
        endBreakBtn.style.display = 'block';
        timerInterval = setInterval(updateTimer, 1000);
    }

    // Iniciar descanso
    startBreakBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/start-break', { method: 'POST' });
            const data = await response.json();

            if (data.status === 'success') {
                startTime = new Date();
                localStorage.setItem('breakStart', startTime.getTime()); // Guardar en localStorage
                window.dispatchEvent(new Event('storage')); // Forzar actualización en otras ventanas
                
                startBreakBtn.style.display = 'none';
                endBreakBtn.style.display = 'block';
                timerInterval = setInterval(updateTimer, 1000);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Finalizar descanso
    endBreakBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/end-break', { method: 'POST' });
            const data = await response.json();

            if (data.status === 'success') {
                localStorage.removeItem('breakStart');
                localStorage.setItem('breakEnded', Date.now());
                window.dispatchEvent(new Event('storage'));

                startBreakBtn.style.display = 'block';
                endBreakBtn.style.display = 'none';
                clearInterval(timerInterval);
                timerDisplay.textContent = '00:00:00';
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });
});
