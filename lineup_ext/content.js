let imgObserver; // globally accessible observer

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


function setupObserver() {
  // implement observer to be able to call processing, when images in focus

  imgObserver = new IntersectionObserver((entries, observer) => {

      const visibleImages = entries.filter(entry => entry.isIntersecting).map(entry => entry.target);

      // if images in focus, but any value (any part visible)
      if (visibleImages.length > 0) {
          processImages(visibleImages, observer);
      }
  }, {
      root: null, // don't set root for observer 
      rootMargin: '0px', // calibrate to 0px
      threshold: 0.1  // setting trigger
  });

  // find and select all images

  document.querySelectorAll('img:not([data-linedup="true"])').forEach(img => {

    imgObserver.observe(img);

  });

}


function observeNewImages() {
  // observe new images, even when dynamically loaded post Content-loaded
  
  // iterate and observe
  document.querySelectorAll('img:not([data-linedup="true"])').forEach(img => {
      imgObserver.observe(img);
  });
}

// set up at start
setupObserver();

// secondary observer ingest at arbitrary time
setTimeout(() => {
  observeNewImages();
}, 380);

// additional observer ingest at user-idle based on scroll
let timeout = null;
window.addEventListener('scroll', () => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    observeNewImages();
  }, 600);
});

/*

END OF OBSERVER SETUP AND CONTAINER SETUP














START OF IMAGE PARSING AND MESSAGE OUT

*/ 

function findOthers(hostPageURL, imageDirectURL, embedding) {
  // function to allow user to query similar faces from database
  
  // prepare message in correct structure
  const messageContent = {
    hostPageURL: hostPageURL,
    imageDirectURL: imageDirectURL,
    embedding: embedding
  };

  // send message
  browser.runtime.sendMessage({
      type: 'to-bg',
      query: messageContent
  });

}


function processImages(images) {
  // auto function to query database for face
  
  // take in observed, visible images
  images.forEach(img => {

        // convert to base64
        imageToBase64(img, (base64Image) => {
          
          // if conversion ok (dependent on CSP)
          if (base64Image) {

            // pack and send
            browser.runtime.sendMessage({
              type: 'to-bg',
              content: {
                hostPageURL: window.location.href,
                imageDirectURL: img.src,
                imageData: base64Image,
              }
            });

            // set processed flag
            img.setAttribute('data-linedup', 'true');

            // remove from observed images
            imgObserver.unobserve(img); 
          }
      });
  });
}

 

function imageToBase64(imgElement, callback) {
  // function to convert img elements to base64

  // create HTML5 canvas
  const canvas = document.createElement('canvas');

  // create context for canvas
  const context = canvas.getContext('2d');

  // set canvas size to img size
  canvas.width = imgElement.clientWidth;
  canvas.height = imgElement.clientHeight;
  
  // draw
  // WARN: can taint canvas
  context.drawImage(imgElement, 0, 0, imgElement.clientWidth, imgElement.clientHeight);

  try {
    // cast to img and return
    // WARN: can fail due to browser idiosyncratic CSP
    // Possible error "tainted due to CORS"
    const dataURL = canvas.toDataURL('image/png');
    callback(dataURL);

  } catch (error) {
    // useful for regular console, not extension debugger
    console.error("Failed to convert image to base64:", error);
    callback(null);
  }
}

/*

END OF IMAGE PARSING














START OF IMAGE PARSING AND MESSAGE OUT

*/ 

function configureButtonStyle(x, y) {
  // branding function
  // FUTURE: making font-family work
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
      pointer-events: all;

      font-family: 'Gill Sans, sans-serif';
      transform: scale(0.8);
      transition: transform 70ms;
  `;
}


function findButtonAtPosition(x, y) {
  // function to locate previous buttons, to perform updates
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
  // updater for images, based on returns from model
  
  // find the element to update, based on img.src matching
  const imageTags = document.querySelectorAll(`img[src="${data.imageDirectURL}"]`);

  // apply 'forEach' in case of dynamic unloading
  imageTags.forEach(imageTag => {

      // get onscreen size, to calc positions
      const rect = imageTag.getBoundingClientRect();

      // loop over each face in data
      for (let idx = 0; idx < data.facial_area.length; idx++) {

          // unpack face data
          const faceBox = data.facial_area[idx];
          
          // unpack x and y position of button
          const xPosition = rect.left + window.scrollX + (faceBox.x_per / 100 * rect.width);
          const yPosition = rect.top + window.scrollY + (faceBox.y_per / 100 * rect.height);

          // Check if there's already a button here
          const existingButton = findButtonAtPosition(xPosition, yPosition);
          const hitRate = data.hit_rate[idx];

          // perform conditional text update for button, if already present
          if (existingButton) {
              const currentText = existingButton.textContent;

              // update text content if the new number is larger
              if (parseInt(currentText) < hitRate || currentText === ' ') {
                currentText = hitRate.toString();
              }

          } else {

              // no existing button, create a new one
              const button = document.createElement('a');
              
              // set text
              button.textContent = hitRate > 1 ? hitRate.toString() : ' ';

              // set style and position
              button.style.cssText = configureButtonStyle(xPosition, yPosition);

              // add event for user-triggered query
              button.addEventListener('click', function(event) {
                  
                  // allow button's overlay to not fall through
                  event.stopPropagation();
                  event.preventDefault();

                  // set function to find similar faces
                  findOthers(window.location.href, imageTag.src, data.embeddings[idx]);
              });

              // wind up animation and show end frame
              setTimeout(() => {
                button.style.transform = 'scale(1)';
              }, 10); // add delay to animation to not collide

              // add button to holding container
              // avoids problems with DOM/CSS idiosyncracies
              // consistently overlays button
              document.querySelector('#lineup-container').appendChild(button);
          }
      }
  });
}

// recieve data to update and add buttons
browser.runtime.onMessage.addListener((message) => {
  if (message.action === "updateImages") {
    updateImages(message.data);
  }
});
