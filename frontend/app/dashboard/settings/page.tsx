'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Settings, Key, Mail, Save, Eye, EyeOff, Check, AlertCircle } from 'lucide-react'

export default function SettingsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  
  // API Keys
  const [serpapiKey, setSerpapiKey] = useState('')
  const [hunterKey, setHunterKey] = useState('')
  const [aiProvider, setAiProvider] = useState<'ollama' | 'openai'>('ollama')
  const [openaiKey, setOpenaiKey] = useState('')
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434')
  const [ollamaModel, setOllamaModel] = useState('llama2')
  const [serpapiKeySet, setSerpapiKeySet] = useState(false)
  const [hunterKeySet, setHunterKeySet] = useState(false)
  const [openaiKeySet, setOpenaiKeySet] = useState(false)
  
  // Google Sheets
  const [googleSheetsEnabled, setGoogleSheetsEnabled] = useState(false)
  const [googleSheetsConfigured, setGoogleSheetsConfigured] = useState(false)
  const [googleSheetId, setGoogleSheetId] = useState('')
  const [googleCredentials, setGoogleCredentials] = useState('')
  
  // SMTP Settings
  const [smtpHost, setSmtpHost] = useState('')
  const [smtpPort, setSmtpPort] = useState('587')
  const [smtpUsername, setSmtpUsername] = useState('')
  const [smtpPassword, setSmtpPassword] = useState('')
  const [smtpFromEmail, setSmtpFromEmail] = useState('')
  const [smtpFromName, setSmtpFromName] = useState('')
  const [smtpPasswordSet, setSmtpPasswordSet] = useState(false)
  
  // Show password states
  const [showSerpapi, setShowSerpapi] = useState(false)
  const [showHunter, setShowHunter] = useState(false)
  const [showOpenai, setShowOpenai] = useState(false)
  const [showSmtpPassword, setShowSmtpPassword] = useState(false)
  const [testingSmtp, setTestingSmtp] = useState(false)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const response = await api.get('/api/settings/', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      const data = response.data
      setSerpapiKeySet(data.serpapi_key_set)
      setHunterKeySet(data.hunter_api_key_set)
      setAiProvider(data.ai_provider || 'ollama')
      setOpenaiKeySet(data.openai_api_key_set)
      setOllamaUrl(data.ollama_base_url || 'http://localhost:11434')
      setOllamaModel(data.ollama_model || 'llama2')
      setGoogleSheetsEnabled(data.google_sheets_enabled || false)
      setGoogleSheetsConfigured(data.google_sheets_configured || false)
      setGoogleSheetId(data.google_sheet_id || '')
      setSmtpHost(data.smtp_host || '')
      setSmtpPort(data.smtp_port?.toString() || '587')
      setSmtpUsername(data.smtp_username || '')
      setSmtpPasswordSet(data.smtp_password_set)
      setSmtpFromEmail(data.smtp_from_email || '')
      setSmtpFromName(data.smtp_from_name || '')
    } catch (error) {
      console.error('Failed to fetch settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveApiKeys = async () => {
    try {
      setSaving(true)
      const token = localStorage.getItem('token')
      const updates: any = {}
      
      if (serpapiKey) updates.serpapi_key = serpapiKey
      if (hunterKey) updates.hunter_api_key = hunterKey
      if (aiProvider) updates.ai_provider = aiProvider
      if (openaiKey) updates.openai_api_key = openaiKey
      if (ollamaUrl) updates.ollama_base_url = ollamaUrl
      if (ollamaModel) updates.ollama_model = ollamaModel
      
      await api.put('/api/settings/api-keys', updates, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      setMessage({ type: 'success', text: 'API keys saved successfully!' })
      setSerpapiKey('')
      setHunterKey('')
      setOpenaiKey('')
      await fetchSettings()
      
      setTimeout(() => setMessage(null), 3000)
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save API keys' })
      setTimeout(() => setMessage(null), 3000)
    } finally {
      setSaving(false)
    }
  }

  const saveSmtpSettings = async () => {
    try {
      setSaving(true)
      const token = localStorage.getItem('token')
      
      const updates: any = {
        smtp_host: smtpHost,
        smtp_port: parseInt(smtpPort),
        smtp_username: smtpUsername,
        smtp_from_email: smtpFromEmail,
        smtp_from_name: smtpFromName,
      }
      
      if (smtpPassword) {
        updates.smtp_password = smtpPassword
      }
      
      await api.put('/api/settings/smtp', updates, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      setMessage({ type: 'success', text: 'SMTP settings saved successfully!' })
      setSmtpPassword('')
      await fetchSettings()
      
      setTimeout(() => setMessage(null), 3000)
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save SMTP settings' })
      setTimeout(() => setMessage(null), 3000)
    } finally {
      setSaving(false)
    }
  }

  const testSmtpConnection = async () => {
    try {
      setTestingSmtp(true)
      const token = localStorage.getItem('token')
      
      await api.post('/api/emails/test-smtp', {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      setMessage({ type: 'success', text: 'SMTP connection successful! Emails can be sent.' })
      setTimeout(() => setMessage(null), 5000)
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'SMTP connection failed. Check your settings.' })
      setTimeout(() => setMessage(null), 5000)
    } finally {
      setTestingSmtp(false)
    }
  }

  const saveGoogleSheetsSettings = async () => {
    try {
      setSaving(true)
      const token = localStorage.getItem('token')
      const updates: any = {
        google_sheets_enabled: googleSheetsEnabled,
        google_sheet_id: googleSheetId,
      }
      
      if (googleCredentials) {
        updates.google_credentials = googleCredentials
      }
      
      await api.put('/api/settings/google-sheets', updates, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      setMessage({ type: 'success', text: 'Google Sheets settings saved successfully!' })
      setGoogleCredentials('')
      await fetchSettings()
      
      setTimeout(() => setMessage(null), 3000)
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save Google Sheets settings' })
      setTimeout(() => setMessage(null), 3000)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <div className="container mx-auto px-6 py-8 max-w-4xl">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-slate-600">Loading settings...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Professional Header */}
        <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200 shadow-sm mb-8 rounded-lg">
          <div className="px-6 py-4">
            <button
              onClick={() => router.push('/dashboard')}
              className="text-slate-600 hover:text-slate-900 mb-4 flex items-center gap-2 transition-colors"
            >
              ← Back to Dashboard
            </button>
            <div className="flex items-center gap-3">
              <div className="w-1 h-8 bg-gradient-to-b from-blue-600 to-indigo-600 rounded-full"></div>
              <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
                <Settings className="w-8 h-8" />
                Settings
              </h1>
            </div>
            <p className="text-slate-600 mt-2">Configure your API keys and integrations</p>
          </div>
        </header>

        {/* Success/Error Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-2 ${
            message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {message.type === 'success' ? <Check className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
            {message.text}
          </div>
        )}

        {/* API Keys Section */}
        <Card className="p-6 mb-6 bg-white shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <Key className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900">API Keys</h2>
          </div>
          
          <div className="space-y-4">
            {/* SerpAPI Key */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                SerpAPI Key {serpapiKeySet && <span className="text-green-600">(Configured ✓)</span>}
              </label>
              <p className="text-xs text-gray-500 mb-2">For Google search results. Get your key at <a href="https://serpapi.com" target="_blank" className="text-blue-600 hover:underline">serpapi.com</a></p>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Input
                    type={showSerpapi ? 'text' : 'password'}
                    value={serpapiKey}
                    onChange={(e) => setSerpapiKey(e.target.value)}
                    placeholder={serpapiKeySet ? "Enter new key to update" : "Enter your SerpAPI key"}
                    className="pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowSerpapi(!showSerpapi)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showSerpapi ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            {/* Hunter.io Key */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hunter.io API Key {hunterKeySet && <span className="text-green-600">(Configured ✓)</span>}
              </label>
              <p className="text-xs text-gray-500 mb-2">For finding email addresses. Get your key at <a href="https://hunter.io" target="_blank" className="text-blue-600 hover:underline">hunter.io</a></p>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Input
                    type={showHunter ? 'text' : 'password'}
                    value={hunterKey}
                    onChange={(e) => setHunterKey(e.target.value)}
                    placeholder={hunterKeySet ? "Enter new key to update" : "Enter your Hunter.io API key"}
                    className="pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowHunter(!showHunter)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showHunter ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            {/* AI Provider Selection */}
            <div className="col-span-2 border-t pt-4">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                AI Provider for Email Generation
              </label>
              <div className="flex gap-4 mb-4">
                <button
                  type="button"
                  onClick={() => setAiProvider('ollama')}
                  className={`flex-1 p-4 border-2 rounded-lg transition-all ${
                    aiProvider === 'ollama'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-semibold">🦙 Ollama (Local)</div>
                  <div className="text-xs text-gray-600 mt-1">Free, runs on your machine</div>
                </button>
                <button
                  type="button"
                  onClick={() => setAiProvider('openai')}
                  className={`flex-1 p-4 border-2 rounded-lg transition-all ${
                    aiProvider === 'openai'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-semibold">🤖 OpenAI</div>
                  <div className="text-xs text-gray-600 mt-1">Cloud-based, requires API key</div>
                </button>
              </div>

              {aiProvider === 'ollama' ? (
                <div className="space-y-3 bg-gray-50 p-4 rounded-lg">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Ollama Base URL
                    </label>
                    <Input
                      value={ollamaUrl}
                      onChange={(e) => setOllamaUrl(e.target.value)}
                      placeholder="http://localhost:11434"
                    />
                    <p className="text-xs text-gray-500 mt-1">Default: http://localhost:11434</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Model Name
                    </label>
                    <Input
                      value={ollamaModel}
                      onChange={(e) => setOllamaModel(e.target.value)}
                      placeholder="llama2"
                    />
                    <p className="text-xs text-gray-500 mt-1">Examples: llama2, mistral, codellama</p>
                  </div>
                  <div className="text-xs bg-blue-50 p-3 rounded">
                    <strong>Note:</strong> Make sure Ollama is installed and running. Visit <a href="https://ollama.ai" target="_blank" className="text-blue-600 hover:underline">ollama.ai</a> to download.
                  </div>
                </div>
              ) : (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    OpenAI API Key {openaiKeySet && <span className="text-green-600">(Configured ✓)</span>}
                  </label>
                  <p className="text-xs text-gray-500 mb-2">Get your key at <a href="https://platform.openai.com" target="_blank" className="text-blue-600 hover:underline">platform.openai.com</a></p>
                  <div className="relative">
                    <Input
                      type={showOpenai ? 'text' : 'password'}
                      value={openaiKey}
                      onChange={(e) => setOpenaiKey(e.target.value)}
                      placeholder={openaiKeySet ? "Enter new key to update" : "sk-..."}
                      className="pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowOpenai(!showOpenai)}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showOpenai ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          <Button
            onClick={saveApiKeys}
            disabled={saving}
            className="mt-6 bg-blue-600 hover:bg-blue-700"
          >
            <Save className="w-4 h-4 mr-2" />
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </Card>

        {/* Google Sheets Integration Section */}
        <Card className="p-6 mb-6 bg-white shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <span className="text-2xl">📊</span>
            <h2 className="text-2xl font-bold text-gray-900">Google Sheets Integration</h2>
          </div>
          
          <div className="mb-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={googleSheetsEnabled}
                onChange={(e) => setGoogleSheetsEnabled(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <span className="text-sm font-medium">
                Auto-export leads to Google Sheets {googleSheetsConfigured && <span className="text-green-600">(Configured ✓)</span>}
              </span>
            </label>
          </div>

          {googleSheetsEnabled && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Google Service Account Credentials (JSON)
                </label>
                <textarea
                  value={googleCredentials}
                  onChange={(e) => setGoogleCredentials(e.target.value)}
                  placeholder='{"type": "service_account", "project_id": "...", ...}'
                  rows={4}
                  className="w-full px-3 py-2 border rounded-lg font-mono text-xs"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Create a service account in Google Cloud Console and paste the JSON here.
                  <a href="https://console.cloud.google.com/iam-admin/serviceaccounts" target="_blank" className="text-blue-600 hover:underline ml-1">Create Service Account →</a>
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Google Sheet ID (Optional)
                </label>
                <Input
                  value={googleSheetId}
                  onChange={(e) => setGoogleSheetId(e.target.value)}
                  placeholder="Leave empty to create new sheet automatically"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Found in the sheet URL: docs.google.com/spreadsheets/d/<strong>SHEET_ID</strong>/edit
                </p>
              </div>

              <Button
                onClick={saveGoogleSheetsSettings}
                disabled={saving || !googleCredentials}
                className="bg-green-600 hover:bg-green-700"
              >
                <Save className="w-4 h-4 mr-2" />
                {saving ? 'Saving...' : 'Save Google Sheets Settings'}
              </Button>
            </div>
          )}
        </Card>

        {/* SMTP Settings Section */}
        <Card className="p-6 bg-white shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <Mail className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900">Email Settings (SMTP)</h2>
          </div>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Host</label>
                <Input
                  value={smtpHost}
                  onChange={(e) => setSmtpHost(e.target.value)}
                  placeholder="smtp.gmail.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Port</label>
                <Input
                  type="number"
                  value={smtpPort}
                  onChange={(e) => setSmtpPort(e.target.value)}
                  placeholder="587"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Username</label>
              <Input
                value={smtpUsername}
                onChange={(e) => setSmtpUsername(e.target.value)}
                placeholder="your-email@gmail.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                SMTP Password {smtpPasswordSet && <span className="text-green-600">(Configured ✓)</span>}
              </label>
              <div className="relative">
                <Input
                  type={showSmtpPassword ? 'text' : 'password'}
                  value={smtpPassword}
                  onChange={(e) => setSmtpPassword(e.target.value)}
                  placeholder={smtpPasswordSet ? "Enter new password to update" : "Your email password or app password"}
                  className="pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowSmtpPassword(!showSmtpPassword)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showSmtpPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">From Email</label>
              <Input
                value={smtpFromEmail}
                onChange={(e) => setSmtpFromEmail(e.target.value)}
                placeholder="your-email@gmail.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">From Name</label>
              <Input
                value={smtpFromName}
                onChange={(e) => setSmtpFromName(e.target.value)}
                placeholder="Your Company Name"
              />
            </div>
          </div>

          <Button
            onClick={saveSmtpSettings}
            disabled={saving || !smtpHost || !smtpUsername || !smtpFromEmail}
            className="mt-6 bg-blue-600 hover:bg-blue-700"
          >
            <Save className="w-4 h-4 mr-2" />
            {saving ? 'Saving...' : 'Save SMTP Settings'}
          </Button>

          <Button
            onClick={testSmtpConnection}
            disabled={testingSmtp || !smtpHost || !smtpUsername || !smtpFromEmail}
            variant="outline"
            className="mt-4 ml-4"
          >
            {testingSmtp ? 'Testing...' : 'Test SMTP Connection'}
          </Button>

          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Gmail users:</strong> Use an <a href="https://support.google.com/accounts/answer/185833" target="_blank" className="underline">App Password</a> instead of your regular password.
            </p>
          </div>
        </Card>
      </div>
    </div>
  )
}
