import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'
import { Map, BarChart3, Play, Home, Github } from 'lucide-react'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'StrategyForge - Multi-Agent Wargaming',
  description: 'LLM-powered wargaming simulation with evaluation framework',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <aside className="w-64 bg-slate-900/80 backdrop-blur-sm border-r border-slate-700/50 p-4 flex flex-col">
            <div className="mb-8">
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                StrategyForge
              </h1>
              <p className="text-xs text-slate-400 mt-1">Multi-Agent Wargaming</p>
            </div>

            <nav className="flex-1 space-y-2">
              <NavLink href="/" icon={<Home size={18} />}>Dashboard</NavLink>
              <NavLink href="/map" icon={<Map size={18} />}>Tactical Map</NavLink>
              <NavLink href="/evaluation" icon={<BarChart3 size={18} />}>Evaluation</NavLink>
              <NavLink href="/simulation" icon={<Play size={18} />}>Simulation</NavLink>
            </nav>

            <div className="pt-4 border-t border-slate-700/50">
              <a
                href="https://github.com/PaulSemaan007/strategyforge"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
              >
                <Github size={16} />
                View Source
              </a>
              <p className="text-xs text-slate-500 mt-2">
                Built with LangGraph + Ollama
              </p>
            </div>
          </aside>

          {/* Main content */}
          <main className="flex-1 overflow-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}

function NavLink({
  href,
  icon,
  children,
}: {
  href: string
  icon: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-300 hover:bg-slate-800/50 hover:text-white transition-colors"
    >
      {icon}
      <span>{children}</span>
    </Link>
  )
}
