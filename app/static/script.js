// script.js
document.addEventListener('DOMContentLoaded', () => {
  const messageContainer = document.getElementById('chatbot-messages');
  const userInput = document.getElementById('user-input');
  const sendButton = document.getElementById('send-btn');
  const testingAssit = document.getElementById('test-asst');
  const xmlFileInput = document.getElementById('xml-file');
  // const xmlBlock = document.getElementsByClassName('xml-upload')[0];
  // xmlBlock.style.display = 'none';
  const uploadButton = document.getElementById('upload-btn');
  let testAssistance = false;
  const clearSessionButton = document.getElementById('clear-session');

  const modal = document.getElementById('uploadModal');
  const closeBtn = document.getElementsByClassName('close')[0];
  const submitUploadBtn = document.getElementById('submit-upload');

  // Function to add a message to the chat
  function addMessage(text, isUser, isLoader = false) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', isUser ? 'user' : 'bot');

    if (isLoader) {
      // Add loader inside the bot's message
      const loaderDiv = document.createElement('div');
      loaderDiv.classList.add('loader');
      messageDiv.appendChild(loaderDiv);
    } else {
      // Add regular message text
      const messageText = document.createElement('p');
      messageText.textContent = text;
      if (!isUser) {
        messageText.innerHTML = marked.parse(text);
      } else {
        messageText.textContent = text;
      }
      messageDiv.appendChild(messageText);
    }

    messageContainer.appendChild(messageDiv);
    messageContainer.scrollTop = messageContainer.scrollHeight; // Auto-scroll
  }

  // Function to simulate a bot response (replace with actual API call)
  function simulateBotResponse(userText) {
    return new Promise((resolve) => {
    
    fetch("/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: userText, testAssistance: testAssistance }),
    })
      .then((response) => response.json())
      .then((data) => {

        resolve(data.response);
      })
      .catch((error) => {
        console.error("Error:", error);
        resolve("Sorry, there was an error processing your request.");
      });
    });
  }

  // Function to handle user input
  async function handleUserInput() {
    const userText = userInput.value.trim();
    if (userText) {
      addMessage(userText, true); // Add user message
      userInput.value = ''; // Clear input field
      userInput.disabled = true;

      // Add loader as bot's message
      addMessage('', false, true);

      const botResponse = await simulateBotResponse(userText);

      // Remove the loader and add the bot's response
      messageContainer.lastChild.remove(); // Remove loader
      addMessage(botResponse, false); // Add bot response
      userInput.disabled = false;
      userInput.focus();
    }
  }

  async function enableTestAssistance() {
    testAssistance = !testAssistance;
    testingAssit.style.backgroundColor = testAssistance ? 'black' : 'grey';
    if (testAssistance)
      xmlBlock.style.display = 'flex';
    else
      xmlBlock.style.display = 'none';
  }

  // Event listeners
  sendButton.addEventListener('click', handleUserInput);
  userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      handleUserInput();
    }
  });
  testingAssit.addEventListener('click', enableTestAssistance);
  testingAssit.onmouseover = () => {
    testingAssit.style.backgroundColor = testAssistance ? '#393d41' : 'darkgrey';
  };
  testingAssit.onmouseout = () => {
    testingAssit.style.backgroundColor = testAssistance ? '#17191b' : 'grey';
  };

  uploadButton.addEventListener('click', () => {
    modal.style.display = 'block';
    console.log("Upload button clicked");
  });

  closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
  });

  window.addEventListener('click', (event) => {
    if (event.target === modal) {
      modal.style.display = 'none';
    }
  });

  submitUploadBtn.addEventListener('click', () => {
    const file = xmlFileInput.files[0];
    if (file) {
      const reader = new FileReader();
  
      reader.onload = async (event) => {
        const xmlData = event.target.result;
  
        try {
          const response = await fetch("/file", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ file: xmlData }),
          });
  
          const data = await response.json();
          console.log(data.response);
          if (data.response.includes("success")) {
            alert(`XML file uploaded successfully`);
            modal.style.display = 'none';
          } else {
            alert(data.response);
          }
        } catch (error) {
          console.error("Error:", error);
          alert("Sorry, please review your XML file, There was an error processing your file.");
        }
        modal.style.display = 'none';
      };
  
      reader.readAsText(file);
    } else {
      alert('Please select a XML file to upload.');
    }
  });

});