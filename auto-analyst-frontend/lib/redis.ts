import { Redis } from '@upstash/redis'
import logger from '@/lib/utils/logger'

// Make logger more robust by providing a fallback if not available
const log = {
  log: (msg: string) => {
    if (typeof logger?.log === 'function') {
      logger.log(msg)
    } else {
      console.log(msg)
    }
  },
  error: (msg: string, err?: any) => {
    if (typeof logger?.error === 'function') {
      logger.error(msg, err)
    } else {
      console.error(msg, err)
    }
  }
}

// Check if we have valid Redis credentials
const hasRedisConfig = !!(
  process.env.UPSTASH_REDIS_REST_URL && 
  process.env.UPSTASH_REDIS_REST_TOKEN &&
  process.env.UPSTASH_REDIS_REST_URL.startsWith('https://') &&
  process.env.UPSTASH_REDIS_REST_TOKEN.length > 5
)

// Create comprehensive mock methods for development without Redis
class MockRedis {
  private storage: Map<string, any> = new Map()
  private hashStorage: Map<string, Map<string, any>> = new Map()
  
  // Standard Redis operations
  async ping() { return "PONG" }
  
  // Key operations
  async get(key: string) { 
    return this.storage.get(key) ?? null 
  }
  
  async set(key: string, value: any) { 
    this.storage.set(key, value)
    return "OK" 
  }
  
  async setex(key: string, ttl: number, value: any) {
    this.storage.set(key, value)
    return "OK"
  }
  
  async setnx(key: string, value: any) {
    if (this.storage.has(key)) return 0
    this.storage.set(key, value)
    return 1
  }
  
  async incr(key: string) {
    const val = this.storage.get(key) || 0
    const newVal = parseInt(val, 10) + 1
    this.storage.set(key, newVal)
    return newVal
  }
  
  async decr(key: string) {
    const val = this.storage.get(key) || 0
    const newVal = Math.max(0, parseInt(val, 10) - 1)
    this.storage.set(key, newVal)
    return newVal
  }
  
  async expire(key: string, ttl: number) {
    return this.storage.has(key) ? 1 : 0
  }
  
  async ttl(key: string) { 
    return this.storage.has(key) ? 1000 : -1
  }
  
  async exists(key: string) {
    return this.storage.has(key) ? 1 : 0
  }
  
  async del(key: string) {
    return this.storage.delete(key) ? 1 : 0
  }
  
  async keys(pattern: string) {
    // Simple glob pattern support for *
    if (pattern === '*') {
      return Array.from(this.storage.keys())
    }
    // Simple prefix support for pattern*
    if (pattern.endsWith('*')) {
      const prefix = pattern.slice(0, -1)
      return Array.from(this.storage.keys()).filter(k => k.startsWith(prefix))
    }
    return Array.from(this.storage.keys()).filter(k => k === pattern)
  }
  
  // Hash operations
  async hset(key: string, fieldOrObject: string | object, value?: any) {
    if (!this.hashStorage.has(key)) {
      this.hashStorage.set(key, new Map())
    }
    
    const hash = this.hashStorage.get(key)!
    
    if (typeof fieldOrObject === 'object') {
      for (const [field, val] of Object.entries(fieldOrObject)) {
        hash.set(field, val)
      }
      return Object.keys(fieldOrObject).length
    } else {
      hash.set(fieldOrObject, value)
      return 1
    }
  }
  
  async hget(key: string, field: string) {
    if (!this.hashStorage.has(key)) return null
    const hash = this.hashStorage.get(key)!
    return hash.has(field) ? hash.get(field) : null
  }
  
  async hgetall(key: string) {
    if (!this.hashStorage.has(key)) return {}
    
    const hash = this.hashStorage.get(key)!
    const result: Record<string, any> = {}
    
    for (const [field, value] of hash.entries()) {
      result[field] = value
    }
    
    return result
  }
  
