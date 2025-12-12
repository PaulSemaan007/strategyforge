'use client'

import { useEffect, useRef, useState } from 'react'
import dynamic from 'next/dynamic'

// Dynamically import Leaflet components to avoid SSR issues
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
)
const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
)
const CircleMarker = dynamic(
  () => import('react-leaflet').then((mod) => mod.CircleMarker),
  { ssr: false }
)
const Popup = dynamic(
  () => import('react-leaflet').then((mod) => mod.Popup),
  { ssr: false }
)
const Polyline = dynamic(
  () => import('react-leaflet').then((mod) => mod.Polyline),
  { ssr: false }
)

export interface UnitPosition {
  id: string
  name: string
  lat: number
  lon: number
  status: string
}

interface SimulationMapProps {
  blueUnits: UnitPosition[]
  redUnits: UnitPosition[]
  isRunning?: boolean
}

// Track previous positions for movement trails
interface UnitHistory {
  [unitId: string]: { lat: number; lon: number }[]
}

export default function SimulationMap({ blueUnits, redUnits, isRunning }: SimulationMapProps) {
  const [mounted, setMounted] = useState(false)
  const [unitHistory, setUnitHistory] = useState<UnitHistory>({})
  const prevPositionsRef = useRef<{ blue: UnitPosition[]; red: UnitPosition[] }>({ blue: [], red: [] })

  // Handle client-side mounting
  useEffect(() => {
    setMounted(true)
  }, [])

  // Track position history for movement trails
  useEffect(() => {
    if (blueUnits.length === 0 && redUnits.length === 0) return

    const newHistory = { ...unitHistory }

    // Track blue unit movements
    blueUnits.forEach((unit) => {
      if (!newHistory[unit.id]) {
        newHistory[unit.id] = []
      }
      const history = newHistory[unit.id]
      const lastPos = history[history.length - 1]

      // Only add if position changed
      if (!lastPos || lastPos.lat !== unit.lat || lastPos.lon !== unit.lon) {
        newHistory[unit.id] = [...history.slice(-5), { lat: unit.lat, lon: unit.lon }]
      }
    })

    // Track red unit movements
    redUnits.forEach((unit) => {
      if (!newHistory[unit.id]) {
        newHistory[unit.id] = []
      }
      const history = newHistory[unit.id]
      const lastPos = history[history.length - 1]

      if (!lastPos || lastPos.lat !== unit.lat || lastPos.lon !== unit.lon) {
        newHistory[unit.id] = [...history.slice(-5), { lat: unit.lat, lon: unit.lon }]
      }
    })

    setUnitHistory(newHistory)
    prevPositionsRef.current = { blue: blueUnits, red: redUnits }
  }, [blueUnits, redUnits])

  // Taiwan Strait center coordinates
  const center: [number, number] = [24.5, 120.5]
  const zoom = 7

  if (!mounted) {
    return (
      <div className="w-full h-full bg-slate-900 flex items-center justify-center">
        <div className="text-slate-500">Loading map...</div>
      </div>
    )
  }

  const getMarkerColor = (force: 'blue' | 'red', status: string): string => {
    if (status === 'destroyed') return '#6B7280'
    if (status === 'damaged') return force === 'blue' ? '#60A5FA' : '#F87171'
    return force === 'blue' ? '#3B82F6' : '#EF4444'
  }

  const getMarkerOpacity = (status: string): number => {
    if (status === 'destroyed') return 0.3
    if (status === 'damaged') return 0.6
    return 0.8
  }

  return (
    <div className="w-full h-full relative">
      {/* Map Legend */}
      <div className="absolute top-2 right-2 z-[1000] bg-slate-900/90 p-3 rounded-lg border border-slate-700 text-xs">
        <div className="font-medium text-white mb-2">Force Positions</div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            <span className="text-slate-300">Blue Force ({blueUnits.length})</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-slate-300">Red Force ({redUnits.length})</span>
          </div>
        </div>
        {isRunning && (
          <div className="mt-2 pt-2 border-t border-slate-700">
            <div className="flex items-center gap-2 text-green-400">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <span>Live tracking</span>
            </div>
          </div>
        )}
      </div>

      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        className="rounded-lg"
      >
        {/* Dark themed tile layer */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Movement trails for blue units */}
        {blueUnits.map((unit) => {
          const history = unitHistory[unit.id] || []
          if (history.length < 2) return null
          return (
            <Polyline
              key={`trail-${unit.id}`}
              positions={history.map((pos) => [pos.lat, pos.lon] as [number, number])}
              pathOptions={{
                color: '#3B82F6',
                weight: 2,
                opacity: 0.4,
                dashArray: '5, 5',
              }}
            />
          )
        })}

        {/* Movement trails for red units */}
        {redUnits.map((unit) => {
          const history = unitHistory[unit.id] || []
          if (history.length < 2) return null
          return (
            <Polyline
              key={`trail-${unit.id}`}
              positions={history.map((pos) => [pos.lat, pos.lon] as [number, number])}
              pathOptions={{
                color: '#EF4444',
                weight: 2,
                opacity: 0.4,
                dashArray: '5, 5',
              }}
            />
          )
        })}

        {/* Blue unit markers */}
        {blueUnits.map((unit) => (
          <CircleMarker
            key={unit.id}
            center={[unit.lat, unit.lon]}
            radius={8}
            pathOptions={{
              color: getMarkerColor('blue', unit.status),
              fillColor: getMarkerColor('blue', unit.status),
              fillOpacity: getMarkerOpacity(unit.status),
              weight: 2,
            }}
          >
            <Popup>
              <div className="text-sm">
                <div className="font-bold text-blue-600">{unit.name}</div>
                <div className="text-gray-600">Blue Force</div>
                <div className="text-gray-500 text-xs mt-1">
                  Status: {unit.status}
                </div>
                <div className="text-gray-400 text-xs">
                  Pos: {unit.lat.toFixed(3)}, {unit.lon.toFixed(3)}
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))}

        {/* Red unit markers */}
        {redUnits.map((unit) => (
          <CircleMarker
            key={unit.id}
            center={[unit.lat, unit.lon]}
            radius={8}
            pathOptions={{
              color: getMarkerColor('red', unit.status),
              fillColor: getMarkerColor('red', unit.status),
              fillOpacity: getMarkerOpacity(unit.status),
              weight: 2,
            }}
          >
            <Popup>
              <div className="text-sm">
                <div className="font-bold text-red-600">{unit.name}</div>
                <div className="text-gray-600">Red Force</div>
                <div className="text-gray-500 text-xs mt-1">
                  Status: {unit.status}
                </div>
                <div className="text-gray-400 text-xs">
                  Pos: {unit.lat.toFixed(3)}, {unit.lon.toFixed(3)}
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}
