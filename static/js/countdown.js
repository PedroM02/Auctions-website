function updateCountdowns() {
    const countdownElements = document.querySelectorAll('.countdown');
    countdownElements.forEach(el => {
        const endTime = new Date(el.dataset.endtime);
        const now = new Date();
        const diff = endTime - now;

        if (diff <= 0) {
            el.textContent = "Leilão terminado";
            return;
        }

        const seconds = Math.floor((diff / 1000) % 60);
        const minutes = Math.floor((diff / 1000 / 60) % 60);
        const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        el.textContent = `${days}d:${hours}h:${minutes}m:${seconds}s`;
    });
}

updateCountdowns();
setInterval(updateCountdowns, 1000);
