/**
 * Gemini Chat API Test
 * 
 * This script tests the Gemini chat API functionality by sending a direct request
 * with automotive data from our demo files.
 */

(function() {
    console.log('🔍 Starting Gemini Chat API Test...');
    
    // Test data from our demo files
    const testData = {
        vehicles: [
            { id: 1, make: 'Toyota', model: 'Camry', year: 2021, price: 28500, mileage: 32000, condition: 'Excellent' },
            { id: 2, make: 'Honda', model: 'Civic', year: 2022, price: 24700, mileage: 18000, condition: 'Good' },
            { id: 3, make: 'Ford', model: 'F-150', year: 2020, price: 38900, mileage: 45000, condition: 'Good' }
        ],
        marketData: [
            { id: 1, make: 'Toyota', model: 'Camry', year: 2021, your_price: 28500, market_price: 30200, price_difference: -1700 },
            { id: 2, make: 'Honda', model: 'Civic', year: 2022, your_price: 24700, market_price: 25900, price_difference: -1200 },
            { id: 3, make: 'Ford', model: 'F-150', year: 2020, your_price: 38900, market_price: 36700, price_difference: 2200 }
        ]
    };
    
    const testQuestions = [
        {
            question: 'What vehicles are in our inventory?',
            data: testData.vehicles
        },
        {
            question: 'Which vehicles are priced below market value?',
            data: testData.marketData
        },
        {
            question: 'Analyze our vehicle pricing strategy and suggest improvements.',
            data: { vehicles: testData.vehicles, marketData: testData.marketData }
        }
    ];
    
    // Create a test UI element to show results
    function createTestUI() {
        if (document.getElementById('gemini-test-container')) {
            return;
        }
        
        const container = document.createElement('div');
        container.id = 'gemini-test-container';
        container.style.position = 'fixed';
        container.style.top = '10px';
        container.style.right = '10px';
        container.style.width = '400px';
        container.style.padding = '15px';
        container.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
        container.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.2)';
        container.style.borderRadius = '5px';
        container.style.zIndex = '9999';
        container.style.maxHeight = '80vh';
        container.style.overflowY = 'auto';
        
        const heading = document.createElement('h2');
        heading.textContent = 'Gemini Chat API Test';
        heading.style.color = '#333';
        container.appendChild(heading);
        
        const results = document.createElement('div');
        results.id = 'gemini-test-results';
        container.appendChild(results);
        
        const runButton = document.createElement('button');
        runButton.textContent = 'Run Tests';
        runButton.style.marginTop = '10px';
        runButton.style.padding = '8px 16px';
        runButton.style.backgroundColor = '#4CAF50';
        runButton.style.color = 'white';
        runButton.style.border = 'none';
        runButton.style.borderRadius = '4px';
        runButton.style.cursor = 'pointer';
        runButton.onclick = runTests;
        container.appendChild(runButton);
        
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.style.marginTop = '10px';
        closeButton.style.marginLeft = '10px';
        closeButton.style.padding = '8px 16px';
        closeButton.style.backgroundColor = '#f44336';
        closeButton.style.color = 'white';
        closeButton.style.border = 'none';
        closeButton.style.borderRadius = '4px';
        closeButton.style.cursor = 'pointer';
        closeButton.onclick = () => container.remove();
        container.appendChild(closeButton);
        
        document.body.appendChild(container);
    }
    
    // Add a log entry to the test UI
    function logTestResult(message, isSuccess = true) {
        const results = document.getElementById('gemini-test-results');
        const entry = document.createElement('div');
        entry.style.margin = '10px 0';
        entry.style.padding = '10px';
        entry.style.backgroundColor = isSuccess ? 'rgba(76, 175, 80, 0.1)' : 'rgba(244, 67, 54, 0.1)';
        entry.style.border = `1px solid ${isSuccess ? '#4CAF50' : '#f44336'}`;
        entry.style.borderRadius = '4px';
        
        entry.innerHTML = message;
        results.appendChild(entry);
    }
    
    // Send a test question to the chat interface
    async function sendTestQuestion(question, data) {
        try {
            logTestResult(`🔄 Testing: "${question}"`, true);
            
            // Get the chat input field and send button
            const inputField = document.querySelector('textarea[placeholder="Ask a question..."]');
            const sendButton = document.querySelector('button[aria-label="Send message"]');
            
            if (!inputField || !sendButton) {
                logTestResult('❌ Chat interface elements not found. Are you on the chat page?', false);
                return;
            }
            
            // Clear any previous input
            inputField.value = '';
            
            // Combine the question with the data 
            const contextualQuestion = `Please analyze this automotive data and ${question}\n\nHere's the data:\n${JSON.stringify(data, null, 2)}`;
            
            // Set the input value
            inputField.value = contextualQuestion;
            
            // Dispatch events to simulate typing
            inputField.dispatchEvent(new Event('input', { bubbles: true }));
            
            // Click the send button
            sendButton.click();
            
            logTestResult(`✅ Question sent: "${question}"`, true);
            
            // Return a promise that resolves when a response is received
            return new Promise((resolve) => {
                const checkForResponse = setInterval(() => {
                    const responseElements = document.querySelectorAll('.chat-message.assistant');
                    const lastResponse = responseElements[responseElements.length - 1];
                    
                    if (lastResponse && lastResponse.textContent.trim().length > 0) {
                        clearInterval(checkForResponse);
                        logTestResult(`✅ Response received for: "${question}"`, true);
                        resolve(lastResponse.textContent);
                    }
                }, 1000);
                
                // Timeout after 30 seconds
                setTimeout(() => {
                    clearInterval(checkForResponse);
                    logTestResult(`❌ Timeout waiting for response to: "${question}"`, false);
                    resolve(null);
                }, 30000);
            });
        } catch (error) {
            logTestResult(`❌ Error: ${error.message}`, false);
            return null;
        }
    }
    
    // Run all tests
    async function runTests() {
        const results = document.getElementById('gemini-test-results');
        results.innerHTML = ''; // Clear previous results
        
        logTestResult('🚀 Starting tests...', true);
        
        for (const test of testQuestions) {
            const response = await sendTestQuestion(test.question, test.data);
            
            if (response) {
                logTestResult(`
                    <strong>Question:</strong> ${test.question}<br>
                    <strong>Response:</strong> ${response.slice(0, 200)}${response.length > 200 ? '...' : ''}
                `, true);
            }
            
            // Wait a bit between tests
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
        
        logTestResult('✅ All tests complete!', true);
    }
    
    // Initialize
    createTestUI();
    console.log('🔍 Gemini Chat API Test ready. Click "Run Tests" to start.');
})(); 