'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowLeft, Search, Loader2, Download, ExternalLink } from 'lucide-react'
import Link from 'next/link'
import axios from 'axios'

interface Lead {
  name: string
  address: string
  phone?: string
  website?: string
  rating?: number
  reviews?: number
  category?: string
}

export default function DiscoverLeadsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [leads, setLeads] = useState<Lead[]>([])
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    business_name: '',
    business_desc: '',
    website: '',
    target_industry: '',
    target_region: '',
    max_leads: 20,
    find_emails: true,
    generate_pdfs: false
  })

  const handleDiscover = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setLeads([])

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        router.push('/auth/login')
        return
      }

      const response = await api.post(
        '/api/leads/discover',
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      )

      // Backend returns a task_id for background processing
      if (response.data.task_id) {
        setError('') 
        alert(`✅ Lead discovery started! Task ID: ${response.data.task_id}\n\nThe system will process your request in the background. You can check the results in "View All Leads" shortly.`)
        router.push('/dashboard/leads')
      } else {
        setLeads(response.data.leads || [])
      }
      
      if (response.data.leads?.length === 0) {
        setError('No leads found. Try different search terms or location.')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to discover leads. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const exportToCSV = () => {
    if (leads.length === 0) return

    const headers = ['Name', 'Address', 'Phone', 'Website', 'Rating', 'Reviews', 'Category']
    const csvContent = [
      headers.join(','),
      ...leads.map(lead => [
        `"${lead.name}"`,
        `"${lead.address}"`,
        lead.phone || '',
        lead.website || '',
        lead.rating || '',
        lead.reviews || '',
        lead.category || ''
      ].join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `leads-${Date.now()}.csv`
    a.click()
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Professional Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200 shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <Link href="/dashboard" className="inline-flex items-center text-sm text-slate-600 hover:text-slate-900 transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-6xl">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-1 h-8 bg-gradient-to-b from-blue-600 to-indigo-600 rounded-full"></div>
            <h1 className="text-3xl font-bold text-slate-900">🎯 Discover Leads</h1>
          </div>
          <p className="text-slate-600">
            Find potential B2B customers using AI-powered search
          </p>
        </div>

        {/* Search Form */}
        <Card className="mb-6 bg-white/80 backdrop-blur-lg border-slate-200/60 shadow-lg">
          <CardHeader>
            <CardTitle className="text-slate-900">Search Parameters</CardTitle>
            <CardDescription className="text-slate-600">
              Enter what type of businesses you&apos;re looking for and where
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleDiscover} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="business_name">Your Business Name *</Label>
                  <Input
                    id="business_name"
                    placeholder="e.g., Acme Marketing Agency"
                    value={formData.business_name}
                    onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="website">Your Website (Optional)</Label>
                  <Input
                    id="website"
                    placeholder="e.g., https://acme.com"
                    value={formData.website}
                    onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="business_desc">Business Description *</Label>
                <Input
                  id="business_desc"
                  placeholder="e.g., We provide digital marketing services to small businesses"
                  value={formData.business_desc}
                  onChange={(e) => setFormData({ ...formData, business_desc: e.target.value })}
                  required
                />
                <p className="text-xs text-muted-foreground">
                  What services/products does your business offer?
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="target_industry">Target Industry (Optional)</Label>
                  <Input
                    id="target_industry"
                    placeholder="e.g., restaurants, real estate, healthcare"
                    value={formData.target_industry}
                    onChange={(e) => setFormData({ ...formData, target_industry: e.target.value })}
                  />
                  <p className="text-xs text-muted-foreground">
                    What industry are you targeting?
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="target_region">Target Region (Optional)</Label>
                  <Input
                    id="target_region"
                    placeholder="e.g., New York, Mumbai, USA"
                    value={formData.target_region}
                    onChange={(e) => setFormData({ ...formData, target_region: e.target.value })}
                  />
                  <p className="text-xs text-muted-foreground">
                    Geographic area to search
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="max_leads">Maximum Leads</Label>
                <Input
                  id="max_leads"
                  type="number"
                  min="1"
                  max="100"
                  value={formData.max_leads}
                  onChange={(e) => setFormData({ ...formData, max_leads: parseInt(e.target.value) })}
                />
                <p className="text-xs text-muted-foreground">
                  Number of leads to discover (1-100)
                </p>
              </div>

              {error && (
                <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                  {error}
                </div>
              )}

              <div className="flex gap-3">
                <Button type="submit" disabled={loading} className="gap-2">
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Discovering...
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4" />
                      Discover Leads
                    </>
                  )}
                </Button>

                {leads.length > 0 && (
                  <Button type="button" variant="outline" onClick={exportToCSV} className="gap-2">
                    <Download className="h-4 w-4" />
                    Export CSV
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Results */}
        {leads.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Found {leads.length} Leads</CardTitle>
              <CardDescription>
                Click on any lead to view details
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {leads.map((lead, index) => (
                  <div
                    key={index}
                    className="p-4 border rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg mb-1">{lead.name}</h3>
                        <p className="text-sm text-muted-foreground mb-2">{lead.address}</p>
                        
                        <div className="flex flex-wrap gap-4 text-sm">
                          {lead.phone && (
                            <div className="flex items-center gap-1">
                              <span className="text-muted-foreground">📞</span>
                              <span>{lead.phone}</span>
                            </div>
                          )}
                          {lead.website && (
                            <a
                              href={lead.website}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-1 text-blue-600 hover:underline"
                            >
                              <ExternalLink className="h-3 w-3" />
                              Website
                            </a>
                          )}
                          {lead.rating && (
                            <div className="flex items-center gap-1">
                              <span className="text-yellow-500">⭐</span>
                              <span>{lead.rating} ({lead.reviews} reviews)</span>
                            </div>
                          )}
                        </div>

                        {lead.category && (
                          <div className="mt-2">
                            <span className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                              {lead.category}
                            </span>
                          </div>
                        )}
                      </div>

                      <Button variant="outline" size="sm">
                        Save Lead
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {loading && (
          <Card>
            <CardContent className="py-12">
              <div className="text-center">
                <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-blue-600" />
                <p className="text-lg font-medium">Searching for leads...</p>
                <p className="text-sm text-muted-foreground mt-1">
                  This may take 10-30 seconds depending on search complexity
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  )
}
