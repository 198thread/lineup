let socket;

function establishWebSocketConnection() {
  // Establishing connection on the specified port 2882
  socket = new WebSocket('ws://localhost:2882');

  socket.onopen = function() {
    console.log('WebSocket connected at localhost:2882');
    // The WebSocket is now ready to send and receive messages
  };

  socket.onmessage = function(event) {
    // Handle any message from the WebSocket server
    console.log('app.py 📫');

    // Check if the data is in JSON format
    try {
      let jdata = JSON.parse(event.data);


      handleMessageFromServer(jdata);

    } catch (error) {
      console.error('Error parsing JSON:', error);
      console.log(event.data)
      return; // Exit the function if parsing fails
    }

  };

  socket.onerror = function(error) {
    console.error('WebSocket Error:', error);
  };

  socket.onclose = function(event) {
    if (!event.wasClean) {
      console.error(`WebSocket Error: [code ${event.code}] ${event.reason}`);
    }
    console.log('WebSocket connection closed. Trying to reconnect...');
    setTimeout(establishWebSocketConnection, 5000); // Reconnect every 5 seconds if the connection was not closed cleanly
  };
}


function updateImageInTabs(data) {
  const hostPageURL = data.hostPageURL;

  browser.tabs.query({url: hostPageURL}).then(tabs => {
    tabs.forEach(tab => {
      // Sending message to content script
      browser.tabs.sendMessage(tab.id, {
        action: "updateImages",
        data: data
      });
    });
  });
}

function updateImagesInSidebar(data) {

  if (typeof browser.sidebarAction !== 'undefined') {
    browser.runtime.sendMessage({
      type: 'from-bg',
      query: data.query
    })
  } else {
    console.error('Sidebar action not supported in this browser');
  }
}

function handleMessageFromServer(data) {
  
  // Check if all required fields are present
  if (data.hostPageURL) {
  // if (data && data.hostPageURL && data.imageDirectURL && data.imageData) {
    updateImageInTabs(data);
  } else if (data.query) {
    updateImagesInSidebar(data)
  } else {
    console.error('Data from server is missing required fields ' + data);
  }
}


// Function to send messages to the WebSocket server
function sendMessageToWebSocket(message) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
  } else {
    console.error('WebSocket is not connected.');
  }
}


// Listen for messages from content scripts
browser.runtime.onMessage.addListener((message) => {
  if (message.type === 'to-bg') {
    if (message.query) {
      console.log('📨 face.mbd');
      sendMessageToWebSocket(message);
    } else if (message.content) {
      console.log('content.js 📫');
      sendMessageToWebSocket(message);
    }
  }
});

establishWebSocketConnection();