const container = document.getElementById('lineup-container');
let userIsInteracting = false;


// Detect mouseover and mouseout to toggle interaction flag
container.addEventListener('mouseover', () => {
    userIsInteracting = true;
});

container.addEventListener('mouseout', () => {
    userIsInteracting = false;
});

// Function to append an image with a link to the sidebar container
function appendImageWithLink(data) {
    const link = document.createElement('a');
    link.href = data.hostPageURL;
    link.target = '_blank';
    const image = document.createElement('img');
    image.src = data.imageData;

    link.appendChild(image);
    container.appendChild(link);

    // Auto-scroll to the new image if the user isn't interacting
    setTimeout(() => {

        if (!userIsInteracting) {
            requestAnimationFrame(() => {
                container.scrollTo({
                    top: container.scrollHeight + 120,
                    behavior: 'smooth'
                });
            });
        }
    }, 20);
}


// Listen for messages from the background script
browser.runtime.onMessage.addListener((message) => {
    if (message.type === 'from-bg') {

        for (each_message of message.query) {
            appendImageWithLink(each_message);
        }

    }
});

