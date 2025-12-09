'use client'

import { useEffect, useState } from 'react'
import { BarChart3, CheckCircle, XCircle, AlertCircle, Play, RefreshCw } from 'lucide-react'

interface Metric {
  name: string
  category: string
  score: number
  grade: string
  details: string
  percentage?: number
}

interface EvaluationResult {
  model_name: string
  scenario_name: string
  total_turns: number
  overall_score: number
  overall_percentage: number
  category_scores: Record<string, number>
  metrics: Metric[]
}

interface Benchmark {
  name: string
  description: string
  num_cases: number
}

export default function EvaluationPage() {
  const [result, setResult] = useState<EvaluationResult | null>(null)
  const [benchmarks, setBenchmarks] = useState<Benchmark[]>([])
  const [selectedBenchmark, setSelectedBenchmark] = useState('quick')
  const [loading, setLoading] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)

  useEffect(() => {
    // Load demo evaluation
    fetch('/api/demo/evaluation')
      .then(res => res.json())
      .then(setResult)
      .catch(() => {
        // Fallback demo data
        setResult({
          model_name: 'llama3.1:8b',
          scenario_name: 'quick',
          total_turns: 3,
          overall_score: 0.542,
          overall_percentage: 54.2,
          category_scores: {
            geospatial: 0.511,
            strategic: 0.656,
            adversarial: 0.417
          },
          metrics: [
            { name: 'Distance Accuracy', category: 'geospatial', score: 0.5, grade: 'F', details: '1 distance claim found' },
            { name: 'Grid Reference Usage', category: 'geospatial', score: 0.3, grade: 'F', details: 'No grid references' },
            { name: 'Terrain Awareness', category: 'geospatial', score: 0.73, grade: 'C', details: '4 terrain concepts' },
            { name: 'Objective Alignment', category: 'strategic', score: 0.5, grade: 'F', details: 'No objectives specified' },
            { name: 'Reasoning Structure', category: 'strategic', score: 0.75, grade: 'C', details: '3/4 elements' },
            { name: 'Decision Consistency', category: 'strategic', score: 0.72, grade: 'C', details: 'First response' },
            { name: 'Opponent Modeling', category: 'adversarial', score: 0.5, grade: 'F', details: '2 references' },
            { name: 'Multi-Step Planning', category: 'adversarial', score: 0.33, grade: 'F', details: '1 indicator' }
          ]
        })
      })

    // Load benchmarks
    fetch('/api/benchmarks')
      .then(res => res.json())
      .then(data => setBenchmarks(data.benchmarks || []))
      .catch(() => {
        setBenchmarks([
          { name: 'quick', description: 'Fast benchmark', num_cases: 3 },
          { name: 'geospatial', description: 'Geospatial reasoning', num_cases: 4 },
          { name: 'strategic', description: 'Strategic decisions', num_cases: 3 },
          { name: 'full', description: 'Complete suite', num_cases: 10 }
        ])
      })
  }, [])

  const runBenchmark = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ benchmark: selectedBenchmark, model: 'llama3.1:8b' })
      })
      const data = await res.json()
      setJobId(data.job_id)
      // Poll for results
      pollForResults(data.job_id)
    } catch {
      setLoading(false)
      alert('Failed to start evaluation. Make sure the API server is running.')
    }
  }

  const pollForResults = async (id: string) => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`/api/evaluate/${id}`)
        const data = await res.json()
        if (data.status === 'completed') {
          setResult(data.result)
          setLoading(false)
          setJobId(null)
        } else if (data.status === 'failed') {
          setLoading(false)
          setJobId(null)
          alert('Evaluation failed: ' + data.error)
        } else {
          setTimeout(checkStatus, 2000)
        }
      } catch {
        setTimeout(checkStatus, 2000)
      }
    }
    checkStatus()
  }

  const getGradeColor = (grade: string): string => {
    switch (grade) {
      case 'A': return 'text-green-400'
      case 'B': return 'text-lime-400'
      case 'C': return 'text-yellow-400'
      case 'D': return 'text-orange-400'
      default: return 'text-red-400'
    }
  }

  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'bg-green-500'
    if (score >= 0.6) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">LLM Evaluation Framework</h1>
          <p className="text-slate-400">Measure wargaming capabilities against benchmarks</p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedBenchmark}
            onChange={e => setSelectedBenchmark(e.target.value)}
            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500"
          >
            {benchmarks.map(b => (
              <option key={b.name} value={b.name}>
                {b.name} ({b.num_cases} cases)
              </option>
            ))}
          </select>
          <button
            onClick={runBenchmark}
            disabled={loading}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 text-white rounded-lg flex items-center gap-2 transition-colors"
          >
            {loading ? (
              <>
                <RefreshCw size={16} className="animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play size={16} />
                Run Benchmark
              </>
            )}
          </button>
        </div>
      </div>

      {result && (
        <>
          {/* Overall Score */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm mb-1">Overall Score</p>
                <div className="flex items-end gap-3">
                  <span className="text-5xl font-bold text-white">
                    {result.overall_percentage.toFixed(1)}%
                  </span>
                  <span className={`text-2xl font-bold ${
                    result.overall_percentage >= 80 ? 'text-green-400' :
                    result.overall_percentage >= 60 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {result.overall_percentage >= 90 ? 'A' :
                     result.overall_percentage >= 80 ? 'B' :
                     result.overall_percentage >= 70 ? 'C' :
                     result.overall_percentage >= 60 ? 'D' : 'F'}
                  </span>
                </div>
                <p className="text-slate-500 text-sm mt-2">
                  Model: {result.model_name} | Benchmark: {result.scenario_name}
                </p>
              </div>

              <div className="w-48 h-48">
                <GaugeChart percentage={result.overall_percentage} />
              </div>
            </div>
          </div>

          {/* Category Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {Object.entries(result.category_scores).map(([category, score]) => (
              <CategoryCard key={category} category={category} score={score} />
            ))}
          </div>

          {/* Detailed Metrics */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <BarChart3 size={20} />
              Detailed Metrics
            </h2>

            <div className="space-y-3">
              {result.metrics.map((metric, i) => (
                <div
                  key={i}
                  className="flex items-center gap-4 p-3 bg-slate-700/30 rounded-lg"
                >
                  <div className="flex-shrink-0">
                    {metric.score >= 0.7 ? (
                      <CheckCircle className="text-green-400" size={20} />
                    ) : metric.score >= 0.5 ? (
                      <AlertCircle className="text-yellow-400" size={20} />
                    ) : (
                      <XCircle className="text-red-400" size={20} />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-medium text-white">{metric.name}</span>
                      <span className={`font-bold ${getGradeColor(metric.grade)}`}>
                        {metric.grade}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-1.5 bg-slate-600 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${getScoreColor(metric.score)} transition-all`}
                          style={{ width: `${metric.score * 100}%` }}
                        />
                      </div>
                      <span className="text-sm text-slate-400 w-12 text-right">
                        {(metric.score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">{metric.details}</p>
                  </div>

                  <span className="text-xs text-slate-500 capitalize px-2 py-1 bg-slate-700 rounded">
                    {metric.category}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="mt-6 bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
            <h2 className="text-lg font-semibold text-white mb-4">Improvement Recommendations</h2>
            <div className="space-y-3">
              {result.metrics
                .filter(m => m.score < 0.6)
                .slice(0, 3)
                .map((metric, i) => (
                  <div key={i} className="flex items-start gap-3 text-sm">
                    <span className="text-red-400">!</span>
                    <div>
                      <span className="text-slate-300">{metric.name}:</span>
                      <span className="text-slate-400 ml-2">
                        {metric.category === 'geospatial' && 'Include precise distance calculations and grid references'}
                        {metric.category === 'strategic' && 'Structure decisions with clear reasoning and risk assessment'}
                        {metric.category === 'adversarial' && 'Model opponent responses and plan counter-moves'}
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

function CategoryCard({ category, score }: { category: string; score: number }) {
  const percentage = score * 100
  const color =
    percentage >= 70 ? 'from-green-500 to-emerald-600' :
    percentage >= 50 ? 'from-yellow-500 to-orange-500' :
    'from-red-500 to-rose-600'

  const icons: Record<string, string> = {
    geospatial: '🌍',
    strategic: '🎯',
    adversarial: '⚔️',
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-5 border border-slate-700/50">
      <div className="flex items-center gap-3 mb-3">
        <span className="text-2xl">{icons[category] || '📊'}</span>
        <span className="font-medium text-white capitalize">{category}</span>
      </div>
      <div className="text-3xl font-bold text-white mb-2">
        {percentage.toFixed(1)}%
      </div>
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full bg-gradient-to-r ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

function GaugeChart({ percentage }: { percentage: number }) {
  const radius = 70
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const color =
    percentage >= 80 ? '#22c55e' :
    percentage >= 60 ? '#eab308' : '#ef4444'

  return (
    <svg viewBox="0 0 180 180" className="transform -rotate-90">
      {/* Background circle */}
      <circle
        cx="90"
        cy="90"
        r={radius}
        fill="none"
        stroke="#334155"
        strokeWidth="12"
      />
      {/* Progress circle */}
      <circle
        cx="90"
        cy="90"
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth="12"
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={strokeDashoffset}
        className="transition-all duration-1000"
      />
    </svg>
  )
}
