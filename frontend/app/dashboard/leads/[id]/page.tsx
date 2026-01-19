'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowLeft, ExternalLink, Mail, Loader2, Edit, Trash2 } from 'lucide-react'
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
  portfolio_path?: string
  status: string
  created_at: string
}

export default function LeadDetailPage() {
  const router = useRouter()
  const params = useParams() ?? {};
  const leadId = (params as any)?.id as string;

  const [loading, setLoading] = useState(true)
  const [lead, setLead] = useState<Lead | null>(null)
  const [error, setError] = useState('')
  const [sendingEmail, setSendingEmail] = useState(false)
  const [emailSuccess, setEmailSuccess] = useState(false)

  const fetchLead = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        router.push('/auth/login')
        return
      }

      const response = await api.get(
        `/api/leads/${leadId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      setLead(response.data)
    } catch (err: any) {
      console.error('Error fetching lead:', err)
      setError(err.response?.data?.detail || 'Failed to load lead details')
    } finally {
      setLoading(false)
    }
  }, [leadId, router])

  useEffect(() => {
    fetchLead()
  }, [fetchLead])

  const handleSendEmail = async () => {
    if (!lead?.contact_email) return

    setSendingEmail(true)
    setEmailSuccess(false)

    try {
      const token = localStorage.getItem('token')
      await api.post(
        `/api/leads/${leadId}/send-email`,
        {},
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )

      setEmailSuccess(true)
      // Refresh lead to update status
      await fetchLead()

      setTimeout(() => setEmailSuccess(false), 3000)
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to send email'
      alert(errorMessage)
    } finally {
      setSendingEmail(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this lead? This action cannot be undone.')) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      await api.delete(
        `/api/leads/${leadId}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )

      router.push('/dashboard/leads')
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete lead'
      alert(errorMessage)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <div className="container mx-auto px-6 py-8 max-w-4xl">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-slate-600">Loading lead details...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error || !lead) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <div className="container mx-auto px-6 py-8 max-w-4xl">
          <Link href="/dashboard/leads" className="inline-flex items-center text-sm text-slate-600 hover:text-slate-900 mb-4 transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Leads
          </Link>
          <Card className="bg-white/80 backdrop-blur-lg border-slate-200/60">
            <CardContent className="py-12">
              <div className="text-center">
                <div className="text-6xl mb-4">❌</div>
                <h3 className="text-xl font-semibold mb-2 text-slate-900">Error Loading Lead</h3>
                <p className="text-slate-600 mb-4">{error || 'Lead not found'}</p>
                <Button onClick={() => router.push('/dashboard/leads')} className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700">
                  Back to Leads
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Professional Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200 shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <Link href="/dashboard/leads" className="inline-flex items-center text-sm text-slate-600 hover:text-slate-900 transition-colors">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Leads
          </Link>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-4xl">
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-1 h-8 bg-gradient-to-b from-blue-600 to-indigo-600 rounded-full"></div>
              <h1 className="text-3xl font-bold text-slate-900">{lead.company_name}</h1>
            </div>
            <p className="text-slate-600">
              Lead details and contact information
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={handleDelete} className="border-slate-300 hover:bg-slate-50">
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Lead
            </Button>
            {lead.contact_email && (
              <Button
                onClick={handleSendEmail}
                disabled={sendingEmail || lead.status === 'contacted'}
                className={`transition-all duration-200 ${
                  emailSuccess 
                    ? 'bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700' 
                    : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'
                }`}
              >
                {sendingEmail ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Sending...
                  </>
                ) : emailSuccess ? (
                  <>✓ Email Sent!</>
                ) : lead.status === 'contacted' ? (
                  <>✓ Already Contacted</>
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

        <div className="grid gap-6">
          {/* Basic Information */}
          <Card className="bg-white/80 backdrop-blur-lg border-slate-200/60 shadow-lg">
            <CardHeader>
              <CardTitle className="text-slate-900">Company Information</CardTitle>
              <CardDescription className="text-slate-600">Basic details about this lead</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-slate-500">Company Name</label>
                  <p className="text-lg font-semibold text-slate-900">{lead.company_name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-500">Status</label>
                  <span className={`inline-flex items-center px-3 py-1 text-sm font-semibold rounded-full ${
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
                {lead.industry && (
                  <div>
                    <label className="text-sm font-medium text-slate-500">Industry</label>
                    <p className="text-slate-700">{lead.industry}</p>
                  </div>
                )}
                <div>
                  <label className="text-sm font-medium text-slate-500">Added</label>
                  <p className="text-slate-700">{new Date(lead.created_at).toLocaleDateString()}</p>
                </div>
              </div>

              {lead.services && (
                <div>
                  <label className="text-sm font-medium text-slate-500">Services</label>
                  <p className="mt-1 text-slate-700">{lead.services}</p>
                </div>
              )}

              <div className="flex gap-4">
                {lead.website && (
                  <a
                    href={lead.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
                  >
                    <ExternalLink className="h-4 w-4" />
                    Visit Website
                  </a>
                )}
                {lead.contact_email && (
                  <div className="flex items-center gap-2 text-slate-600">
                    <Mail className="h-4 w-4" />
                    {lead.contact_email}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Generated Email */}
          {lead.email_subject && lead.email_body && (
            <Card className="bg-white/80 backdrop-blur-lg border-slate-200/60 shadow-lg">
              <CardHeader>
                <CardTitle className="text-slate-900">Generated Email</CardTitle>
                <CardDescription className="text-slate-600">AI-generated email content for this lead</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-gradient-to-r from-slate-50 to-blue-50 p-4 rounded-lg border border-slate-200/60">
                  <div className="font-semibold text-lg mb-3 text-slate-900">
                    Subject: {lead.email_subject}
                  </div>
                  <div className="text-sm whitespace-pre-wrap leading-relaxed text-slate-700">
                    {lead.email_body}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Portfolio */}
          {lead.portfolio_path && (
            <Card className="bg-white/80 backdrop-blur-lg border-slate-200/60 shadow-lg">
              <CardHeader>
                <CardTitle className="text-slate-900">Generated Portfolio</CardTitle>
                <CardDescription className="text-slate-600">Custom portfolio created for this lead</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-gradient-to-r from-slate-50 to-blue-50 p-4 rounded-lg border border-slate-200/60">
                  <p className="text-sm text-slate-600 mb-3">
                    Portfolio generated and saved at: {lead.portfolio_path}
                  </p>
                  <Button variant="outline" size="sm" className="border-slate-300 hover:bg-slate-50">
                    View Portfolio
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}