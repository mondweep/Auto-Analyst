// CommonJS-compatible API config for Node.js tests
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
const UPLOAD_API_URL = process.env.NEXT_PUBLIC_UPLOAD_API_URL || 'http://localhost:8001';
const AUTOMOTIVE_API_URL = process.env.NEXT_PUBLIC_AUTOMOTIVE_API_URL || 'http://localhost:8080';
const FILE_SERVER_URL = process.env.NEXT_PUBLIC_FILE_SERVER_URL || 'http://localhost:8001';

module.exports = {
  API_URL,
  UPLOAD_API_URL,
  AUTOMOTIVE_API_URL,
  FILE_SERVER_URL
}; 