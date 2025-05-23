"use client"

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Head from 'next/head'
import Link from 'next/link'
import { Elements } from '@stripe/react-stripe-js'
import { loadStripe, StripeElementsOptions } from '@stripe/stripe-js'
import { motion } from 'framer-motion'
import { ArrowLeft, CreditCard, ShieldCheck, Lock } from 'lucide-react'
import CheckoutForm from '@/components/CheckoutForm'
import { useSession } from 'next-auth/react'

// Load stripe outside of component to avoid recreating it on each render
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)

export default function CheckoutPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { data: session, status } = useSession()
  const [loadingPlan, setLoadingPlan] = useState(true)
  
  const plan = searchParams?.get('plan')
  const cycle = searchParams?.get('cycle')
  
  const [planDetails, setPlanDetails] = useState({
    name: '',
    amount: 0,
    cycle: 'month',
    priceId: '',
  })
  
  // Add state for payment intent
  const [clientSecret, setClientSecret] = useState('')
  const [paymentLoading, setPaymentLoading] = useState(false)
  const [paymentError, setPaymentError] = useState('')
  
  useEffect(() => {
    if (!plan || !cycle || status === 'loading') {
      return
    }
    
    if (status === 'unauthenticated') {
      router.push('/login?redirect=/pricing')
      return
    }
    
    // Get plan details based on URL parameters
    const pricingTiers = [
      {
        name: 'Standard',
        monthly: {
          price: 15,
          priceId: process.env.NEXT_PUBLIC_STRIPE_MONTHLY_PRICE_ID,
        },
        yearly: {
          price: 126,
          priceId: process.env.NEXT_PUBLIC_STRIPE_YEARLY_PRICE_ID,
        },
        daily: {
          price: 0.75,
          priceId: process.env.NEXT_PUBLIC_STRIPE_DAILY_PRICE_ID,
        },
      },
      {
        name: 'Pro',
        monthly: {
          price: 29,
          priceId: process.env.NEXT_PUBLIC_STRIPE_PRO_PRICE_ID,
        },
        yearly: {
          price: 244,
          priceId: process.env.NEXT_PUBLIC_STRIPE_PRO_YEARLY_PRICE_ID,
        },
      },
    ]
    
    const selectedPlan = pricingTiers.find(p => p.name.toLowerCase() === plan)
    
    if (selectedPlan) {
      const billing = cycle === 'yearly' ? 'yearly' : cycle === 'daily' ? 'daily' : 'monthly'
      const planData = {
        name: selectedPlan.name,
        amount: selectedPlan[billing]?.price || 0,
        cycle: billing === 'yearly' ? 'year' : billing === 'daily' ? 'day' : 'month',
        priceId: selectedPlan[billing]?.priceId || '',
      }
      
      setPlanDetails(planData)
      
      // Create checkout session when plan is selected
      if (planData.priceId && session) {
        setPaymentLoading(true)
        
        fetch('/api/checkout-sessions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            priceId: planData.priceId,
            userId: session.user?.email,
            planName: planData.name,
            interval: planData.cycle,
          }),
        })
          .then(res => res.json())
          .then(data => {
            if (data.message) {
              setPaymentError(data.message)
            } else {
              setClientSecret(data.clientSecret)
            }
            setPaymentLoading(false)
          })
          .catch(err => {
            console.error('Error creating payment intent:', err)
            setPaymentError('Failed to set up payment. Please try again.')
            setPaymentLoading(false)
          })
      }
    } else {
      // Plan not found, redirect to pricing
      router.push('/pricing')
    }
    
    setLoadingPlan(false)
  }, [plan, cycle, router, status, session])
  
  if (status === 'loading' || loadingPlan || paymentLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-10 h-10 rounded-full border-t-2 border-[#FF7F7F]"
        />
      </div>
    )
  }
  
  return (
    <>
      <Head>
        <title>Checkout | Auto-Analyst</title>
      </Head>
      
      <div className="min-h-screen bg-gray-50 py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between mb-10">
            <Link href="/pricing" className="flex items-center text-gray-700 hover:text-[#FF7F7F] transition-colors cursor-pointer">
              <ArrowLeft size={16} className="mr-1" />
              <span>Back to pricing</span>
            </Link>
            
            <div className="flex items-center gap-1 text-sm text-gray-500">
              <Lock size={14} />
              <span>Secure Checkout</span>
            </div>
          </div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <h1 className="text-3xl font-bold text-gray-900 mb-2 text-center">Complete your purchase</h1>
            <p className="text-gray-600 mb-10 text-center">
              You're subscribing to the {planDetails.name} plan
            </p>
            
            {paymentError && (
              <div className="mb-6 p-4 bg-red-50 text-red-600 rounded-md">
                {paymentError}
              </div>
            )}
            
            <div className="grid gap-10 lg:grid-cols-5">
              <div className="lg:col-span-3">
                {clientSecret && (
                  <Elements 
                    stripe={stripePromise} 
                    options={{ 
                      clientSecret,
                      appearance: {
                        theme: 'stripe' as const
                      }
                    } as StripeElementsOptions}
                  >
                    <CheckoutForm 
                      planName={planDetails.name}
                      amount={planDetails.amount}
                      interval={planDetails.cycle as 'month' | 'year' | 'day'}
                      clientSecret={clientSecret}
                    />
                  </Elements>
                )}
              </div>
              
              <div className="lg:col-span-2">
                <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Order Summary</h3>
                  
                  <div className="border-t border-gray-200 py-4">
                    <div className="flex justify-between mb-2">
                      <span className="text-gray-700">{planDetails.name} Plan</span>
                      <span className="text-gray-900">${planDetails.amount}</span>
                    </div>
                    <p className="text-sm text-gray-500">
                      Billed {planDetails.cycle === 'year' ? 'yearly' : planDetails.cycle === 'day' ? 'daily' : 'monthly'}
                    </p>
                  </div>
                  
                  <div className="border-t border-gray-200 py-4">
                    <div className="flex justify-between font-medium text-gray-900">
                      <span>Total (USD)</span>
                      <span>${planDetails.amount}</span>
                    </div>
                  </div>
                  
                  <div className="mt-6 space-y-4">
                    <div className="flex items-center text-sm text-gray-600">
                      <ShieldCheck size={16} className="mr-2 text-green-500" />
                      <span>Your subscription is protected by our 30-day guarantee</span>
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <CreditCard size={16} className="mr-2 text-gray-400" />
                      <span>We accept all major credit cards</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </>
  )
} 