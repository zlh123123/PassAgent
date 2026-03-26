"use client";

import { useEffect, useRef, useState } from "react";
import { MapPinned, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { LocationFactor } from "@/components/passinfinity/types";

declare global {
  interface Window {
    L?: any;
  }
}

interface Props {
  locations: LocationFactor[];
  onChange: (locations: LocationFactor[]) => void;
}

let leafletLoader: Promise<any> | null = null;

function ensureLeaflet() {
  if (typeof window === "undefined") {
    return Promise.reject(new Error("Leaflet 仅能在浏览器中加载"));
  }
  if (window.L) return Promise.resolve(window.L);
  if (leafletLoader) return leafletLoader;

  leafletLoader = new Promise((resolve, reject) => {
    const cssId = "passinfinity-leaflet-css";
    if (!document.getElementById(cssId)) {
      const link = document.createElement("link");
      link.id = cssId;
      link.rel = "stylesheet";
      link.href = "/vendor/leaflet/leaflet.css";
      document.head.appendChild(link);
    }

    const existingScript = document.getElementById("passinfinity-leaflet-js");
    if (existingScript) {
      existingScript.addEventListener("load", () => resolve(window.L));
      existingScript.addEventListener("error", () => reject(new Error("Leaflet 脚本加载失败")));
      return;
    }

    const script = document.createElement("script");
    script.id = "passinfinity-leaflet-js";
    script.src = "/vendor/leaflet/leaflet.js";
    script.async = true;
    script.onload = () => resolve(window.L);
    script.onerror = () => reject(new Error("Leaflet 脚本加载失败"));
    document.body.appendChild(script);
  });

  return leafletLoader;
}

function makeLocationId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) return crypto.randomUUID();
  return `loc-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function MapFactorEditor({ locations, onChange }: Props) {
  const mapRef = useRef<any>(null);
  const layerRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const locationsRef = useRef<LocationFactor[]>(locations);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    locationsRef.current = locations;
  }, [locations]);

  useEffect(() => {
    let cancelled = false;

    ensureLeaflet()
      .then((L) => {
        if (cancelled || !containerRef.current || mapRef.current) return;

        const map = L.map(containerRef.current, {
          center: [31.2304, 121.4737],
          zoom: 4,
          zoomControl: true,
        });
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "&copy; OpenStreetMap contributors",
        }).addTo(map);

        const layerGroup = L.layerGroup().addTo(map);
        map.on("click", (event: any) => {
          const nextLocation: LocationFactor = {
            location_id: makeLocationId(),
            label: `位置 ${locationsRef.current.length + 1}`,
            lat: Number(event.latlng.lat.toFixed(4)),
            lng: Number(event.latlng.lng.toFixed(4)),
          };
          onChange([...locationsRef.current, nextLocation]);
        });

        mapRef.current = map;
        layerRef.current = layerGroup;
        setReady(true);
      })
      .catch(() => {
        setReady(false);
      });

    return () => {
      cancelled = true;
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
        layerRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!ready || !window.L || !mapRef.current || !layerRef.current) return;

    const L = window.L;
    layerRef.current.clearLayers();

    locations.forEach((location, index) => {
      const marker = L.circleMarker([location.lat, location.lng], {
        radius: 9,
        weight: 3,
        color: "#fff",
        fillColor: "#0f172a",
        fillOpacity: 0.95,
      }).addTo(layerRef.current);
      marker.bindTooltip(`${index + 1}. ${location.label || "未命名位置"}`, {
        permanent: true,
        direction: "top",
        opacity: 0.9,
      });
    });

    if (locations.length > 0) {
      const group = L.featureGroup(layerRef.current.getLayers());
      mapRef.current.fitBounds(group.getBounds().pad(0.4));
    }
  }, [locations, ready]);

  function updateLocation(locationId: string, patch: Partial<LocationFactor>) {
    onChange(
      locations.map((location) =>
        location.location_id === locationId ? { ...location, ...patch } : location,
      ),
    );
  }

  function removeLocation(locationId: string) {
    onChange(locations.filter((location) => location.location_id !== locationId));
  }

  return (
    <div className="rounded border border-slate-200 bg-white p-4">
      <div className="mb-3 flex items-center justify-between gap-4">
        <p className="text-sm text-slate-600">点击地图落点即可加入位置因子，保存前可逐条改名。</p>
        <Button type="button" variant="outline" size="sm" onClick={() => onChange([])} disabled={locations.length === 0}>
          清空
        </Button>
      </div>

      <div className="grid gap-3 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="overflow-hidden rounded border border-slate-200">
          <div ref={containerRef} className="h-[380px] w-full bg-slate-100" />
        </div>

        <div className="rounded border border-slate-200 bg-slate-50 p-3">
          <div className="mb-2 flex items-center gap-1.5 text-xs font-medium text-slate-600">
            <MapPinned className="h-3.5 w-3.5" />
            已添加位置
          </div>

          <div className="space-y-2">
            {locations.length === 0 && (
              <p className="py-4 text-center text-xs text-slate-400">
                点击左侧地图开始
              </p>
            )}

            {locations.map((location, index) => (
              <div key={location.location_id} className="flex items-start gap-2 rounded border border-slate-200 bg-white p-2">
                <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-900 text-xs font-medium text-white">
                  {index + 1}
                </div>
                <div className="min-w-0 flex-1">
                  <Input
                    id={`location-${location.location_id}`}
                    value={location.label}
                    onChange={(e) => updateLocation(location.location_id, { label: e.target.value })}
                    placeholder="位置名称"
                    className="h-7 text-xs"
                  />
                  <p className="mt-1 text-xs text-slate-400">
                    {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
                  </p>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  className="h-7 w-7 shrink-0"
                  onClick={() => removeLocation(location.location_id)}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
