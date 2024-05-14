let socket; // file-global accessible socket

function establishWebSocketConnection() {
  // handler for socket expected functions
  
  // implement socket at python app.py address
  socket = new WebSocket('ws://localhost:2882');

  // check for comms
  socket.onopen = function() {
    console.log('WebSocket connected at localhost:2882');
  };

  // handle incoming
  socket.onmessage = function(event) {
    console.log('app.py 📫');

    // cast data to json, to be sent around files
    try {
      let jdata = JSON.parse(event.data);

      // divert to appropriate files
      handleMessageFromServer(jdata);

    } catch (error) {
      
      // use page specific console, not extension debugger
      console.error('Error parsing JSON:', error);
      console.log(event.data)
      return;
    }

  };

  // handle error
  socket.onerror = function(error) {
    console.error('WebSocket Error:', error);
  };

  // handle closing from remote
  socket.onclose = function(event) {
    if (!event.wasClean) {
      console.error(`WebSocket Error: [code ${event.code}] ${event.reason}`);
    }
    // rejoin if possible, check every 5 seconds
    console.log('WebSocket connection closed. Trying to reconnect...');
    setTimeout(establishWebSocketConnection, 5000);
  };
}


function updateImageInTabs(data) {
  // function to divert data, from model to images that need updates

  // find content.js of said page
  const hostPageURL = data.hostPageURL;

  browser.tabs.query({url: hostPageURL}).then(tabs => {
    tabs.forEach(tab => {

      // send message to correct content.js
      browser.tabs.sendMessage(tab.id, {
        action: "updateImages",
        data: data
      });
    });
  });
}

function updateImagesInSidebar(data) {
  // debug function to send all updates to sidebar

  if (typeof browser.sidebarAction !== 'undefined') {

    // pack and send
    browser.runtime.sendMessage({
      type: 'from-bg',
      query: data.query
    })
  } else {
    console.error('Sidebar action not supported in this browser');
  }
}

function handleMessageFromServer(data) {
  // function to validate and divert data from app.py

  // Check if all required fields are present
  if (data.hostPageURL) {
    
    // update images on page
    updateImageInTabs(data);
  } else if (data.query) {
    
    // append images to sidebar
    updateImagesInSidebar(data)
  } else {
    console.error('Data from server is missing required fields ' + data);
  }
}


function sendMessageToWebSocket(message) {
  // function to validate and send to app.py
  if (socket && socket.readyState === WebSocket.OPEN) {
    
    // send it
    socket.send(JSON.stringify(message));
  } else {
    console.error('WebSocket is not connected.');
  }
}


browser.runtime.onMessage.addListener((message) => {
  // listen for messages from other js pages

  if (message.type === 'to-bg') {
    if (message.query) {
      // handle if from sidebar
      console.log('📨 face.mbd');
      sendMessageToWebSocket(message);

      // handle if from content.js
    } else if (message.content) {
      console.log('content.js 📫');
      sendMessageToWebSocket(message);
    }
  }
});

establishWebSocketConnection(); // start socket
