/**
 * Chat Interface Tester - This script helps automate testing of the chat interface
 * Run this script in the browser console when on the chat page
 */

/**
 * Configuration
 */
const TEST_CONFIG = {
  BASE_URL: window.location.origin,
  CHAT_PATH: '/chat',
  WAIT_TIME: 5000, // Time to wait between actions in ms
  TEST_QUESTIONS: [
    {
      id: 'test-basic-question',
      question: 'What vehicles are in the inventory?',
      expectedKeywords: ['Toyota', 'Camry', 'Honda', 'Civic', 'Ford', 'F-150', 'inventory']
    },
    {
      id: 'test-market-analysis',
      question: 'Analyze the market data and tell me which vehicles are priced below market value',
      expectedKeywords: ['Toyota', 'Camry', 'Honda', 'Civic', 'below market', 'price difference', 'percent']
    },
    {
      id: 'test-complex-reasoning',
      question: 'Based on the inventory and market data, which vehicle would be the best one to promote in a sale to maximize profit?',
      expectedKeywords: ['profit', 'market', 'price', 'recommend', 'sale', 'maximize']
    }
  ]
};

/**
 * Test Runner
 */
class ChatTester {
  constructor(config) {
    this.config = config;
    this.results = {
      testsRun: 0,
      testsPassed: 0,
      testsFailed: 0,
      details: []
    };
    this.currentTestIndex = 0;
  }

  /**
   * Start testing
   */
  async start() {
    console.log('%c📋 Starting Chat Interface Tests...', 'font-size: 14px; font-weight: bold; color: blue;');
    
    // Check if we're on the chat page
    if (!window.location.pathname.includes(this.config.CHAT_PATH)) {
      console.error(`❌ Not on chat page! Navigate to ${this.config.BASE_URL}${this.config.CHAT_PATH} first`);
      return;
    }
    
    await this.testInterfaceLoaded();
    await this.runAllQuestions();
    
    this.reportResults();
  }
  
  /**
   * Test if the chat interface loaded correctly
   */
  async testInterfaceLoaded() {
    console.log('%c🔍 Test Case 1: Checking if chat interface loaded correctly...', 'color: purple;');
    
    const inputField = document.querySelector('textarea[placeholder^="Ask a question"]');
    const chatContainer = document.querySelector('.chat-container') || document.querySelector('[class*="chat"]');
    
    const passed = !!(inputField && chatContainer);
    
    this.recordResult('interface-loaded', 'Chat Interface Loads Properly', passed, {
      details: passed ? 
        'Found input field and chat container' : 
        'Could not find input field or chat container'
    });
    
    if (passed) {
      console.log('%c✅ Chat interface loaded successfully', 'color: green;');
    } else {
      console.error('%c❌ Chat interface not loaded correctly', 'color: red;');
    }
    
    return passed;
  }
  
  /**
   * Run all questions
   */
  async runAllQuestions() {
    for (const testCase of this.config.TEST_QUESTIONS) {
      await this.sendQuestionAndCheck(testCase);
      
      // Wait between questions
      await this.wait(this.config.WAIT_TIME);
    }
  }
  
