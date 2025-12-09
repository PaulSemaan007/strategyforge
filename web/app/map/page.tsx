'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'
import { Layers, Info, Target, Users } from 'lucide-react'

// Dynamic import for Leaflet (SSR incompatible)
const MapComponent = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-slate-800/50 rounded-lg">
      <div className="text-slate-400">Loading map...</div>
    </div>
  ),
})

interface MapFeature {
  type: string
  properties: {
    id: string
    name: string
    type: string
    force?: string
    strength?: number
    capabilities?: string[]
    value?: number
    owner?: string
  }
  geometry: {
    type: string
    coordinates: [number, number]
  }
}

interface MapData {
  type: string
  features: MapFeature[]
  bounds: {
    center: [number, number]
    zoom: number
  }
}

export default function MapPage() {
  const [mapData, setMapData] = useState<MapData | null>(null)
  const [selectedUnit, setSelectedUnit] = useState<MapFeature | null>(null)
  const [showBlue, setShowBlue] = useState(true)
  const [showRed, setShowRed] = useState(true)
  const [showObjectives, setShowObjectives] = useState(true)

  useEffect(() => {
    fetch('/api/map/taiwan_strait')
      .then(res => res.json())
      .then(setMapData)
      .catch(() => {
        // Demo data fallback
        setMapData({
          type: 'FeatureCollection',
          features: [
            {
              type: 'Feature',
              properties: { id: 'blue-1', name: 'Blue HQ', type: 'headquarters', force: 'blue', strength: 100 },
              geometry: { type: 'Point', coordinates: [121.5, 25.0] }
            },
            {
              type: 'Feature',
              properties: { id: 'red-1', name: 'Red HQ', type: 'headquarters', force: 'red', strength: 100 },
              geometry: { type: 'Point', coordinates: [119.3, 26.0] }
            },
            {
              type: 'Feature',
              properties: { id: 'obj-1', name: 'Strait Control', type: 'objective', value: 10, owner: 'contested' },
              geometry: { type: 'Point', coordinates: [120.0, 24.5] }
            }
          ],
          bounds: { center: [24.5, 120.5], zoom: 7 }
        })
      })
  }, [])

  const filteredFeatures = mapData?.features.filter(f => {
    if (f.properties.force === 'blue' && !showBlue) return false
    if (f.properties.force === 'red' && !showRed) return false
    if (f.properties.type === 'objective' && !showObjectives) return false
    return true
  }) || []

  const blueUnits = mapData?.features.filter(f => f.properties.force === 'blue') || []
  const redUnits = mapData?.features.filter(f => f.properties.force === 'red') || []
  const objectives = mapData?.features.filter(f => f.properties.type === 'objective') || []

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-slate-700/50 bg-slate-900/50">
        <h1 className="text-xl font-bold text-white">Taiwan Strait - Tactical Map</h1>
        <p className="text-sm text-slate-400">Interactive geospatial visualization</p>
      </div>

      <div className="flex-1 flex">
        {/* Map */}
        <div className="flex-1 p-4">
          <div className="h-full rounded-lg overflow-hidden border border-slate-700/50">
            {mapData && (
              <MapComponent
                features={filteredFeatures}
                center={mapData.bounds.center}
                zoom={mapData.bounds.zoom}
                onFeatureClick={setSelectedUnit}
              />
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="w-80 p-4 border-l border-slate-700/50 bg-slate-900/30 overflow-auto">
          {/* Layer Controls */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
              <Layers size={16} />
              Layer Controls
            </h3>
            <div className="space-y-2">
              <LayerToggle
                label="Blue Force"
                count={blueUnits.length}
                color="blue"
                checked={showBlue}
                onChange={setShowBlue}
              />
              <LayerToggle
                label="Red Force"
                count={redUnits.length}
                color="red"
                checked={showRed}
                onChange={setShowRed}
              />
              <LayerToggle
                label="Objectives"
                count={objectives.length}
                color="yellow"
                checked={showObjectives}
                onChange={setShowObjectives}
              />
            </div>
          </div>

          {/* Unit Details */}
          {selectedUnit && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
                <Info size={16} />
                Selected Unit
              </h3>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
                <div className="flex items-center gap-2 mb-3">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      selectedUnit.properties.force === 'blue'
                        ? 'bg-blue-500'
                        : selectedUnit.properties.force === 'red'
                        ? 'bg-red-500'
                        : 'bg-yellow-500'
                    }`}
                  />
                  <span className="font-medium text-white">{selectedUnit.properties.name}</span>
                </div>
                <div className="space-y-2 text-sm">
                  <InfoRow label="ID" value={selectedUnit.properties.id} />
                  <InfoRow label="Type" value={selectedUnit.properties.type} />
                  {selectedUnit.properties.strength && (
                    <InfoRow label="Strength" value={`${selectedUnit.properties.strength}%`} />
                  )}
                  {selectedUnit.properties.capabilities && (
                    <div>
                      <span className="text-slate-400">Capabilities:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {selectedUnit.properties.capabilities.map(cap => (
                          <span
                            key={cap}
                            className="px-2 py-0.5 bg-slate-700 rounded text-xs text-slate-300"
                          >
                            {cap}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {selectedUnit.properties.value && (
                    <InfoRow label="Strategic Value" value={selectedUnit.properties.value.toString()} />
                  )}
                  <InfoRow
                    label="Position"
                    value={`${selectedUnit.geometry.coordinates[1].toFixed(3)}, ${selectedUnit.geometry.coordinates[0].toFixed(3)}`}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Force Summary */}
          <div>
            <h3 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
              <Users size={16} />
              Force Summary
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                <div className="text-2xl font-bold text-blue-400">{blueUnits.length}</div>
                <div className="text-xs text-slate-400">Blue Units</div>
              </div>
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                <div className="text-2xl font-bold text-red-400">{redUnits.length}</div>
                <div className="text-xs text-slate-400">Red Units</div>
              </div>
            </div>

            <div className="mt-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <Target size={16} className="text-yellow-400" />
                <span className="text-sm text-slate-300">{objectives.length} Strategic Objectives</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function LayerToggle({
  label,
  count,
  color,
  checked,
  onChange,
}: {
  label: string
  count: number
  color: string
  checked: boolean
  onChange: (v: boolean) => void
}) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
  }

  return (
    <label className="flex items-center gap-3 cursor-pointer group">
      <input
        type="checkbox"
        checked={checked}
        onChange={e => onChange(e.target.checked)}
        className="sr-only"
      />
      <div
        className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-colors ${
          checked ? `${colors[color]} border-transparent` : 'border-slate-500'
        }`}
      >
        {checked && (
          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
          </svg>
        )}
      </div>
      <span className="text-sm text-slate-300 group-hover:text-white transition-colors flex-1">
        {label}
      </span>
      <span className="text-xs text-slate-500">{count}</span>
    </label>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-slate-400">{label}:</span>
      <span className="text-slate-200">{value}</span>
    </div>
  )
}
