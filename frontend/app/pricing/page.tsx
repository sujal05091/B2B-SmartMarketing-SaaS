'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Check, Star, Zap } from 'lucide-react'

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for getting started',
    features: [
      '50 leads per month',
      'Basic lead discovery',
      'Email generation',
      'Portfolio creation',
      'Community support'
    ],
    limitations: [
      'Limited to 50 leads/month',
      'Basic analytics',
      'No priority support'
    ],
    buttonText: 'Get Started',
    popular: false,
    stripePriceId: null
  },
  {
    name: 'Pro',
    price: '$9.99',
    period: 'per month',
    description: 'For growing businesses',
    features: [
      '500 leads per month',
      'Advanced lead discovery',
      'AI-powered email personalization',
      'Custom portfolio templates',
      'Priority email support',
      'Google Sheets integration',
      'Advanced analytics'
    ],
    limitations: [],
    buttonText: 'Start Pro Trial',
    popular: true,
    stripePriceId: 'price_pro_monthly' // Replace with actual Stripe price ID
  },
  {
    name: 'Enterprise',
    price: '$29.99',
    period: 'per month',
    description: 'For scaling companies',
    features: [
      'Unlimited leads',
      'All Pro features',
      'Custom integrations',
      'Dedicated account manager',
      'Phone support',
      'White-label options',
      'API access'
    ],
    limitations: [],
    buttonText: 'Contact Sales',
    popular: false,
    stripePriceId: 'price_enterprise_monthly' // Replace with actual Stripe price ID
  }
]

const addOnPlans = [
  {
    name: 'Extra Leads Pack',
    price: '$4.99',
    description: '100 additional leads',
    features: ['100 extra leads', 'Valid for 30 days', 'Can be purchased multiple times']
  }
]

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly')

  const handleSubscribe = async (plan: typeof plans[0]) => {
    if (plan.name === 'Free') {
      // Redirect to signup or dashboard
      window.location.href = '/auth/signup'
      return
    }

    if (plan.name === 'Enterprise') {
      // Redirect to contact form
      window.location.href = '/contact'
      return
    }

    // Handle Stripe checkout for Pro plan
    const token = localStorage.getItem('token')
    if (!token) {
      window.location.href = '/auth/login'
      return
    }

    try {
      const response = await fetch('/api/billing/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          priceId: plan.stripePriceId,
          billingCycle
        }),
      })

      const { url } = await response.json()
      window.location.href = url
    } catch (error) {
      console.error('Error creating checkout session:', error)
    }
  }

  const handleBuyAddOn = async (addOn: typeof addOnPlans[0]) => {
    const token = localStorage.getItem('token')
    if (!token) {
      window.location.href = '/auth/login'
      return
    }

    try {
      const response = await fetch('/api/billing/buy-leads', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          leadPack: 100,
          price: 4.99
        }),
      })

      const { url } = await response.json()
      window.location.href = url
    } catch (error) {
      console.error('Error purchasing leads:', error)
    }
  }

  return (
    <div className="min-h-screen bg-background py-12 px-4">
      <div className="container mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Choose Your Plan
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Start free and scale as you grow. All plans include our core lead generation and AI-powered marketing tools.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4 mb-8">
            <span className={billingCycle === 'monthly' ? 'font-semibold' : 'text-muted-foreground'}>Monthly</span>
            <button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className="relative w-12 h-6 bg-muted rounded-full transition-colors"
            >
              <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'
              }`} />
            </button>
            <span className={billingCycle === 'yearly' ? 'font-semibold' : 'text-muted-foreground'}>
              Yearly <span className="bg-secondary text-secondary-foreground px-2 py-1 rounded text-xs ml-1">Save 20%</span>
            </span>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {plans.map((plan) => (
            <Card key={plan.name} className={`relative ${plan.popular ? 'border-primary shadow-lg' : ''}`}>
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-primary text-primary-foreground px-3 py-1 rounded-full text-sm flex items-center">
                    <Star className="w-3 h-3 mr-1" />
                    Most Popular
                  </span>
                </div>
              )}

              <CardHeader className="text-center">
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <div className="text-3xl font-bold">
                  {billingCycle === 'yearly' && plan.price !== '$0' ? (
                    <span className="line-through text-muted-foreground mr-2">
                      ${(parseFloat(plan.price.slice(1)) * 12).toFixed(2)}
                    </span>
                  ) : null}
                  {billingCycle === 'yearly' && plan.price !== '$0'
                    ? `$${(parseFloat(plan.price.slice(1)) * 12 * 0.8).toFixed(2)}`
                    : plan.price
                  }
                  {plan.price !== '$0' && <span className="text-lg font-normal text-muted-foreground">/{billingCycle === 'yearly' ? 'year' : plan.period}</span>}
                </div>
                <CardDescription>{plan.description}</CardDescription>
              </CardHeader>

              <CardContent>
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-center">
                      <Check className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  onClick={() => handleSubscribe(plan)}
                  className="w-full"
                  variant={plan.popular ? 'default' : 'outline'}
                >
                  {plan.buttonText}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Add-on Plans */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold mb-4">Need More Leads?</h2>
          <p className="text-muted-foreground mb-8">Purchase additional leads anytime</p>
        </div>

        <div className="grid md:grid-cols-1 max-w-md mx-auto gap-6">
          {addOnPlans.map((addOn) => (
            <Card key={addOn.name}>
              <CardHeader className="text-center">
                <CardTitle className="text-xl">{addOn.name}</CardTitle>
                <div className="text-2xl font-bold text-primary">{addOn.price}</div>
                <CardDescription>{addOn.description}</CardDescription>
              </CardHeader>

              <CardContent>
                <ul className="space-y-2 mb-6">
                  {addOn.features.map((feature, index) => (
                    <li key={index} className="flex items-center">
                      <Zap className="w-4 h-4 text-yellow-500 mr-2 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button onClick={() => handleBuyAddOn(addOn)} className="w-full">
                  Buy Now
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* FAQ or Additional Info */}
        <div className="text-center mt-12">
          <p className="text-muted-foreground">
            All plans include a 14-day free trial. Cancel anytime.
            <br />
            Need a custom plan? <a href="/contact" className="text-primary hover:underline">Contact us</a>
          </p>
        </div>
      </div>
    </div>
  )
}