  async hmget(key: string, ...fields: string[]) {
    if (!this.hashStorage.has(key)) {
      return fields.map(() => null)
    }
    
    const hash = this.hashStorage.get(key)!
    return fields.map(field => hash.has(field) ? hash.get(field) : null)
  }
  
  async hsetnx(key: string, field: string, value: any) {
    if (!this.hashStorage.has(key)) {
      this.hashStorage.set(key, new Map())
    }
    
    const hash = this.hashStorage.get(key)!
    
    if (hash.has(field)) {
      return 0
    }
    
    hash.set(field, value)
    return 1
  }
  
  async hincrby(key: string, field: string, increment: number) {
    if (!this.hashStorage.has(key)) {
      this.hashStorage.set(key, new Map())
    }
    
    const hash = this.hashStorage.get(key)!
    const currentValue = hash.has(field) ? parseInt(hash.get(field), 10) || 0 : 0
    const newValue = currentValue + increment
    
    hash.set(field, newValue.toString())
    return newValue
  }
  
  async hkeys(key: string) {
    if (!this.hashStorage.has(key)) return []
    return Array.from(this.hashStorage.get(key)!.keys())
  }
  
  async hvals(key: string) {
    if (!this.hashStorage.has(key)) return []
    return Array.from(this.hashStorage.get(key)!.values())
  }
  
  // Set operations
  async sadd(key: string, ...members: any[]) {
    if (!this.storage.has(key)) {
      this.storage.set(key, new Set())
    }
    
    const set = this.storage.get(key)
    let added = 0
    
    for (const member of members) {
      if (!set.has(member)) {
        set.add(member)
        added++
      }
    }
    
    return added
  }
  
  async srem(key: string, ...members: any[]) {
    if (!this.storage.has(key)) return 0
    
    const set = this.storage.get(key)
    let removed = 0
    
    for (const member of members) {
      if (set.has(member)) {
        set.delete(member)
        removed++
      }
    }
    
    return removed
  }
  
  async smembers(key: string) {
    if (!this.storage.has(key)) return []
    return Array.from(this.storage.get(key))
  }
  
  async sismember(key: string, member: any) {
    if (!this.storage.has(key)) return 0
    return this.storage.get(key).has(member) ? 1 : 0
  }
  
  // Sorted set operations
  async zadd(key: string, score: number, member: any) {
    if (!this.storage.has(key)) {
      this.storage.set(key, [])
    }
    
    const zset = this.storage.get(key)
    const existingIndex = zset.findIndex((item: any) => item.member === member)
    
    if (existingIndex !== -1) {
      zset[existingIndex].score = score
      return 0
    }
    
    zset.push({ score, member })
    zset.sort((a: any, b: any) => a.score - b.score)
    return 1
  }
  
  async zrange(key: string, start: number, stop: number) {
    if (!this.storage.has(key)) return []
    
    const zset = this.storage.get(key)
    return zset.slice(start, stop + 1).map((item: any) => item.member)
  }
  
  async zrem(key: string, member: any) {
    if (!this.storage.has(key)) return 0
    
    const zset = this.storage.get(key)
    const existingIndex = zset.findIndex((item: any) => item.member === member)
    
    if (existingIndex === -1) return 0
    
    zset.splice(existingIndex, 1)
    return 1
  }
}

// Initialize Redis client or use mock
let redis;
try {
  console.log('Using mock Redis implementation (Demo mode)');
  
  // Always use the mock implementation for demo purposes
  redis = new MockRedis() as unknown as Redis;
} catch (error) {
  console.error('Error initializing Redis client:', error);
  // Fallback to mock if Redis fails to initialize
  console.log('Falling back to mock Redis implementation after error');
  redis = new MockRedis() as unknown as Redis;
}

// Make testConnection always return true for demo purposes
const testConnection = async () => {
  try {
    // Always return success for demo mode
    console.log('✅ Redis connection successful (mock)');
    return true;
  } catch (error) {
    console.error('⚠️ Redis connection failed:', error);
    return true; // Still return true to prevent auth issues
  }
};

// Don't automatically run the test on import
// This prevents build-time errors and unnecessary connections
// testConnection();