  /**
   * Send a question and check the response
   */
  async sendQuestionAndCheck(testCase) {
    console.log(`%c🔍 Testing question: "${testCase.question}"`, 'color: purple;');
    
    const inputField = document.querySelector('textarea[placeholder^="Ask a question"]');
    const sendButton = document.querySelector('button[type="submit"]') || 
                      document.querySelector('button[aria-label="Send message"]') ||
                      inputField.closest('form').querySelector('button');
    
    if (!inputField || !sendButton) {
      console.error('❌ Could not find input field or send button');
      this.recordResult(testCase.id, `Question: ${testCase.question.substring(0, 20)}...`, false, {
        details: 'Could not find input field or send button'
      });
      return false;
    }
    
    // Count messages before sending
    const messageCountBefore = document.querySelectorAll('[class*="message"]').length;
    
    // Type the question
    inputField.value = testCase.question;
    inputField.dispatchEvent(new Event('input', { bubbles: true }));
    
    // Click send button
    sendButton.click();
    
    // Wait for response (look for loading indicator disappearing)
    console.log('⏳ Waiting for response...');
    
    // Maximum wait time is 30 seconds
    let waited = 0;
    const checkInterval = 500; // Check every 500ms
    const maxWait = 30000; // 30 seconds
    
    while (waited < maxWait) {
      await this.wait(checkInterval);
      waited += checkInterval;
      
      const isLoading = document.querySelector('[class*="loading"]') || 
                       document.querySelector('[aria-label*="loading"]') ||
                       sendButton.disabled;
      
      const messageCountAfter = document.querySelectorAll('[class*="message"]').length;
      
      // If no longer loading and we have a new message, we got a response
      if (!isLoading && messageCountAfter > messageCountBefore) {
        console.log('✅ Received response');
        break;
      }
      
      if (waited >= maxWait) {
        console.error('❌ Timed out waiting for response');
        this.recordResult(testCase.id, `Question: ${testCase.question.substring(0, 20)}...`, false, {
          details: 'Timed out waiting for response'
        });
        return false;
      }
    }
    
    // Get the latest message content (AI response)
    const messages = document.querySelectorAll('[class*="message"]');
    const latestMessage = messages[messages.length - 1];
    
    if (!latestMessage) {
      console.error('❌ Could not find response message');
      this.recordResult(testCase.id, `Question: ${testCase.question.substring(0, 20)}...`, false, {
        details: 'Could not find response message'
      });
      return false;
    }
    
    const responseText = latestMessage.textContent;
    console.log(`📝 Response: ${responseText.substring(0, 100)}...`);
    
    // Check if the response contains expected keywords
    const keywordsFound = testCase.expectedKeywords.filter(keyword => 
      responseText.toLowerCase().includes(keyword.toLowerCase())
    );
    
    const passed = keywordsFound.length > 0;
    const percentage = Math.round((keywordsFound.length / testCase.expectedKeywords.length) * 100);
    
    this.recordResult(testCase.id, `Question: ${testCase.question.substring(0, 20)}...`, passed, {
      details: passed ? 
        `Found ${keywordsFound.length}/${testCase.expectedKeywords.length} expected keywords (${percentage}%)` : 
        'Response did not contain any expected keywords',
      keywordsFound,
      keywordsMissing: testCase.expectedKeywords.filter(kw => !keywordsFound.includes(kw)),
      responseText: responseText.substring(0, 500) // Truncate long responses
    });
    
    if (passed) {
      console.log(`%c✅ Response contains ${keywordsFound.length}/${testCase.expectedKeywords.length} expected keywords (${percentage}%)`, 'color: green;');
    } else {
      console.error(`%c❌ Response does not contain expected keywords`, 'color: red;');
    }
    
    return passed;
  }
  
  /**
   * Record test result
   */
  recordResult(id, name, passed, details = {}) {
    this.results.testsRun++;
    
    if (passed) {
      this.results.testsPassed++;
    } else {
      this.results.testsFailed++;
    }
    
    this.results.details.push({
      id,
      name,
      passed,
      ...details,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Report test results
   */
  reportResults() {
    console.log('\n');
    console.log('%c📊 Chat Interface Test Results', 'font-size: 16px; font-weight: bold; color: blue;');
    console.log(`Tests Run: ${this.results.testsRun}`);
    console.log(`%c✅ Tests Passed: ${this.results.testsPassed}`, 'color: green;');
    console.log(`%c❌ Tests Failed: ${this.results.testsFailed}`, 'color: red;');
    console.log('\nDetailed Results:');
    
    this.results.details.forEach(result => {
      console.log(`${result.passed ? '✅' : '❌'} ${result.name}`);
      
      if (!result.passed) {
        console.log(`   Details: ${result.details}`);
      }
    });
    
    console.log('\n');
    console.log('%cTo download test results as JSON, run:', 'font-style: italic;');
    console.log('chatTester.downloadResults()');
  }
  
  /**
   * Helper to wait for specified milliseconds
   */
  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  /**
   * Download test results as JSON
   */
  downloadResults() {
    const resultsJson = JSON.stringify(this.results, null, 2);
    const blob = new Blob([resultsJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-test-results-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    
    URL.revokeObjectURL(url);
  }
}

// Create global instance for easy console access
window.chatTester = new ChatTester(TEST_CONFIG);

console.log('%c📋 Chat Tester loaded!', 'font-size: 14px; font-weight: bold; color: blue;');
console.log('To start tests, run: chatTester.start()'); 