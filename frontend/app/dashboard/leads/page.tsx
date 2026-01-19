'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowLeft, ExternalLink, Mail, Loader2, RefreshCw, Calendar, ChevronDown } from 'lucide-react'
import Link from 'next/link'
import { api } from '@/lib/api'

interface Lead {
  id: string
  company_name: string
  website?: string
  industry?: string
  services?: string
  contact_email?: string
  email_subject?: string
  email_body?: string
  status: string
  created_at: string
}

export default function ViewLeadsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [leads, setLeads] = useState<Lead[]>([])
  const [error, setError] = useState('')
  const [sendingEmail, setSendingEmail] = useState<string | null>(null)
  const [emailSuccess, setEmailSuccess] = useState<string | null>(null)
  const [sendingAllEmails, setSendingAllEmails] = useState(false)
  const [sendAllResults, setSendAllResults] = useState<any>(null)

  const fetchLeads = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        router.push('/auth/login')
        return
      }

      const response = await api.get(
        '/api/leads/',
        {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          params: {
            skip: 0,
            limit: 100
          }
        }
      )

      console.log('📊 API Response:', response.data)
      console.log('📊 Number of leads:', response.data?.length || 0)
      setLeads(response.data || [])
    } catch (err: any) {
      console.error('❌ Error fetching leads:', err)
      setError(err.response?.data?.detail || 'Failed to load leads')
    } finally {
      setLoading(false)
    }
  }, [router])

  useEffect(() => {
    fetchLeads()
  }, [fetchLeads])

  const handleSendEmail = async (leadId: string) => {
    setSendingEmail(leadId)
    setEmailSuccess(null)
    
    try {
      const token = localStorage.getItem('token')
      await api.post(
        `/api/leads/${leadId}/send-email`,
        {},
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )
      
      setEmailSuccess(leadId)
      // Refresh leads to update status
      await fetchLeads()
      
      // Clear success message after 3 seconds
      setTimeout(() => setEmailSuccess(null), 3000)
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to send email'
      alert(errorMessage)
    } finally {
      setSendingEmail(null)
    }
  }

  const handleSendAllEmails = async () => {
    if (!confirm('Are you sure you want to send emails to all leads with email addresses? This will mark them as contacted.')) {
      return
    }

    setSendingAllEmails(true)
    setSendAllResults(null)

    try {
      const token = localStorage.getItem('token')
      const response = await api.post(
        '/api/leads/send-all-emails',
        {},
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )
      
      setSendAllResults(response.data)
      // Refresh leads to update status
      await fetchLeads()
      
      alert(`Email sending completed!\n${response.data.sent_count} sent, ${response.data.failed_count} failed`)
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to send emails'
      alert(errorMessage)
    } finally {
      setSendingAllEmails(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Professional Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <Link href="/dashboard" className="inline-flex items-center text-sm text-slate-600 hover:text-slate-900 transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-7xl">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <div className="w-1 h-8 bg-gradient-to-b from-blue-600 to-indigo-600 rounded-full"></div>
              <h1 className="text-3xl font-bold text-slate-900">Lead Management</h1>
            </div>
            <p className="text-slate-600 text-lg">
              Manage and engage with your B2B prospects
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button variant="outline" onClick={fetchLeads} disabled={loading} className="border-slate-300 hover:bg-slate-50">
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button 
              variant="outline" 
              onClick={handleSendAllEmails} 
              disabled={sendingAllEmails || leads.length === 0}
              className="whitespace-nowrap border-slate-300 hover:bg-slate-50"
            >
              {sendingAllEmails ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Sending All...
                </>
              ) : (
                <>
                  <Mail className="h-4 w-4 mr-2" />
                  Send All Emails
                </>
              )}
            </Button>
            <Button onClick={() => router.push('/dashboard/discover')} className="whitespace-nowrap bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700">
              Discover More Leads
            </Button>
          </div>
        </div>

        {error && (
          <div className="p-4 mb-6 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
            {error}
          </div>
        )}

        {loading ? (
          <Card>
            <CardContent className="py-12">
              <div className="text-center">
                <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-blue-600" />
                <p className="text-lg font-medium">Loading leads...</p>
              </div>
            </CardContent>
          </Card>
        ) : leads.length === 0 ? (
          <Card>
            <CardContent className="py-12">
              <div className="text-center">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-xl font-semibold mb-2">No leads yet</h3>
                <p className="text-muted-foreground mb-4">
                  Start discovering potential customers for your business
                </p>
                <Button onClick={() => router.push('/dashboard/discover')}>
                  Discover Your First Leads
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <>
            <div className="mb-6">
              <div className="flex items-center gap-2 text-sm text-slate-600">
                <span className="font-medium">📊 Showing {leads.length} lead{leads.length !== 1 ? 's' : ''}</span>
              </div>
            </div>

            <div className="grid gap-6">
              {leads.map((lead) => (
                <Card key={lead.id} className="bg-white/80 backdrop-blur-lg border-slate-200/60 hover:shadow-xl hover:shadow-slate-200/50 transition-all duration-300 hover:border-slate-300/60">
                  <CardContent className="p-6">
                    <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-4">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3 mb-2">
                              <div className="w-2 h-8 bg-gradient-to-b from-blue-600 to-indigo-600 rounded-full"></div>
                              <h3 className="text-xl font-bold text-slate-900 truncate">
                                {lead.company_name}
                              </h3>
                            </div>
                            {lead.industry && (
                              <span className="inline-flex items-center px-3 py-1 text-xs font-semibold bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 border border-blue-200/50 rounded-full">
                                {lead.industry}
                              </span>
                            )}
                          </div>
                          <span className={`inline-flex items-center px-3 py-1 text-xs font-semibold rounded-full self-start ${
                            lead.status === 'new' 
                              ? 'bg-gradient-to-r from-emerald-50 to-green-50 text-emerald-700 border border-emerald-200/50' 
                              : lead.status === 'contacted' 
                              ? 'bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 border border-blue-200/50' 
                              : lead.status === 'interested' 
                              ? 'bg-gradient-to-r from-purple-50 to-violet-50 text-purple-700 border border-purple-200/50' 
                              : 'bg-gradient-to-r from-slate-50 to-gray-50 text-slate-700 border border-slate-200/50'
                          }`}>
                            {lead.status}
                          </span>
                        </div>

                        {lead.services && (
                          <p className="text-slate-600 mb-4 leading-relaxed">
                            {lead.services}
                          </p>
                        )}

                        <div className="flex flex-wrap gap-4 text-sm">
                          {lead.website && (
                            <a
                              href={lead.website}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
                            >
                              <ExternalLink className="h-4 w-4" />
                              Website
                            </a>
                          )}
                          {lead.contact_email && (
                            <div className="inline-flex items-center gap-2 text-slate-600">
                              <Mail className="h-4 w-4" />
                              {lead.contact_email}
                            </div>
                          )}
                          <div className="inline-flex items-center gap-2 text-slate-500">
                            <Calendar className="h-4 w-4" />
                            Added {new Date(lead.created_at).toLocaleDateString()}
                          </div>
                        </div>

                        {lead.email_subject && (
                          <details className="mt-4 group">
                            <summary className="cursor-pointer text-sm font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-2 transition-colors">
                              <ChevronDown className="h-4 w-4 group-open:rotate-180 transition-transform" />
                              View generated email
                            </summary>
                            <div className="mt-3 p-4 bg-gradient-to-r from-slate-50 to-blue-50 rounded-lg border border-slate-200/60">
                              <div className="font-semibold text-slate-900 mb-2">
                                Subject: {lead.email_subject}
                              </div>
                              <div className="text-slate-700 whitespace-pre-wrap leading-relaxed">
                                {lead.email_body}
                              </div>
                            </div>
                          </details>
                        )}
                      </div>

                      <div className="flex flex-col gap-3 lg:ml-6 lg:flex-shrink-0 lg:min-w-[140px]">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => router.push(`/dashboard/leads/${lead.id}`)}
                          className="w-full border-slate-300 hover:bg-slate-50 hover:border-slate-400 transition-colors"
                        >
                          View Details
                        </Button>
                        {lead.contact_email && (
                          <Button 
                            size="sm"
                            onClick={() => handleSendEmail(lead.id)}
                            disabled={sendingEmail === lead.id || lead.status === 'contacted'}
                            className={`w-full transition-all duration-200 ${
                              emailSuccess === lead.id 
                                ? 'bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700' 
                                : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'
                            }`}
                          >
                            {sendingEmail === lead.id ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Sending...
                              </>
                            ) : emailSuccess === lead.id ? (
                              <>✓ Sent!</>
                            ) : lead.status === 'contacted' ? (
                              <>✓ Contacted</>
                            ) : (
                              <>
                                <Mail className="h-4 w-4 mr-2" />
                                Send Email
                              </>
                            )}
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  )
}
