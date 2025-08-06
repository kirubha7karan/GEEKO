// script.js
document.addEventListener('DOMContentLoaded', () => {
  // Add Batman startup animation
  const container = document.querySelector('.chatbot-container');
  
  // Add loaded class after startup animation
  setTimeout(() => {
    container.classList.add('loaded');
  }, 3000);

  // Add welcome message with Batman flair
  setTimeout(() => {
    addMessage("Welcome! How may I assist you today?", false);
  }, 4000);

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

  // Function to detect and format JSON
  function formatJSON(text) {
    try {
      // Try to parse as JSON
      const parsed = JSON.parse(text);
      return `<div class="json-block"><pre><code>${JSON.stringify(parsed, null, 2)}</code></pre></div>`;
    } catch (e) {
      return null;
    }
  }

  // Function to detect JSON blocks within text and format them
  function formatMixedContent(text) {
    // Look for JSON blocks in the text (enclosed in backticks or standalone)
    const jsonBlockRegex = /```json\s*([\s\S]*?)\s*```|```\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```/g;
    
    // More aggressive JSON detection for large JSON objects
    const standaloneJsonRegex = /(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})/g;
    
    let formattedText = text;
    
    // First handle code blocks with JSON
    formattedText = formattedText.replace(jsonBlockRegex, (match, jsonContent1, jsonContent2) => {
      const jsonContent = jsonContent1 || jsonContent2;
      try {
        const parsed = JSON.parse(jsonContent.trim());
        return `<div class="json-block"><pre><code>${JSON.stringify(parsed, null, 2)}</code></pre></div>`;
      } catch (e) {
        return match; // Return original if not valid JSON
      }
    });
    
    // Handle large JSON objects that span multiple lines (like tool outputs)
    formattedText = formattedText.replace(standaloneJsonRegex, (match) => {
      // Only format if it looks like a substantial JSON object
      if (match.length > 30 && match.includes('"') && match.includes(':')) {
        try {
          const parsed = JSON.parse(match);
          // Only format if it's a complex object (not just a simple string)
          if (typeof parsed === 'object' && parsed !== null) {
            return `<div class="json-block"><pre><code>${JSON.stringify(parsed, null, 2)}</code></pre></div>`;
          }
        } catch (e) {
          // If JSON parsing fails, still try to format it nicely
          return `<div class="json-block"><pre><code>${match}</code></pre></div>`;
        }
      }
      return match;
    });
    
    // Special handling for tool outputs that might not be properly enclosed
    if (text.includes('tool_outputs') || text.includes('"type"') || text.includes('"function"')) {
      // Try to parse the entire text as JSON if it starts with { and ends with }
      const trimmed = text.trim();
      if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
        try {
          const parsed = JSON.parse(trimmed);
          return `<div class="json-block"><pre><code>${JSON.stringify(parsed, null, 2)}</code></pre></div>`;
        } catch (e) {
          // If parsing fails, at least format it as code
          return `<div class="json-block"><pre><code>${trimmed}</code></pre></div>`;
        }
      }
    }
    
    return formattedText;
  }

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
      // Create message content container
      const messageContent = document.createElement('div');
      messageContent.classList.add('message-content');
      
      if (isUser) {
        // For user messages, preserve line breaks naturally with CSS white-space: pre-wrap
        const messageText = document.createElement('p');
        messageText.textContent = text; // This preserves line breaks with white-space: pre-wrap
        messageContent.appendChild(messageText);
      } else {
        // For bot messages, handle different content types
        
        // Check if entire message is JSON
        const jsonFormatted = formatJSON(text.trim());
        if (jsonFormatted) {
          messageContent.innerHTML = jsonFormatted;
        } else {
          // First handle mixed JSON content before markdown processing
          const processedText = formatMixedContent(text);
          
          // If the processed text contains JSON blocks, don't apply markdown
          if (processedText.includes('<pre class="json-block">')) {
            messageContent.innerHTML = processedText;
          } else {
            // Configure marked options for better rendering
            marked.setOptions({
              breaks: true, // Convert \n to <br>
              gfm: true, // GitHub Flavored Markdown
              sanitize: false, // Allow HTML (be careful in production)
              pedantic: false, // Don't conform to obscure parts of markdown.pl
              smartLists: true, // Use smarter list behavior
              highlight: function(code, lang) {
                // Basic syntax highlighting for code blocks
                if (lang === 'json') {
                  try {
                    const parsed = JSON.parse(code);
                    return JSON.stringify(parsed, null, 2);
                  } catch (e) {
                    return code;
                  }
                }
                return code;
              }
            });
            
            // Parse markdown and handle it properly
            let parsedContent = marked.parse(processedText);
            
            // Post-process to fix specific formatting issues
            parsedContent = parsedContent
              // Ensure proper line breaks in lists
              .replace(/<li>/g, '<li>')
              .replace(/<\/li>/g, '</li>')
              // Fix summary and description highlighting
              .replace(/\*\*(Summary|Description):\*\*/g, '<strong style="color: #FFD700;">$1:</strong>')
              .replace(/\*(Summary|Description):\*/g, '<strong style="color: #FFD700;">$1:</strong>')
              // Highlight steps and reproduce sections
              .replace(/\*\*(Step to Reproduce|Expected Result|Actual Result|Bug Proof):\*\*/g, '<strong style="color: #FFD700;">$1:</strong>')
              .replace(/\*(Step to Reproduce|Expected Result|Actual Result|Bug Proof):\*/g, '<strong style="color: #FFD700;">$1:</strong>');
            
            messageContent.innerHTML = parsedContent;
          }
        }
      }
      
      messageDiv.appendChild(messageContent);
    }

    messageContainer.appendChild(messageDiv);
    
    // Smooth scroll to bottom with animation
    messageContainer.scrollTo({
      top: messageContainer.scrollHeight,
      behavior: 'smooth'
    });
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
      // Add visual feedback to send button
      sendButton.style.transform = 'scale(0.95)';
      setTimeout(() => {
        sendButton.style.transform = 'scale(1)';
      }, 150);
      
      addMessage(userText, true); // Add user message
      userInput.value = ''; // Clear input field
      autoResizeTextarea(); // Reset textarea height
      userInput.disabled = true;
      sendButton.disabled = true;

      // Add loader as bot's message
      addMessage('', false, true);

      const botResponse = await simulateBotResponse(userText);

      // Remove the loader and add the bot's response
      messageContainer.lastChild.remove(); // Remove loader
      addMessage(botResponse, false); // Add bot response
      userInput.disabled = false;
      sendButton.disabled = false;
      userInput.focus();
    }
  }

  async function enableTestAssistance() {
    testAssistance = !testAssistance;
    
    // Add visual feedback with animation
    testingAssit.style.transform = 'scale(0.95)';
    setTimeout(() => {
      testingAssit.style.transform = 'scale(1)';
    }, 150);
    
    // Update background with transition
    testingAssit.style.background = testAssistance 
      ? 'linear-gradient(135deg, #6c757d 0%, #495057 100%)' 
      : 'linear-gradient(135deg, #6c757d 0%, #495057 100%)';
    testingAssit.style.opacity = testAssistance ? '1' : '0.7';
    
    if (testAssistance) {
      // Add visual indicator that RAG mode is active
      testingAssit.textContent = 'RAG Mode ✓';
      testingAssit.classList.add('active');
    } else {
      testingAssit.textContent = 'RAG Mode';
      testingAssit.classList.remove('active');
    }
  }

  // Function to auto-resize textarea
  function autoResizeTextarea() {
    userInput.style.height = 'auto'; // Reset height to auto
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px'; // Set height to content, max 120px
  }

  // Event listeners
  sendButton.addEventListener('click', handleUserInput);
  
  // Updated keyboard handling for textarea (Shift+Enter for new line, Enter to send)
  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent default new line
      handleUserInput();
    }
  });
  
  // Auto-resize textarea as user types
  userInput.addEventListener('input', autoResizeTextarea);
  
  // Initial resize to fit content
  autoResizeTextarea();
  testingAssit.addEventListener('click', enableTestAssistance);
  
  // Remove old hover event listeners as we now use CSS for hover effects
  testingAssit.onmouseover = null;
  testingAssit.onmouseout = null;

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