# Auto-Analyst Chat Interface Testing

This directory contains tools for testing the chat interface in the Auto-Analyst application using a Test-Driven Development (TDD) approach.

## Test Files

- `ChatInterface.test.js` - Manual test cases for the chat interface
- `chatTester.js` - JavaScript test runner that can be executed in the browser console
- `chat-tester.html` - HTML page with instructions and test cases

## Testing the Chat Interface

### Prerequisites

1. Start the backend services:
   ```
   cd Auto-Analyst/auto-analyst-backend
   python file_server.py  # Starts on port 8001
   ```

   In a new terminal:
   ```
   cd Auto-Analyst/auto-analyst-backend
   python automotive_server.py  # Starts on port 8003
   ```

2. Start the frontend application:
   ```
   cd Auto-Analyst/auto-analyst-frontend
   npm run dev  # Starts on port 3000 (or next available port)
   ```

### Running Tests

#### Automated Testing

1. Open the Auto-Analyst chat interface in your browser (typically http://localhost:3000/chat)
2. Open your browser's developer console (F12 or right-click > Inspect > Console)
3. Copy the entire content of `chatTester.js` and paste it into the console
4. Run the tests by typing:
   ```javascript
   chatTester.start()
   ```
5. Wait for the tests to complete and view the results in the console

#### Manual Testing

1. Open `chat-tester.html` in your browser
2. Follow the setup instructions
3. Use the provided test questions to manually test the chat interface
4. Copy questions from the manual testing section to test specific scenarios

## Test Cases

1. **Chat Interface Loads Properly**
   - Verify chat interface loads with all components

2. **Basic Question and Response**
   - Test basic questions about inventory data
   - Example: "What vehicles are in the inventory?"

3. **Model Provider Settings**
   - Verify Gemini model is working correctly
   - Test with complex reasoning questions

4. **Data Analysis Questions**
   - Test data analysis capabilities
   - Example: "Analyze the market data and tell me which vehicles are priced below market value"

5. **Fallback Behavior**
   - Test application behavior when backend services are unavailable

6. **No Free Trial Overlay**
   - Verify no "Ready to unlock full access?" overlay appears

## Expected Behavior

- Chat interface should load without errors
- Questions should receive appropriate responses
- Responses should reference data from CSV files when applicable
- Complex questions should demonstrate the Gemini model's reasoning capabilities
- No API key or authentication issues should appear

## Troubleshooting

- If responses are slow, ensure backend services are running properly
- If the model isn't responding, check that Gemini is properly configured in the codebase
- If the app displays "Ready to unlock full access?", the free trial bypass needs to be fixed

## Adding New Tests

Edit `chatTester.js` and add new test cases to the `TEST_CONFIG.TEST_QUESTIONS` array. Each test should include:

```javascript
{
  id: 'test-id',
  question: 'Your test question',
  expectedKeywords: ['keyword1', 'keyword2']
}
``` 