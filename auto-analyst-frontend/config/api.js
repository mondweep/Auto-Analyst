// Define API URLs
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
export const AUTOMOTIVE_API_URL = process.env.NEXT_PUBLIC_AUTOMOTIVE_API_URL || 'http://localhost:8080';
export const FILE_SERVER_URL = process.env.NEXT_PUBLIC_FILE_SERVER_URL || 'http://localhost:8001';
export const UPLOAD_API_URL = process.env.NEXT_PUBLIC_UPLOAD_API_URL || 'http://localhost:8001';

export default API_URL; 