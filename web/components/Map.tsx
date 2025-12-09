'use client'

import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { useEffect } from 'react'

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

interface MapProps {
  features: MapFeature[]
  center: [number, number]
  zoom: number
  onFeatureClick?: (feature: MapFeature) => void
}

function MapController({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap()

  useEffect(() => {
    map.setView([center[0], center[1]], zoom)
  }, [map, center, zoom])

  return null
}

export default function Map({ features, center, zoom, onFeatureClick }: MapProps) {
  const getMarkerColor = (feature: MapFeature): string => {
    if (feature.properties.force === 'blue') return '#3B82F6'
    if (feature.properties.force === 'red') return '#EF4444'
    if (feature.properties.type === 'objective') return '#EAB308'
    return '#6B7280'
  }

  const getMarkerRadius = (feature: MapFeature): number => {
    if (feature.properties.type === 'objective') return 12
    if (feature.properties.type === 'headquarters') return 10
    return 8
  }

  return (
    <MapContainer
      center={[center[0], center[1]]}
      zoom={zoom}
      style={{ height: '100%', width: '100%' }}
      className="rounded-lg"
    >
      <MapController center={center} zoom={zoom} />

      {/* Dark themed tile layer */}
      <TileLayer
        attribution='&copy; <a href="https://carto.com/">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />

      {/* Unit markers */}
      {features.map(feature => (
        <CircleMarker
          key={feature.properties.id}
          center={[
            feature.geometry.coordinates[1],
            feature.geometry.coordinates[0],
          ]}
          radius={getMarkerRadius(feature)}
          pathOptions={{
            color: getMarkerColor(feature),
            fillColor: getMarkerColor(feature),
            fillOpacity: 0.7,
            weight: 2,
          }}
          eventHandlers={{
            click: () => onFeatureClick?.(feature),
          }}
        >
          <Popup>
            <div className="text-sm">
              <div className="font-bold">{feature.properties.name}</div>
              <div className="text-gray-600">{feature.properties.type}</div>
              {feature.properties.strength && (
                <div>Strength: {feature.properties.strength}%</div>
              )}
              {feature.properties.value && (
                <div>Value: {feature.properties.value}</div>
              )}
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  )
}
