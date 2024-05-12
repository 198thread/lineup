let imgObserver;

function setupObserver() {
  imgObserver = new IntersectionObserver((entries, observer) => {
      // Filter for images that are intersecting (visible)
      const visibleImages = entries.filter(entry => entry.isIntersecting).map(entry => entry.target);
      if (visibleImages.length > 0) {
          processImages(visibleImages, observer);
      }
  }, {
      root: null,  // Observing with respect to the viewport
      rootMargin: '0px',
      threshold: 0.1  // Adjust based on when you want to trigger the processing
  });

  // Select and observe the images
  document.querySelectorAll('img:not([data-linedup="true"])').forEach(img => {
    imgObserver.observe(img);
  });
}


function observeNewImages() {
  const newImages = document.querySelectorAll('img:not([data-linedup="true"])');
  newImages.forEach(img => {
      if (!img.hasAttribute('data-linedup')) {
        imgObserver.observe(img);
      }
  });
}

setupObserver();


setTimeout(() => {
  observeNewImages();
}, 380);


let timeout = null;
window.addEventListener('scroll', () => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    observeNewImages();
  }, 600);
});



// Setup a global container for floating elements if not already present
if (!document.querySelector('#lineup-container')) {
  const floatingContainer = document.createElement('div');
  floatingContainer.id = 'lineup-container';
  floatingContainer.style.position = 'absolute';
  floatingContainer.style.top = '0';
  floatingContainer.style.left = '0';
  floatingContainer.style.width = '100%';
  floatingContainer.style.height = '100%';
  floatingContainer.style.pointerEvents = 'none'; // Allows clicks to pass through when not on a button
  document.body.appendChild(floatingContainer);
}




/*

END OF OBSERVER SETUP AND CONTAINER SETUP



START OF IMAGE PARSING AND MESSAGE OUT

*/ 





function findOthers(hostPageURL, imageDirectURL, embedding) {

  const messageContent = {
    hostPageURL: hostPageURL,
    imageDirectURL: imageDirectURL, // Corrected to use the current imageTag in the loop
    embedding: embedding
  };

  browser.runtime.sendMessage({
      type: 'to-bg',
      query: messageContent
  });

}


function processImages(images) {

  // Process only new images that don't have the 'linedup' property
  images.forEach(img => {

        // Process the image
        imageToBase64(img, (base64Image) => {
          if (base64Image) {

            // Send the image data to background.js
            browser.runtime.sendMessage({
              type: 'to-bg',
              content: {
                hostPageURL: window.location.href,
                imageDirectURL: img.src,
                imageData: base64Image,
              }
            });

            img.setAttribute('data-linedup', 'true');

            imgObserver.unobserve(img); 
          }
      });
  });
}

 

function imageToBase64(imgElement, callback) {
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  canvas.width = imgElement.clientWidth;
  canvas.height = imgElement.clientHeight;
  context.drawImage(imgElement, 0, 0, imgElement.clientWidth, imgElement.clientHeight);

  try {
    const dataURL = canvas.toDataURL('image/png');
    callback(dataURL);
  } catch (error) {
    console.error("Failed to convert image to base64:", error);
    callback(null);
  }
}



/*

END OF IMAGE PARSING


START OF IMAGE PARSING AND MESSAGE OUT

*/ 





function configureButtonStyle(x, y) {
  return `
      text-decoration: none;
      color: black;
      position: absolute;
      left: ${x}px;
      top: ${y}px;
      background-color: rgba(255, 255, 153, 0.7);
      border: 3px solid rgb(204, 255, 0);
      border-radius: 50%;
      width: 20px;
      height: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1001;
      cursor: pointer;
      user-select: none;
      pointer-events: all; // Ensure the button can be clicked

      font-family: 'Gill Sans, sans-serif';
      transform: scale(0.8); /* Start from a scaled down state */
      transition: transform 70ms; /* Simple transition for scaling */

  `;
}


function findButtonAtPosition(x, y) {

  const buttons = document.querySelectorAll('#lineup-container > a');

  for (const button of buttons) {
      
      const btnX = parseFloat(button.style.left);
      const btnY = parseFloat(button.style.top);

      if (Math.abs(btnX - x) < 3 && Math.abs(btnY - y) < 3) {
          return button;
      }

  }

  return null;
}




function updateImages(data) {
  const imageTags = document.querySelectorAll(`img[src="${data.imageDirectURL}"]`);

  imageTags.forEach(imageTag => {
      const rect = imageTag.getBoundingClientRect();

      // Loop over the index of facial areas
      for (let idx = 0; idx < data.facial_area.length; idx++) {
          const faceBox = data.facial_area[idx]; // Access faceBox using index
          const xPosition = rect.left + window.scrollX + (faceBox.x_per / 100 * rect.width);
          const yPosition = rect.top + window.scrollY + (faceBox.y_per / 100 * rect.height);

          // Check if there's already a button here
          const existingButton = findButtonAtPosition(xPosition, yPosition);
          const hitRate = data.hit_rate[idx];

          if (existingButton) {

              const currentText = existingButton.textContent;
              // Update text content if the new number is larger
              if (parseInt(currentText) < hitRate || currentText === ' ') {
                currentText = hitRate.toString();
              }
          } else {
              // No existing button, create a new one
              const button = document.createElement('a');
              button.textContent = hitRate > 1 ? hitRate.toString() : ' ';
              button.style.cssText = configureButtonStyle(xPosition, yPosition);
              button.addEventListener('click', function(event) {
                  event.stopPropagation();
                  event.preventDefault();
                  findOthers(window.location.href, imageTag.src, data.embeddings[idx]);
              });

              // Trigger the scale animation
              setTimeout(() => {
                button.style.transform = 'scale(1)';
              }, 10); // Short delay to ensure the initial style is applied first


              document.querySelector('#lineup-container').appendChild(button);
          }
      }
  });
}

browser.runtime.onMessage.addListener((message) => {
  if (message.action === "updateImages") {
    updateImages(message.data);
  }
});




