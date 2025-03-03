document.getElementById('dataset-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    // Show loading and start progress bar animation
    const loading = document.getElementById('loading');
    const progress = document.getElementById('progress');
    const errorDiv = document.getElementById('error');
    const resultsDiv = document.getElementById('dataset-results');

    loading.style.display = 'block';
    errorDiv.style.display = 'none';
    resultsDiv.innerHTML = '';
    progress.style.width = '0%';

    // Simulate progress animation
    let progressValue = 0;
    const progressInterval = setInterval(() => {
        if (progressValue < 90) { // Stop at 90% until response is received
            progressValue += 2; // Increment smoothly
            progress.style.width = `${progressValue}%`;
        }
    }, 100); // Update every 100ms

    try {
        const response = await fetch('/generate-dataset/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        clearInterval(progressInterval); // Stop animation
        progress.style.width = '100%'; // Complete the bar

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        resultsDiv.innerHTML = JSON.stringify(result, null, 2);
    } catch (error) {
        clearInterval(progressInterval);
        progress.style.width = '0%'; // Reset on error
        errorDiv.innerHTML = `Error: ${error.message}`;
        errorDiv.style.display = 'block';
    } finally {
        setTimeout(() => {
            loading.style.display = 'none'; // Hide loading after a slight delay
            progress.style.width = '0%'; // Reset for next use
        }, 500); // Delay for smooth transition
    }
});