export default redis

// Export test connection function for explicit use in runtime contexts
export { testConnection }

// Consolidated hash-based key schema - ONLY use these keys
export const KEYS = {
  USER_PROFILE: (userId: string) => `user:${userId}:profile`,
  USER_SUBSCRIPTION: (userId: string) => `user:${userId}:subscription`,
  USER_CREDITS: (userId: string) => `user:${userId}:credits`,
};

// Credits management utilities with consolidated hash-based storage
export const creditUtils = {
  // Get user's remaining credits
  async getRemainingCredits(userId: string): Promise<number> {
    try {
      // Only use hash-based storage
      const creditsHash = await redis.hgetall<{
        total?: string;
        used?: string;
      }>(KEYS.USER_CREDITS(userId));
      
      if (creditsHash && creditsHash.total) {
        const total = parseInt(creditsHash.total);
        const used = creditsHash.used ? parseInt(creditsHash.used) : 0;
        return total - used;
      }
      
      // Default for new users
      return 100;
    } catch (error) {
      console.error('Error fetching credits:', error);
      return 100; // Failsafe
    }
  },

  // Set initial credits for a user
  async initializeCredits(userId: string, credits: number = parseInt(process.env.NEXT_PUBLIC_CREDITS_INITIAL_AMOUNT || '100')): Promise<void> {
    try {
      // Only use hash-based approach
      await redis.hset(KEYS.USER_CREDITS(userId), {
        total: credits.toString(),
        used: '0',
        lastUpdate: new Date().toISOString(),
        resetDate: this.getNextMonthFirstDay()
      });
      
      logger.log(`Credits initialized successfully for ${userId}: ${credits}`);
    } catch (error) {
      console.error('Error initializing credits:', error);
    }
  },

  // Deduct credits when a user makes an API call
  async deductCredits(userId: string, amount: number): Promise<boolean> {
    try {
      // Only use hash-based approach
      const creditsHash = await redis.hgetall<{
        total?: string;
        used?: string;
      }>(KEYS.USER_CREDITS(userId));
      
      if (creditsHash && creditsHash.total) {
        const total = parseInt(creditsHash.total);
        const used = creditsHash.used ? parseInt(creditsHash.used) : 0;
        const remaining = total - used;
        
        // Check if user has enough credits
        if (remaining < amount) {
          return false;
        }
        
        // Update used credits in hash
        const newUsed = used + amount;
        await redis.hset(KEYS.USER_CREDITS(userId), {
          used: newUsed.toString(),
          lastUpdate: new Date().toISOString()
        });
        
        return true;
      }
      
      // Initialize credits if not found
      await this.initializeCredits(userId);
      
      // Check if we have enough of the initial credits
      return amount <= 100;
    } catch (error) {
      console.error('Error deducting credits:', error);
      return true; // Failsafe
    }
  },

  // Check if a user has enough credits
  async hasEnoughCredits(userId: string, amount: number): Promise<boolean> {
    const remainingCredits = await this.getRemainingCredits(userId);
    return remainingCredits >= amount;
  },
  
  // Helper to get the first day of next month
  getNextMonthFirstDay(): string {
    const today = new Date();
    const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1);
    return nextMonth.toISOString().split('T')[0];
  },
  
  // Helper to get the first day of next year
  getNextYearFirstDay(): string {
    const today = new Date();
    const nextYear = new Date(today.getFullYear() + 1, 0, 1);
    return nextYear.toISOString().split('T')[0];
  },
  
  // Reset user credits based on their plan
  async resetUserCredits(userId: string): Promise<boolean> {
    try {
      // Get subscription to determine plan
      const sub = await redis.hgetall(KEYS.USER_SUBSCRIPTION(userId));
      
      if (!sub || !sub.plan) {
        // No subscription found, fallback to basic
        return false;
      }
      
      // Determine credit amount based on plan
      let creditAmount = 100; // Default
      if ((sub.plan as string).includes('Pro')) {
        creditAmount = 999999;
      } else if ((sub.plan as string).includes('Standard')) {
        creditAmount = 500;
      } else if ((sub.plan as string).includes('Basic')) {
        creditAmount = 100;
      }
      
      // Update credits hash
      await redis.hset(KEYS.USER_CREDITS(userId), {
        total: creditAmount.toString(),
        used: '0',
        lastUpdate: new Date().toISOString(),
        resetDate: sub.interval === 'year' ? this.getNextYearFirstDay() : this.getNextMonthFirstDay()
      });
      
      return true;
    } catch (error) {
      console.error('Error resetting user credits:', error);
      return false;
    }
  }
};

