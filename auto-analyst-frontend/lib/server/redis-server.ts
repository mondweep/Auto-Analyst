import { Redis } from '@upstash/redis';
import { KEYS } from '../redis';

// Check if we have valid Redis credentials
const hasRedisConfig = !!(
  process.env.UPSTASH_REDIS_REST_URL &&
  process.env.UPSTASH_REDIS_REST_TOKEN &&
  process.env.UPSTASH_REDIS_REST_URL.startsWith('https://') &&
  process.env.UPSTASH_REDIS_REST_TOKEN.length > 5
)

// Create mock methods for development without Redis
const mockRedis = {
  ping: async () => "PONG",
  hgetall: async () => ({}),
  hset: async () => "OK",
  del: async () => 1,
  get: async () => null,
  set: async () => "OK",
  incr: async () => 1
}

// Initialize Redis client or use mock
const serverRedis = hasRedisConfig
  ? new Redis({
      url: process.env.UPSTASH_REDIS_REST_URL || '',
      token: process.env.UPSTASH_REDIS_REST_TOKEN || '',
    })
  : mockRedis as unknown as Redis;

// Server-side only Redis operations
export const serverCreditUtils = {
  async getRemainingCredits(userId: string): Promise<number> {
    try {
      // Try getting from the hash first
      const creditsHash = await serverRedis.hgetall(KEYS.USER_CREDITS(userId));
      
      if (creditsHash && creditsHash.total) {
        const total = parseInt(creditsHash.total as string);
        const used = creditsHash.used ? parseInt(creditsHash.used as string) : 0;
        return total - used;
      }
      
      // Default for new users
      return 100;
    } catch (error) {
      console.error('Server Redis error fetching credits:', error);
      return 100; // Default fallback
    }
  }
};

// Test server-side Redis connection
export const testServerRedisConnection = async (): Promise<{
  success: boolean;
  message: string;
}> => {
  try {
    await serverRedis.ping();
    return { 
      success: true, 
      message: 'Server Redis connection successful' 
    };
  } catch (error) {
    console.error('Server Redis connection failed:', error);
    return { 
      success: false, 
      message: error instanceof Error ? error.message : 'Unknown error'
    };
  }
};

export default serverRedis; 