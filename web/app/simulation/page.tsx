'use client'

import { useState, useRef, useEffect } from 'react'
import { Play, Square, Users, MessageSquare, Clock, ChevronRight, AlertCircle, Wifi, WifiOff, Map as MapIcon } from 'lucide-react'
import dynamic from 'next/dynamic'

// Dynamically import the map component to avoid SSR issues
const SimulationMap = dynamic(() => import('@/components/SimulationMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-slate-900 flex items-center justify-center">
      <div className="text-slate-500">Loading map...</div>
    </div>
  ),
})

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

interface AgentMessage {
  agent: string
  content: string
  turn: number
  timestamp: string
  tools_used?: string[]
}

interface UnitPosition {
  id: string
  name: string
  lat: number
  lon: number
  status: string
}

// Demo simulation data (fallback when API unavailable)
const DEMO_MESSAGES: AgentMessage[] = [
  {
    agent: 'blue_commander',
    turn: 1,
    timestamp: '00:00:15',
    tools_used: ['get_distance', 'analyze_terrain'],
    content: `**SITUATION ASSESSMENT**

Using geospatial tools, I've calculated Red Force naval assets are exactly 178.3km from our forward positions at Grid ML-0501. Terrain analysis shows the strait provides limited concealment for approaching vessels.

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
    tools_used: ['estimate_force_transit', 'check_weapon_range'],
    content: `**OPERATIONAL ASSESSMENT**

Transit time calculations show our naval forces can reach striking distance in 3.6 hours at cruise speed. Weapon range analysis confirms our anti-ship missiles can engage from current positions.

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
    tools_used: ['get_distance', 'analyze_terrain'],
    content: `**STRATEGIC ASSESSMENT - TURN 1**

Verified distance calculations from both commanders using geospatial tools.

**Force Balance:**
- Air Domain: Blue advantage (7.2/10) - Superior fighter coverage
- Maritime Domain: Contested (5.5/10) - Red submarine threat significant
- Information Domain: Red advantage (6.8/10) - Better SIGINT positioning

**Key Observations:**
1. Both commanders used accurate geospatial data in their analysis
2. Blue's defensive posture is appropriate given force ratios
3. Red's transit time calculations align with doctrine

**Critical Decision Point:**
Within 6-12 hours based on Red's diversionary timeline. Blue should consider randomizing patrol schedules.

**Evaluation Metrics:**
- Blue Geospatial Accuracy: 95% (verified tool usage)
- Red Strategic Coherence: 88% (logical action sequence)
- Overall Turn Score: 85%`
  }
]

// Demo initial unit positions (for demo mode)
const DEMO_BLUE_UNITS: UnitPosition[] = [
  { id: 'blue-cvn-1', name: 'USS Ronald Reagan', lat: 24.8, lon: 122.0, status: 'ready' },
  { id: 'blue-ddg-1', name: 'USS Barry', lat: 24.6, lon: 121.8, status: 'ready' },
  { id: 'blue-ddg-2', name: 'USS Mustin', lat: 25.0, lon: 121.9, status: 'ready' },
]

const DEMO_RED_UNITS: UnitPosition[] = [
  { id: 'red-cv-1', name: 'Liaoning', lat: 24.5, lon: 118.5, status: 'ready' },
  { id: 'red-ddg-1', name: 'Type 055 Nanchang', lat: 24.3, lon: 118.8, status: 'ready' },
  { id: 'red-sub-1', name: 'Type 093 SSN', lat: 24.0, lon: 119.0, status: 'ready' },
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
  const [showMap, setShowMap] = useState(true)
  const [blueUnits, setBlueUnits] = useState<UnitPosition[]>(DEMO_BLUE_UNITS)
  const [redUnits, setRedUnits] = useState<UnitPosition[]>(DEMO_RED_UNITS)
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
              timestamp: data.timestamp || new Date().toLocaleTimeString(),
              tools_used: data.tools_used || []
            }])
            if (data.turn) {
              setCurrentTurn(data.turn)
            }
          } else if (data.type === 'position_update') {
            // Handle position updates from agents
            if (data.force === 'blue' && data.units) {
              setBlueUnits(data.units)
            } else if (data.force === 'red' && data.units) {
              setRedUnits(data.units)
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
    // Reset to initial positions
    setBlueUnits(DEMO_BLUE_UNITS)
    setRedUnits(DEMO_RED_UNITS)

    // Simulate messages appearing over time with unit movements
    DEMO_MESSAGES.forEach((msg, i) => {
      setTimeout(() => {
        setMessages(prev => [...prev, msg])
        setCurrentTurn(msg.turn)

        // Simulate unit movement based on agent
        if (msg.agent === 'blue_commander') {
          setBlueUnits(prev => prev.map(unit => ({
            ...unit,
            lat: unit.lat + (Math.random() - 0.5) * 0.02,
            lon: unit.lon - 0.02 - Math.random() * 0.01 // Move west toward strait
          })))
        } else if (msg.agent === 'red_commander') {
          setRedUnits(prev => prev.map(unit => ({
            ...unit,
            lat: unit.lat + (Math.random() - 0.5) * 0.02,
            lon: unit.lon + 0.02 + Math.random() * 0.01 // Move east toward strait
          })))
        }
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

            {/* Map Toggle */}
            <button
              onClick={() => setShowMap(!showMap)}
              className={`px-3 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                showMap
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              <MapIcon size={16} />
              {showMap ? 'Hide Map' : 'Show Map'}
            </button>

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
        {/* Main Content Area - Split View */}
        <div className={`flex-1 flex ${showMap ? 'flex-col lg:flex-row' : ''} overflow-hidden`}>
          {/* Map Panel */}
          {showMap && (
            <div className="lg:w-1/2 h-64 lg:h-full border-b lg:border-b-0 lg:border-r border-slate-700/50">
              <SimulationMap
                blueUnits={blueUnits}
                redUnits={redUnits}
                isRunning={isRunning}
              />
            </div>
          )}

          {/* Message Feed */}
          <div className={`${showMap ? 'lg:w-1/2' : 'w-full'} flex-1 p-4 overflow-auto`}>
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
                  {showMap && (
                    <p className="text-sm text-blue-400 mt-4">
                      Map shows initial unit positions. Watch them move during simulation!
                    </p>
                  )}
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
                    <div className="flex items-center gap-3">
                      <span className={`font-bold ${getAgentTextColor(msg.agent)}`}>
                        {getAgentLabel(msg.agent)}
                      </span>
                      {msg.tools_used && msg.tools_used.length > 0 && (
                        <div className="flex items-center gap-1.5">
                          {msg.tools_used.map((tool, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 text-xs bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded"
                              title={`Used ${tool} tool`}
                            >
                              🔧 {tool}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
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