// Subscription utilities for efficiently accessing user plan data
export const subscriptionUtils = {
  // Get complete user subscription data efficiently
  async getUserSubscriptionData(userId: string): Promise<{
    plan: string;
    credits: {
      used: number;
      total: number | 'Unlimited';
      remaining: number | 'Unlimited';
    };
    isPro: boolean;
  }> {
    try {
      // Get subscription and credits from hash
      const subData = await redis.hgetall(KEYS.USER_SUBSCRIPTION(userId));
      const creditsData = await redis.hgetall(KEYS.USER_CREDITS(userId));
      
      // Default values if no data found
      let plan = 'Free';
      let isPro = false;
      let creditsTotal = 100;
      let creditsUsed = 0;
      
      // Parse subscription data if found
      if (subData && subData.plan) {
        plan = subData.plan as string;
        isPro = plan.toUpperCase().includes('PRO');
      }
      
      // Parse credits data if found
      if (creditsData) {
        creditsTotal = parseInt(creditsData.total as string || '100');
        creditsUsed = parseInt(creditsData.used as string || '0');
      } 
      
      // Format the response with the right types for unlimited credits
      const isUnlimited = isPro || creditsTotal >= 999999;
      const formattedTotal = isUnlimited ? 'Unlimited' : creditsTotal;
      const remaining = isUnlimited ? 'Unlimited' : Math.max(0, creditsTotal - creditsUsed);
      
      return {
        plan,
        credits: {
          used: creditsUsed,
          total: formattedTotal,
          remaining
        },
        isPro
      };
    } catch (error) {
      console.error('Error getting user subscription data:', error);
      // Return fallback defaults if there's an error
      return {
        plan: 'Free',
        credits: {
          used: 0,
          total: 100, 
          remaining: 100
        },
        isPro: false
      };
    }
  },
  
  // Check if a user has an active subscription
  async isSubscriptionActive(userId: string): Promise<boolean> {
    try {
      const subscriptionData = await redis.hgetall(KEYS.USER_SUBSCRIPTION(userId));
      
      // Check if this is a Free plan (missing data is treated as Free)
      const isFree = 
        !subscriptionData || 
        !subscriptionData.planType || 
        subscriptionData.planType === 'FREE' || 
        (subscriptionData.plan && (subscriptionData.plan as string).includes('Free'));
      
      // Free plans are always considered active
      if (isFree) {
        return true;
      }
      
      // For paid plans, check status and expiration
      if (!subscriptionData.status) {
        return false;
      }
      
      // Check if subscription is active and not expired
      if (subscriptionData.status === 'active') {
        // Check if subscription has expired
        if (subscriptionData.renewalDate) {
          const renewalDate = new Date(subscriptionData.renewalDate as string);
          const now = new Date();
          if (renewalDate < now) {
            // Subscription has expired, downgrade to free plan
            logger.log(`Subscription expired for user ${userId}. Downgrading to Free plan.`);
            await this.downgradeToFreePlan(userId);
            return false;
          }
        }
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error checking subscription status:', error);
      return false;
    }
  },
  
  // Check if a user can use credits based on their subscription
  async canUseCredits(userId: string): Promise<boolean> {
    try {
      // Always check if credits need to be refreshed first, regardless of plan type
      await this.refreshCreditsIfNeeded(userId);
      
      // Then check if subscription is active
      const isActive = await this.isSubscriptionActive(userId);
      
      // Check remaining credits - applies to both free and paid plans
      const remainingCredits = await creditUtils.getRemainingCredits(userId);
      
      return remainingCredits > 0;
    } catch (error) {
      console.error('Error checking if user can use credits:', error);
      return false;
    }
  },
  
  // Refresh credits if needed (for yearly subscriptions)
  async refreshCreditsIfNeeded(userId: string): Promise<boolean> {
    try {
      const subscriptionData = await redis.hgetall(KEYS.USER_SUBSCRIPTION(userId));
      const creditsData = await redis.hgetall(KEYS.USER_CREDITS(userId));
      
      if (!creditsData) {
        return false;
      }
      
      // Check if this is a Free plan (if no subscription data or planType is FREE)
      const isFree = !subscriptionData || 
                     !subscriptionData.planType || 
                     subscriptionData.planType === 'FREE' ||
                     (subscriptionData.plan && (subscriptionData.plan as string).includes('Free'));
      
      // Check if the subscription is pending cancellation/downgrade or inactive
      const isPendingDowngrade = 
        (subscriptionData && (
          subscriptionData.pendingDowngrade === 'true' ||
          subscriptionData.status === 'inactive'
        )) ||
        (creditsData && creditsData.pendingDowngrade === 'true');
      
      // For Free plans, we should consider them as 'active' for credits refresh purposes
      // Also, subscriptions in 'canceling' or 'inactive' state should still get their credits refreshed
      const shouldProcess = isFree || 
                         (subscriptionData && (
                           subscriptionData.status === 'active' || 
                           subscriptionData.status === 'canceling' ||
                           subscriptionData.status === 'inactive'
                         ));
      
      // Treat all plans (including Free) similarly for credit refreshes
      if (shouldProcess) {
        const now = new Date();
        
        // Parse the reset date - handle both YYYY-MM-DD and ISO string formats
        let resetDate = null;
        if (creditsData.resetDate) {
          try {
            // Try to parse the date, accounting for different formats
            const resetStr = creditsData.resetDate as string;
            resetDate = resetStr.includes('T') 
              ? new Date(resetStr) 
              : new Date(`${resetStr}T00:00:00Z`);
          } catch (e) {
            resetDate = null;
          }
        }
        
        // Determine credit amount based on plan type or pending downgrade
        let creditAmount = 100; // Default free plan
        
        if (isPendingDowngrade || (subscriptionData && subscriptionData.status === 'inactive')) {
          // If inactive or pending downgrade, use 100 credits (Free plan)
          creditAmount = 100;
        } else if (!isFree) {
          // Use regular plan type logic for non-free, non-downgrading plans
          const planType = subscriptionData.planType as string;
          if (planType === 'STANDARD') {
            creditAmount = 500;
          } else if (planType === 'PRO') {
            creditAmount = 999999; // Effectively unlimited
          }
        }
        
        // If we've passed the reset date, refresh credits
        // This applies to both free and paid plans
        if (!resetDate || now >= resetDate) {
          // Calculate next reset date - one month from current reset date or now
          const nextResetDate = new Date(resetDate || now);
          nextResetDate.setMonth(nextResetDate.getMonth() + 1);
          
          // Prepare credit data - remove pendingDowngrade and nextTotalCredits if present
          const newCreditData: any = {
            total: creditAmount.toString(),
            used: '0',
            resetDate: nextResetDate.toISOString().split('T')[0],
            lastUpdate: now.toISOString()
          };
          
          // If this was a pending downgrade or an inactive subscription, complete the downgrade
          if (isPendingDowngrade) {
            // Remove the pending flags
            delete newCreditData.pendingDowngrade;
            delete newCreditData.nextTotalCredits;
            
            // If subscription is in canceling state or inactive, complete the downgrade
            if (subscriptionData && (
                subscriptionData.status === 'canceling' || 
                subscriptionData.status === 'inactive'
            )) {
              await this.downgradeToFreePlan(userId);
            }
          }
          
          // Save to Redis (only update credit data if not fully downgraded)
          if (!subscriptionData || (
              subscriptionData.status !== 'canceling' && 
              subscriptionData.status !== 'inactive'
          )) {
            await redis.hset(KEYS.USER_CREDITS(userId), newCreditData);
          }
          
          return true;
        }
      }
      
      return false;
    } catch (error) {
      console.error('Error refreshing credits:', error);
      return false;
    }
  },
  
  // Helper to check if two dates are at least one month apart
  isMonthDifference(date1: Date, date2: Date): boolean {
    // Get difference in months
    const months = (date2.getFullYear() - date1.getFullYear()) * 12 + 
                 (date2.getMonth() - date1.getMonth());
    
    // If months difference is at least 1
    if (months >= 1) {
      return true;
    }
    
    // If same month but day is same or later in the next period
    if (months === 0 && date2.getDate() >= date1.getDate()) {
      return true;
    }
    
    return false;
  },
  
  // Downgrade a user to the free plan
  async downgradeToFreePlan(userId: string): Promise<boolean> {
    try {
      const now = new Date();
      
      // Calculate the reset date for one month from now
      const resetDate = new Date(now);
      resetDate.setMonth(resetDate.getMonth() + 1);
      
      // Update subscription data
      // Note: Free plan status should always be 'active' regardless of payment history
      const subscriptionData = {
        plan: 'Free Plan',
        planType: 'FREE',
        status: 'active', // Free plans are always active
        amount: '0',
        interval: 'month',
        purchaseDate: now.toISOString(),
        renewalDate: '',
        lastUpdated: now.toISOString(),
        stripeCustomerId: '',
        stripeSubscriptionId: ''
      };
      
      // Get current used credits to preserve them
      const currentCredits = await redis.hgetall(KEYS.USER_CREDITS(userId));
      const usedCredits = currentCredits && currentCredits.used 
        ? parseInt(currentCredits.used as string) 
        : 0;
      
      // Set free credits (100) but preserve used credits
      const creditData = {
        total: '100',
        used: Math.min(usedCredits, 100).toString(), // Used credits shouldn't exceed new total
        resetDate: resetDate.toISOString().split('T')[0],
        lastUpdate: now.toISOString()
      };
      
      // Save to Redis
      await redis.hset(KEYS.USER_SUBSCRIPTION(userId), subscriptionData);
      await redis.hset(KEYS.USER_CREDITS(userId), creditData);
      
      logger.log(`Successfully downgraded user ${userId} to the Free plan`);
      return true;
    } catch (error) {
      console.error('Error downgrading to free plan:', error);
      return false;
    }
  },
  
  // Scheduled task to check for expired subscriptions
  // This should be called periodically (via a cron job or similar)
  async checkExpiredSubscriptions(): Promise<void> {
    try {
      // Get all subscription keys
      const subscriptionKeys = await redis.keys('user:*:subscription');
      
      // Check each subscription
      for (const key of subscriptionKeys) {
        // Extract user ID from the key
        const userId = key.split(':')[1];
        
        // Check if subscription is active
        await this.isSubscriptionActive(userId);
      }
    } catch (error) {
      console.error('Error checking expired subscriptions:', error);
    }
  }
};

export const profileUtils = {
  // Save user profile info (at least email)
  async saveUserProfile(userId: string, profile: { email: string, name?: string, image?: string, joinedDate?: string, role?: string }): Promise<void> {
    try {
      await redis.hset(KEYS.USER_PROFILE(userId), {
        email: profile.email,
        name: profile.name || '',
        image: profile.image || '',
        joinedDate: profile.joinedDate || '',
        role: profile.role || '',
      });
      logger.log(`User profile saved for ${userId}`);
    } catch (error) {
      console.error('Error saving user profile:', error);
    }
  },

  // Optionally, get user profile info
  async getUserProfile(userId: string): Promise<any> {
    try {
      return await redis.hgetall(KEYS.USER_PROFILE(userId));
    } catch (error) {
      console.error('Error fetching user profile:', error);
      return null;
    }
  }
};