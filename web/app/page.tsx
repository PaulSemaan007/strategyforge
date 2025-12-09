'use client'

import { useEffect, useState } from 'react'
import { Map, Target, Users, Zap, ArrowRight, BarChart3, Play } from 'lucide-react'
import Link from 'next/link'

interface Scenario {
  id: string
  name: string
  region: string
  description: string
  blue_units: number
  red_units: number
  objectives: number
  available: boolean
}

interface EvaluationSummary {
  overall_percentage: number
  category_scores: Record<string, number>
}

export default function Dashboard() {
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [demoEval, setDemoEval] = useState<EvaluationSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch scenarios
    fetch('/api/scenarios')
      .then(res => res.json())
      .then(data => setScenarios(data.scenarios || []))
      .catch(() => {
        // Use demo data if API not available
        setScenarios([
          {
            id: 'taiwan_strait',
            name: 'Taiwan Strait Crisis',
            region: 'Indo-Pacific',
            description: 'Naval and air operations in the Taiwan Strait',
            blue_units: 8,
            red_units: 9,
            objectives: 5,
            available: true
          }
        ])
      })

    // Fetch demo evaluation
    fetch('/api/demo/evaluation')
      .then(res => res.json())
      .then(data => setDemoEval(data))
      .catch(() => {
        setDemoEval({
          overall_percentage: 54.2,
          category_scores: {
            geospatial: 0.511,
            strategic: 0.656,
            adversarial: 0.417
          }
        })
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Welcome to StrategyForge</h1>
        <p className="text-slate-400">
          Multi-Agent Wargaming Evaluation System powered by LangGraph + Ollama
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon={<Map className="text-blue-400" />}
          label="Active Scenarios"
          value={scenarios.filter(s => s.available).length.toString()}
        />
        <StatCard
          icon={<Users className="text-purple-400" />}
          label="Total Units"
          value={scenarios.reduce((acc, s) => acc + s.blue_units + s.red_units, 0).toString()}
        />
        <StatCard
          icon={<Target className="text-green-400" />}
          label="Objectives"
          value={scenarios.reduce((acc, s) => acc + s.objectives, 0).toString()}
        />
        <StatCard
          icon={<Zap className="text-yellow-400" />}
          label="Model"
          value="Llama 3.1"
        />
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scenarios */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Map size={20} className="text-blue-400" />
            Available Scenarios
          </h2>

          {loading ? (
            <div className="animate-pulse space-y-3">
              <div className="h-24 bg-slate-700/50 rounded-lg" />
            </div>
          ) : (
            <div className="space-y-3">
              {scenarios.map(scenario => (
                <div
                  key={scenario.id}
                  className={`p-4 rounded-lg border ${
                    scenario.available
                      ? 'bg-slate-700/30 border-slate-600/50 hover:bg-slate-700/50 cursor-pointer'
                      : 'bg-slate-800/30 border-slate-700/30 opacity-60'
                  } transition-colors`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-white">{scenario.name}</h3>
                      <p className="text-sm text-slate-400">{scenario.region}</p>
                    </div>
                    {scenario.available ? (
                      <span className="px-2 py-1 text-xs bg-green-500/20 text-green-400 rounded">
                        Ready
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs bg-slate-500/20 text-slate-400 rounded">
                        Coming Soon
                      </span>
                    )}
                  </div>
                  <div className="mt-3 flex gap-4 text-xs text-slate-500">
                    <span className="text-blue-400">{scenario.blue_units} Blue</span>
                    <span className="text-red-400">{scenario.red_units} Red</span>
                    <span>{scenario.objectives} Objectives</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          <Link
            href="/map"
            className="mt-4 flex items-center justify-center gap-2 w-full py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
          >
            View Tactical Map <ArrowRight size={16} />
          </Link>
        </div>

        {/* Evaluation Overview */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <BarChart3 size={20} className="text-purple-400" />
            LLM Evaluation Results
          </h2>

          {demoEval && (
            <>
              <div className="mb-6">
                <div className="flex items-end gap-2 mb-2">
                  <span className="text-4xl font-bold text-white">
                    {demoEval.overall_percentage.toFixed(1)}%
                  </span>
                  <span className="text-slate-400 mb-1">Overall Score</span>
                </div>
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                    style={{ width: `${demoEval.overall_percentage}%` }}
                  />
                </div>
              </div>

              <div className="space-y-3">
                {Object.entries(demoEval.category_scores).map(([cat, score]) => (
                  <CategoryScore key={cat} category={cat} score={score} />
                ))}
              </div>
            </>
          )}

          <Link
            href="/evaluation"
            className="mt-4 flex items-center justify-center gap-2 w-full py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors"
          >
            View Details <ArrowRight size={16} />
          </Link>
        </div>

        {/* Quick Actions */}
        <div className="lg:col-span-2 bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
          <h2 className="text-lg font-semibold text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <ActionCard
              href="/simulation"
              icon={<Play className="text-green-400" />}
              title="Run Simulation"
              description="Start a new wargaming simulation with AI agents"
            />
            <ActionCard
              href="/evaluation"
              icon={<BarChart3 className="text-purple-400" />}
              title="Run Benchmark"
              description="Evaluate LLM capabilities against test suites"
            />
            <ActionCard
              href="/map"
              icon={<Map className="text-blue-400" />}
              title="View Map"
              description="Interactive tactical map with unit positions"
            />
          </div>
        </div>
      </div>

      {/* Tech Stack */}
      <div className="mt-8 text-center text-slate-500 text-sm">
        <p>Built with LangGraph | Ollama (Llama 3.1) | FastAPI | Next.js</p>
        <p className="mt-1">Designed for Anduril Thunderforge Team</p>
      </div>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700/50">
      <div className="flex items-center gap-3">
        {icon}
        <div>
          <p className="text-2xl font-bold text-white">{value}</p>
          <p className="text-xs text-slate-400">{label}</p>
        </div>
      </div>
    </div>
  )
}

function CategoryScore({ category, score }: { category: string; score: number }) {
  const percentage = score * 100
  const color =
    percentage >= 70 ? 'bg-green-500' :
    percentage >= 50 ? 'bg-yellow-500' : 'bg-red-500'

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-slate-300 capitalize">{category}</span>
        <span className="text-slate-400">{percentage.toFixed(1)}%</span>
      </div>
      <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} transition-all`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

function ActionCard({
  href,
  icon,
  title,
  description,
}: {
  href: string
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <Link
      href={href}
      className="p-4 bg-slate-700/30 hover:bg-slate-700/50 rounded-lg border border-slate-600/50 transition-colors group"
    >
      <div className="flex items-center gap-3 mb-2">
        {icon}
        <span className="font-medium text-white group-hover:text-blue-400 transition-colors">
          {title}
        </span>
      </div>
      <p className="text-sm text-slate-400">{description}</p>
    </Link>
  )
}
