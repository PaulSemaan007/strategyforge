'use client'

import { useState, useRef, useEffect } from 'react'
import { Play, Square, Users, MessageSquare, Clock, ChevronRight, AlertCircle, Wifi, WifiOff } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

interface AgentMessage {
  agent: string
  content: string
  turn: number
  timestamp: string
}

// Demo simulation data (fallback when API unavailable)
const DEMO_MESSAGES: AgentMessage[] = [
  {
    agent: 'blue_commander',
    turn: 1,
    timestamp: '00:00:15',
    content: `**SITUATION ASSESSMENT**

Current disposition shows Red Force naval assets concentrated at Grid ML-0501, approximately 180km from our forward positions. Intelligence indicates 3 destroyer groups and 2 submarine contacts.

**RECOMMENDED ACTION**

1. Establish Combat Air Patrol (CAP) over Grid TS-2500 with 4x F-16 fighters
2. Position ASW assets along the 150km line to detect submarine infiltration
3. Maintain EMCON (emissions control) to avoid revealing our defensive posture

**RATIONALE**

By establishing CAP at the midpoint, we achieve 200km early warning coverage while preserving fuel for sustained operations. ASW positioning creates a layered defense against submarine threats.

**RISK ASSESSMENT**

- Medium risk of Red air probes within 12 hours
- Low risk of amphibious action (insufficient lift capacity observed)
- High value of maintaining air superiority for follow-on operations`
  },
  {
    agent: 'red_commander',
    turn: 1,
    timestamp: '00:01:32',
    content: `**OPERATIONAL ASSESSMENT**

Blue Force has established predictable patrol patterns. Their CAP rotations create a 15-minute gap during shift changes at approximately 0600 and 1800 hours.

**PROPOSED ACTION**

1. Launch diversionary air group toward Grid TS-3000 to draw Blue CAP south
2. Position submarine assets at Grid TS-1800 for potential strike corridor
3. Prepare electronic warfare assets for communications jamming

**TACTICAL ADVANTAGE**

Blue's reliance on active radar creates vulnerability to anti-radiation missiles. Recommend SEAD package preparation for Phase 2.

**EXPECTED BLUE RESPONSE**

Blue will likely reinforce CAP and may attempt ASW sweep. This creates opportunity for feint operations.`
  },
  {
    agent: 'analyst',
    turn: 1,
    timestamp: '00:02:45',
    content: `**STRATEGIC ASSESSMENT - TURN 1**

**Force Balance:**
- Air Domain: Blue advantage (7.2/10) - Superior fighter coverage
- Maritime Domain: Contested (5.5/10) - Red submarine threat significant
- Information Domain: Red advantage (6.8/10) - Better SIGINT positioning

**Key Observations:**
1. Both commanders demonstrate sound tactical reasoning
2. Blue's defensive posture is appropriate given force ratios
3. Red's identification of CAP gaps shows good intelligence analysis

**Critical Decision Point:**
Within 6-12 hours based on Red's diversionary timeline. Blue should consider randomizing patrol schedules.

**Evaluation Metrics:**
- Blue Geospatial Accuracy: 85% (correct distance calculations)
- Red Strategic Coherence: 82% (logical action sequence)
- Overall Turn Score: 78%`
  }
]

