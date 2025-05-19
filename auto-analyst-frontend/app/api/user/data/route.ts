// import { NextRequest, NextResponse } from 'next/server'
// import { getToken } from 'next-auth/jwt'
// import redis, { KEYS, subscriptionUtils, profileUtils } from '@/lib/redis'

// // Define subscription plan options to match pricing.tsx tiers
// const SUBSCRIPTION_PLANS = {
//   FREE: {
//     name: 'Free',
//     totalCredits: 100,
//     amount: 0,
//     interval: 'month'
//   },
//   STANDARD: {
//     name: 'Standard',
//     totalCredits: 500,
//     amount: 15,
//     yearlyAmount: 126,
//     interval: 'month',
//     yearlyInterval: 'year'
//   },
//   PRO: {
//     name: 'Pro',
//     totalCredits: Number.MAX_SAFE_INTEGER, // Unlimited
//     amount: 29,
//     yearlyAmount: 243.60,
//     interval: 'month',
//     yearlyInterval: 'year'
//   }
// }

// export async function GET(request: NextRequest) {
//   // Use getToken to authenticate
//   const token = await getToken({ req: request })
//   
//   if (!token || !token.email) {
//     return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
//   }
//
//   try {
//     const userEmail = token.email
//     const userId = token.sub || "anonymous"
//     
//     // Get force flag to bypass caching
//     const searchParams = request.nextUrl.searchParams
//     const forceRefresh = searchParams.get('force') === 'true' || searchParams.get('refresh') === 'true'
//     
//     // Check if we should force a credits check/refresh
//     if (forceRefresh) {
//       await subscriptionUtils.refreshCreditsIfNeeded(userId)
//     }
//     
//     // Get timestamp query param (for cache busting)
//     const timestamp = searchParams.get('_t') || Date.now()
//     
//     // Check subscription data in Redis (hash-based storage)
//     const subscriptionData = await redis.hgetall(KEYS.USER_SUBSCRIPTION(userId)) || {}
//     
//     // Determine plan key mapping
//     let planKey = 'FREE'
//     let planDetails = SUBSCRIPTION_PLANS.FREE
//     
//     if (subscriptionData.planType === 'PRO') {
//       planKey = 'PRO'
//       planDetails = SUBSCRIPTION_PLANS.PRO
//     } else if (subscriptionData.planType === 'STANDARD') {
//       planKey = 'STANDARD'
//       planDetails = SUBSCRIPTION_PLANS.STANDARD
//     }
//     
//     // Get subscription values from Redis with defaults
//     const amount = subscriptionData.amount ? parseFloat(subscriptionData.amount as string) : planDetails.amount
//     const purchaseDate = subscriptionData.purchaseDate || new Date().toISOString()
//     const interval = subscriptionData.interval || planDetails.interval
//     let status = subscriptionData.status || 'inactive'
//     
//     // Override status for Free plans - Free plans should always be active
//     if (planKey === 'FREE' || planDetails.name === 'Free') {
//       status = 'active'
//     }
//     
//     const stripeCustomerId = subscriptionData.stripeCustomerId || ''
//     const stripeSubscriptionId = subscriptionData.stripeSubscriptionId || ''
//     
//     // Calculate renewal date based on purchase date and interval
//     let renewalDate = subscriptionData.renewalDate as string || calculateRenewalDate(purchaseDate as string, interval as string)
//     
//     // Get credit data from Redis
//     const creditsData = await redis.hgetall(KEYS.USER_CREDITS(userId)) || {}
//     
//     // Set default credit values if not found
//     const creditsUsed = creditsData.used ? parseInt(creditsData.used as string) : 0
//     const creditsTotal = creditsData.total ? parseInt(creditsData.total as string) : planDetails.totalCredits
//     const resetDate = creditsData.resetDate as string || new Date(new Date().getFullYear(), new Date().getMonth() + 1, 1).toISOString().split('T')[0]
//     const lastUpdate = creditsData.lastUpdate as string || new Date().toISOString()
//
//     // Format total credits for UI display
//     const formattedTotal = creditsTotal === 999999 ? Infinity : creditsTotal
//     
//     // Handle yearly subscription special case
//     const isYearly = interval === 'year'
//     if (isYearly && !creditsData.nextMonthlyReset) {
//       // Add a special field for yearly subscriptions to show next monthly credit reset
//       // Ensure lastUpdate is a valid date string
//       const lastUpdateStr = typeof lastUpdate === 'string' ? lastUpdate : new Date().toISOString()
//       const nextReset = new Date(lastUpdateStr)
//       nextReset.setMonth(nextReset.getMonth() + 1)
//       
//       // Add the next monthly reset date for yearly plans
//       creditsData.nextMonthlyReset = nextReset.toISOString().split('T')[0]
//     }
//     
//     // For yearly subscriptions, ensure we have the correct next credit reset date
//     if (subscriptionData.interval === 'year') {
//       // If we have a subscription but no explicit nextMonthlyReset field, calculate it
//       if (!subscriptionData.nextMonthlyReset) {
//         const now = new Date();
//         const nextMonth = new Date(now);
//         nextMonth.setMonth(now.getMonth() + 1);
//         nextMonth.setDate(1); // First day of next month
//         
//         // Store this for future reference
//         await redis.hset(KEYS.USER_SUBSCRIPTION(userId), {
//           nextMonthlyReset: nextMonth.toISOString().split('T')[0]
//         });
//         
//         // Update our local copy too
//         subscriptionData.nextMonthlyReset = nextMonth.toISOString().split('T')[0];
//       }
//     }
//     
//     // Return the user data
//     const userData = {
//       profile: {
//         name: token.name || 'User',
//         email: userEmail,
//         image: token.picture,
//         joinedDate: subscriptionData.purchaseDate ? 
//           (subscriptionData.purchaseDate as string).split('T')[0] : 
//           new Date().toISOString().split('T')[0],
//         role: planDetails.name
//       },
//       subscription: {
//         plan: planDetails.name,
//         planType: subscriptionData.planType,
//         status: status,
//         amount: parseFloat(subscriptionData.amount as string) || amount,
//         interval: subscriptionData.interval || interval,
//         renewalDate: renewalDate,
//         isYearly: interval === 'year',
//         nextCreditReset: interval === 'year' ? resetDate : null,
//         stripeCustomerId: stripeCustomerId,
//         stripeSubscriptionId: stripeSubscriptionId
//       },
//       credits: {
//         used: creditsUsed,
//         total: formattedTotal,
//         resetDate: resetDate,
//         lastUpdate: lastUpdate,
//         resetInterval: 'month' // Always monthly
//       },
//       debug: {
//         userId,
//         timestamp,
//         rawSubscriptionData: subscriptionData,
//         rawCreditsData: creditsData,
//         planKey
//       }
//     }
//     
//     // Save user profile to Redis
//     await profileUtils.saveUserProfile(userId, {
//       email: userEmail,
//       name: token.name || 'User',
//       image: token.picture as string || '',
//       joinedDate: userData.profile.joinedDate,
//       role: planDetails.name
//     });
//     
//     return NextResponse.json(userData)
//   } catch (error) {
//     console.error('Error fetching user data:', error)
//     return NextResponse.json({ error: 'Failed to fetch user data' }, { status: 500 })
//   }
// }

// function calculateRenewalDate(purchaseDate: string, interval: string): string {
//   const date = new Date(purchaseDate)
//   
//   if (interval === 'month') {
//     // Add one month to the purchase date
//     date.setMonth(date.getMonth() + 1)
//   } else if (interval === 'year') {
//     // Add one year to the purchase date
//     date.setFullYear(date.getFullYear() + 1)
//   }
//   
//   return date.toISOString().split('T')[0]
// } 

export {} 