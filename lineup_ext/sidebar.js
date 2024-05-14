const container = document.getElementById('lineup-container'); // file-global accessible container
let userIsInteracting = false; // file-global accessible flag

// check if mouse is over sidebar, used to halt animations while user-idle on sidebar
container.addEventListener('mouseover', () => {
    userIsInteracting = true;
});

container.addEventListener('mouseout', () => {
    userIsInteracting = false;
});

function appendImageWithLink(data) {
    // function to handle new images coming in

    // create element for linking
    const link = document.createElement('a');
    link.href = data.hostPageURL;
    link.target = '_blank';

    // create img for display
    const image = document.createElement('img');
    image.src = data.imageData;

    // append
    link.appendChild(image);
    container.appendChild(link);

    // auto-scroll upwards, like chat bubbles, if user's mouse not in sidebar
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


browser.runtime.onMessage.addListener((message) => {
    // listen for new data from model
    // routed via background.js
    if (message.type === 'from-bg') {

        for (each_message of message.query) {
            // for each, in case of empty
            appendImageWithLink(each_message);
        }

    }
});