export default function SimulationPage() {
  const [isRunning, setIsRunning] = useState(false)
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [currentTurn, setCurrentTurn] = useState(0)
  const [scenario, setScenario] = useState('taiwan_strait')
  const [maxTurns, setMaxTurns] = useState(3)
  const [error, setError] = useState<string | null>(null)
  const [useDemo, setUseDemo] = useState(false)
  const [apiConnected, setApiConnected] = useState<boolean | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Check API connectivity on mount
  useEffect(() => {
    const checkApi = async () => {
      try {
        const res = await fetch(`${API_URL}/`, { method: 'GET' })
        setApiConnected(res.ok)
      } catch {
        setApiConnected(false)
      }
    }
    checkApi()
  }, [])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startSimulation = async () => {
    setIsRunning(true)
    setMessages([])
    setCurrentTurn(1)
    setError(null)

    // If API not connected, use demo mode
    if (!apiConnected) {
      runDemoSimulation()
      return
    }

    try {
      // Start simulation via API
      const response = await fetch(`${API_URL}/api/simulation/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario,
          turns: maxTurns,
          model: 'llama3.1:8b'
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const { job_id } = await response.json()

      // Connect to SSE stream
      const eventSource = new EventSource(`${API_URL}/api/simulation/${job_id}/stream`)
      eventSourceRef.current = eventSource

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === 'message' && data.agent && data.content) {
            setMessages(prev => [...prev, {
              agent: data.agent,
              content: data.content,
              turn: data.turn || currentTurn,
              timestamp: data.timestamp || new Date().toLocaleTimeString()
            }])
            if (data.turn) {
              setCurrentTurn(data.turn)
            }
          } else if (data.type === 'status' && data.status === 'completed') {
            setIsRunning(false)
            eventSource.close()
          } else if (data.type === 'error') {
            setError(data.message || 'Simulation error')
            setIsRunning(false)
            eventSource.close()
          }
        } catch (e) {
          console.error('Failed to parse SSE message:', e)
        }
      }

      eventSource.onerror = (e) => {
        console.error('SSE connection error:', e)
        // Don't show error if simulation completed normally
        if (isRunning) {
          setError('Connection lost. The simulation may still be running on the server.')
        }
        setIsRunning(false)
        eventSource.close()
      }

    } catch (e) {
      console.error('Failed to start simulation:', e)
      setError(`Failed to connect to API. Running demo mode instead.`)
      runDemoSimulation()
    }
  }

  const runDemoSimulation = () => {
    setUseDemo(true)
    setMessages([])
    setCurrentTurn(1)

    // Simulate messages appearing over time
    DEMO_MESSAGES.forEach((msg, i) => {
      setTimeout(() => {
        setMessages(prev => [...prev, msg])
        setCurrentTurn(msg.turn)
      }, (i + 1) * 2000)
    })

    // End simulation
    setTimeout(() => {
      setIsRunning(false)
      setUseDemo(false)
    }, DEMO_MESSAGES.length * 2000 + 1000)
  }

  const stopSimulation = () => {
    setIsRunning(false)
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
  }

  const getAgentColor = (agent: string): string => {
    switch (agent) {
      case 'blue_commander': return 'border-blue-500 bg-blue-500/10'
      case 'red_commander': return 'border-red-500 bg-red-500/10'
      case 'analyst': return 'border-green-500 bg-green-500/10'
      default: return 'border-slate-500 bg-slate-500/10'
    }
  }

  const getAgentLabel = (agent: string): string => {
    switch (agent) {
      case 'blue_commander': return 'BLUE COMMANDER'
      case 'red_commander': return 'RED COMMANDER'
      case 'analyst': return 'ANALYST'
      default: return agent.toUpperCase()
    }
  }

  const getAgentTextColor = (agent: string): string => {
    switch (agent) {
      case 'blue_commander': return 'text-blue-400'
      case 'red_commander': return 'text-red-400'
      case 'analyst': return 'text-green-400'
      default: return 'text-slate-400'
    }
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-slate-700/50 bg-slate-900/50">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold text-white">Wargaming Simulation</h1>
            <p className="text-sm text-slate-400">Multi-agent turn-based simulation powered by LangGraph</p>
          </div>

          <div className="flex items-center gap-4">
            {/* API Status Indicator */}
            <div className="flex items-center gap-2 text-sm">
              {apiConnected === null ? (
                <span className="text-slate-500">Checking API...</span>
              ) : apiConnected ? (
                <span className="flex items-center gap-1 text-green-400">
                  <Wifi size={14} />
                  API Connected
                </span>
              ) : (
                <span className="flex items-center gap-1 text-yellow-400">
                  <WifiOff size={14} />
                  Demo Mode
                </span>
              )}
            </div>

            <div className="flex items-center gap-2">
              <label className="text-sm text-slate-400">Scenario:</label>
              <select
                value={scenario}
                onChange={e => setScenario(e.target.value)}
                disabled={isRunning}
                className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded text-white text-sm"
              >
                <option value="taiwan_strait">Taiwan Strait</option>
                <option value="eastern_europe" disabled>Eastern Europe (Coming Soon)</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <label className="text-sm text-slate-400">Turns:</label>
              <input
                type="number"
                value={maxTurns}
                onChange={e => setMaxTurns(parseInt(e.target.value) || 3)}
                disabled={isRunning}
                min={1}
                max={10}
                className="w-16 px-2 py-1.5 bg-slate-800 border border-slate-700 rounded text-white text-sm"
              />
            </div>

            {!isRunning ? (
              <button
                onClick={startSimulation}
                className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg flex items-center gap-2 transition-colors"
              >
                <Play size={16} />
                Start Simulation
              </button>
            ) : (
              <button
                onClick={stopSimulation}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg flex items-center gap-2 transition-colors"
              >
                <Square size={16} />
                Stop
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-3 bg-red-900/50 border-b border-red-700 flex items-center gap-2 text-red-200">
          <AlertCircle size={16} />
          <span className="text-sm">{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-400 hover:text-red-200"
          >
            ×
          </button>
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        {/* Message Feed */}
        <div className="flex-1 p-4 overflow-auto">
          {messages.length === 0 && !isRunning ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <Users size={48} className="mx-auto text-slate-600 mb-4" />
                <h2 className="text-xl font-medium text-slate-400 mb-2">No Simulation Running</h2>
                <p className="text-slate-500 mb-4">
                  Click "Start Simulation" to begin the wargaming exercise
                </p>
                <p className="text-sm text-slate-600">
                  Agents: Blue Commander, Red Commander, Analyst
                </p>
                {!apiConnected && (
                  <p className="text-sm text-yellow-500 mt-4">
                    Note: API not connected. Will run in demo mode.
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="space-y-4 max-w-4xl mx-auto">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`p-4 rounded-lg border-l-4 ${getAgentColor(msg.agent)}`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className={`font-bold ${getAgentTextColor(msg.agent)}`}>
                      {getAgentLabel(msg.agent)}
                    </span>
                    <div className="flex items-center gap-3 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <Clock size={12} />
                        {msg.timestamp}
                      </span>
                      <span>Turn {msg.turn}</span>
                    </div>
                  </div>
                  <div className="text-slate-300 text-sm whitespace-pre-wrap leading-relaxed">
                    {msg.content.split('\n').map((line, j) => {
                      if (line.startsWith('**') && line.endsWith('**')) {
                        return (
                          <div key={j} className="font-bold text-white mt-3 mb-1">
                            {line.replace(/\*\*/g, '')}
                          </div>
                        )
                      }
                      if (line.startsWith('- ')) {
                        return (
                          <div key={j} className="flex items-start gap-2 ml-2">
                            <ChevronRight size={14} className="mt-0.5 text-slate-500" />
                            <span>{line.substring(2)}</span>
                          </div>
                        )
                      }
                      if (line.match(/^\d+\./)) {
                        return (
                          <div key={j} className="ml-2 my-1">{line}</div>
                        )
                      }
                      if (line.startsWith('### ')) {
                        return (
                          <div key={j} className="font-bold text-white mt-3 mb-1">
                            {line.replace(/^### /, '')}
                          </div>
                        )
                      }
                      return <div key={j}>{line}</div>
                    })}
                  </div>
                </div>
              ))}

              {isRunning && (
                <div className="flex items-center gap-3 text-slate-400 p-4">
                  <div className="animate-pulse flex gap-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  <span>{useDemo ? 'Loading demo data...' : 'Agents reasoning with Ollama...'}</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="w-72 p-4 border-l border-slate-700/50 bg-slate-900/30">
          {/* Status */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-white mb-3">Simulation Status</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Status</span>
                <span className={isRunning ? 'text-green-400' : 'text-slate-500'}>
                  {isRunning ? 'Running' : 'Idle'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Current Turn</span>
                <span className="text-white">{currentTurn} / {maxTurns}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Messages</span>
                <span className="text-white">{messages.length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Mode</span>
                <span className={apiConnected ? 'text-green-400' : 'text-yellow-400'}>
                  {apiConnected ? 'Live AI' : 'Demo'}
                </span>
              </div>
            </div>
          </div>

          {/* Agents */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-white mb-3">Active Agents</h3>
            <div className="space-y-2">
              <AgentStatus name="Blue Commander" color="blue" active={isRunning} />
              <AgentStatus name="Red Commander" color="red" active={isRunning} />
              <AgentStatus name="Analyst" color="green" active={isRunning} />
            </div>
          </div>

          {/* Model Info */}
          <div>
            <h3 className="text-sm font-medium text-white mb-3">Model Configuration</h3>
            <div className="bg-slate-800/50 rounded-lg p-3 text-sm">
              <div className="flex justify-between mb-2">
                <span className="text-slate-400">Model</span>
                <span className="text-white">llama3.1:8b</span>
              </div>
              <div className="flex justify-between mb-2">
                <span className="text-slate-400">Temperature</span>
                <span className="text-white">0.7</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Framework</span>
                <span className="text-white">LangGraph</span>
              </div>
            </div>
          </div>

          {/* Connection Info */}
          <div className="mt-6 p-3 bg-slate-800/30 rounded-lg text-xs text-slate-500">
            <p>API: {API_URL}</p>
            <p className="mt-1">
              {apiConnected
                ? 'Connected to backend. Using real LLM responses.'
                : 'Backend not available. Using demo data.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function AgentStatus({
  name,
  color,
  active,
}: {
  name: string
  color: string
  active: boolean
}) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-500',
    red: 'bg-red-500',
    green: 'bg-green-500',
  }

  return (
    <div className="flex items-center gap-3 p-2 bg-slate-800/30 rounded">
      <div className={`w-2 h-2 rounded-full ${colors[color]} ${active ? 'animate-pulse' : 'opacity-50'}`} />
      <span className="text-sm text-slate-300">{name}</span>
      <MessageSquare size={14} className="ml-auto text-slate-500" />
    </div>
  )
}
