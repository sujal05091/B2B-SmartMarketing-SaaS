'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Users, Target, TrendingUp, Mail, LogOut, Settings as SettingsIcon, MessageCircle } from 'lucide-react'
import { API_URL } from '@/lib/api'

interface User {
  id: string
  email: string
  full_name: string
  company_name: string
  plan: string
}

interface DashboardStats {
  total_leads: number
  emails_sent: number
  success_rate: number
}

interface UserUsage {
  leads_used: number
  lead_limit: number
  plan: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<DashboardStats>({
    total_leads: 0,
    emails_sent: 0,
    success_rate: 0
  })
  const [usage, setUsage] = useState<UserUsage>({
    leads_used: 0,
    lead_limit: 50,
    plan: 'free'
  })

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    
    if (!token || !userData) {
      router.push('/auth/login')
      return
    }

    setUser(JSON.parse(userData))
    fetchDashboardStats()
    fetchUserUsage()
    setLoading(false)
  }, [router])

  const fetchDashboardStats = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/analytics/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error)
    }
  }

  const fetchUserUsage = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (response.ok) {
        const userData = await response.json()
        setUsage({
          leads_used: userData.leads_used || 0,
          lead_limit: userData.lead_limit || 50,
          plan: userData.plan || 'free'
        })
      }
    } catch (error) {
      console.error('Failed to fetch user usage:', error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Professional Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <Target className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">B2B Smart Marketing</h1>
              <p className="text-sm text-slate-600">{user?.company_name}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button 
              variant="outline" 
              onClick={() => router.push('/dashboard/settings')}
              className="border-slate-300 hover:bg-slate-50"
            >
              <SettingsIcon className="h-4 w-4 mr-2" />
              Settings
            </Button>
            <Button 
              variant="outline" 
              onClick={handleLogout}
              className="border-slate-300 hover:bg-slate-50"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Professional Welcome Section */}
        <div className="mb-10">
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-1 h-8 bg-gradient-to-b from-blue-600 to-indigo-600 rounded-full"></div>
            <h2 className="text-3xl font-bold text-slate-900">Welcome back, {user?.full_name}</h2>
          </div>
          <p className="text-slate-600 text-lg">
            Optimize your lead generation and accelerate business growth
          </p>
        </div>

        {/* Usage Meter */}
        <Card className="mb-8 shadow-lg border-0 bg-gradient-to-r from-blue-50 to-indigo-50">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg font-semibold text-slate-900 flex items-center justify-between">
              <span>Lead Usage</span>
              <span className="text-sm font-normal text-slate-600">
                {usage.leads_used} / {usage.lead_limit} leads used
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="w-full bg-slate-200 rounded-full h-3">
                <div 
                  className={`h-3 rounded-full transition-all duration-500 ${
                    usage.leads_used / usage.lead_limit > 0.8 
                      ? 'bg-red-500' 
                      : usage.leads_used / usage.lead_limit > 0.6 
                        ? 'bg-yellow-500' 
                        : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min((usage.leads_used / usage.lead_limit) * 100, 100)}%` }}
                />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-600">
                  {usage.lead_limit - usage.leads_used} leads remaining
                </span>
                {usage.leads_used / usage.lead_limit > 0.8 && (
                  <Button 
                    size="sm" 
                    onClick={() => router.push('/pricing')}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    Upgrade Plan
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Professional Stats Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <StatCard
            title="Total Leads"
            value={stats.total_leads.toString()}
            icon={<Users className="h-8 w-8 text-blue-600" />}
            description="Active prospects"
            trend="↗️ +12%"
            color="blue"
          />
          <StatCard
            title="Active Campaigns"
            value="0"
            icon={<Target className="h-8 w-8 text-indigo-600" />}
            description="Running campaigns"
            trend="📈 Ready to launch"
            color="indigo"
          />
          <StatCard
            title="Conversion Rate"
            value={`${stats.success_rate}%`}
            icon={<TrendingUp className="h-8 w-8 text-emerald-600" />}
            description="Lead to customer"
            trend="🎯 Target: 15%"
            color="emerald"
          />
          <StatCard
            title="Emails Sent"
            value={stats.emails_sent.toString()}
            icon={<Mail className="h-8 w-8 text-amber-600" />}
            description="This month"
            trend="📧 Automated"
            color="amber"
          />
        </div>

        {/* Quick Actions - Professional Design */}
        <Card className="shadow-lg border-0 bg-white">
          <CardHeader className="pb-6">
            <CardTitle className="text-xl font-semibold text-slate-900 flex items-center">
              <div className="w-2 h-2 bg-blue-600 rounded-full mr-3"></div>
              Quick Actions
            </CardTitle>
            <CardDescription className="text-slate-600">
              Streamline your marketing operations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <Button 
                className="h-24 bg-gradient-to-br from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-lg border-0 group" 
                onClick={() => router.push('/dashboard/discover')}
              >
                <div className="text-center">
                  <Target className="h-8 w-8 mx-auto mb-3 text-white group-hover:scale-110 transition-transform" />
                  <div className="text-white font-semibold">Discover Leads</div>
                  <div className="text-blue-100 text-xs mt-1">AI-powered prospecting</div>
                </div>
              </Button>
              <Button 
                className="h-24 bg-gradient-to-br from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 shadow-lg border-0 group" 
                onClick={() => router.push('/dashboard/leads')}
              >
                <div className="text-center">
                  <Users className="h-8 w-8 mx-auto mb-3 text-white group-hover:scale-110 transition-transform" />
                  <div className="text-white font-semibold">Manage Leads</div>
                  <div className="text-indigo-100 text-xs mt-1">View & organize prospects</div>
                </div>
              </Button>
              <Button 
                className="h-24 bg-gradient-to-br from-slate-700 to-slate-800 hover:from-slate-800 hover:to-slate-900 shadow-lg border-0 group"
                onClick={() => router.push('/dashboard/chatbot')}
              >
                <div className="text-center">
                  <MessageCircle className="h-8 w-8 mx-auto mb-3 text-white group-hover:scale-110 transition-transform" />
                  <div className="text-white font-semibold">AI Assistant</div>
                  <div className="text-slate-300 text-xs mt-1">B2B marketing insights</div>
                </div>
              </Button>
              <Button 
                className="h-24 bg-gradient-to-br from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 shadow-lg border-0 group"
              >
                <div className="text-center">
                  <Mail className="h-8 w-8 mx-auto mb-3 text-white group-hover:scale-110 transition-transform" />
                  <div className="text-white font-semibold">Create Campaign</div>
                  <div className="text-emerald-100 text-xs mt-1">Automated outreach</div>
                </div>
              </Button>
              <Button 
                className="h-24 bg-gradient-to-br from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 shadow-lg border-0 group"
                onClick={() => router.push('/pricing')}
              >
                <div className="text-center">
                  <TrendingUp className="h-8 w-8 mx-auto mb-3 text-white group-hover:scale-110 transition-transform" />
                  <div className="text-white font-semibold">Buy More Leads</div>
                  <div className="text-amber-100 text-xs mt-1">$0.10 per lead</div>
                </div>
              </Button>
              <Button 
                className="h-24 bg-gradient-to-br from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 shadow-lg border-0 group"
                onClick={() => router.push('/pricing')}
              >
                <div className="text-center">
                  <SettingsIcon className="h-8 w-8 mx-auto mb-3 text-white group-hover:scale-110 transition-transform" />
                  <div className="text-white font-semibold">Upgrade Plan</div>
                  <div className="text-purple-100 text-xs mt-1">More features & leads</div>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Professional Getting Started */}
        <Card className="mt-8 shadow-lg border-0 bg-gradient-to-r from-blue-600/5 via-indigo-600/5 to-purple-600/5">
          <CardHeader>
            <CardTitle className="text-xl font-semibold text-slate-900 flex items-center">
              <div className="w-2 h-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full mr-3"></div>
              Getting Started Guide
            </CardTitle>
            <CardDescription className="text-slate-600">
              Follow these steps to maximize your lead generation results
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-4 p-4 bg-white/60 rounded-lg border border-green-200">
                <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center text-white font-bold shadow-lg">
                  ✓
                </div>
                <div>
                  <div className="font-semibold text-slate-900">Account Setup Complete</div>
                  <div className="text-sm text-slate-600">Your B2B marketing platform is ready</div>
                </div>
              </div>
              <div className="flex items-center gap-4 p-4 bg-white/60 rounded-lg border border-blue-200">
                <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold shadow-lg">
                  2
                </div>
                <div>
                  <div className="font-semibold text-slate-900">Configure API Keys</div>
                  <div className="text-sm text-slate-600">Set up SerpAPI, Hunter.io, and AI providers</div>
                </div>
              </div>
              <div className="flex items-center gap-4 p-4 bg-white/60 rounded-lg border border-indigo-200">
                <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold shadow-lg">
                  3
                </div>
                <div>
                  <div className="font-semibold text-slate-900">Launch Your First Campaign</div>
                  <div className="text-sm text-slate-600">Discover and engage with quality B2B leads</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

function StatCard({ title, value, icon, description, trend, color }: { 
  title: string
  value: string
  icon: React.ReactNode
  description: string
  trend?: string
  color?: string
}) {
  const colorClasses = {
    blue: 'border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100',
    indigo: 'border-indigo-200 bg-gradient-to-br from-indigo-50 to-indigo-100',
    emerald: 'border-emerald-200 bg-gradient-to-br from-emerald-50 to-emerald-100',
    amber: 'border-amber-200 bg-gradient-to-br from-amber-50 to-amber-100',
  }

  return (
    <Card className={`shadow-lg border-0 ${colorClasses[color as keyof typeof colorClasses] || 'border-slate-200 bg-white'}`}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle className="text-sm font-semibold text-slate-900">{title}</CardTitle>
        <div className="p-2 bg-white/60 rounded-lg shadow-sm">
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold text-slate-900 mb-1">{value}</div>
        <p className="text-xs text-slate-600 mb-2">{description}</p>
        {trend && (
          <div className="text-xs font-medium text-slate-700 bg-white/40 px-2 py-1 rounded-md inline-block">
            {trend}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
