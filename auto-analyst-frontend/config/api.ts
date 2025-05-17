// API URLs and configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const PREVIEW_API_URL = process.env.NEXT_PUBLIC_PREVIEW_API_URL || 'http://localhost:8000';
const UPLOAD_API_URL = process.env.NEXT_PUBLIC_UPLOAD_API_URL || 'http://localhost:8001';
const AUTOMOTIVE_API_URL = process.env.NEXT_PUBLIC_AUTOMOTIVE_API_URL || 'http://localhost:8003';

export { 
  API_URL as default,
  PREVIEW_API_URL,
  UPLOAD_API_URL,
  AUTOMOTIVE_API_URL
}; 