const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!res.ok) {
    let detail = `API ${path} failed: ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // response wasn't JSON — keep the generic message
    }
    throw new ApiError(res.status, detail);
  }
  return res.json();
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API ${path} failed: ${res.status}`);
  return res.json();
}

export interface Region {
  id: string;
  name: string;
  type: string;
  parent_id: string | null;
  center: [number, number];
  zoom: number;
  case_study?: boolean;
  children?: string[];
}

export interface SourceInfo {
  status: string;
  name: string;
  retrieved_at?: string;
  connection?: string;
}

export interface ForestHistory {
  region_id: string;
  unit: string;
  observations: { year: number; area: number }[];
  trend: {
    direction: string;
    annual_rate: number;
    annual_rate_pct: number;
    is_accelerating: boolean;
    explanation: string;
  };
  critical_threshold_area: number | null;
  projected_threshold_year: number | null;
  forecast: { year: number; low: number; mid: number; high: number }[];
  forecast_confidence: string;
  causes: string[];
  source: SourceInfo;
}

export interface WaterBalance {
  region_id: string;
  unit: string;
  balance: {
    available_reserve: number;
    annual_replenishment: number;
    current_extraction: number;
    sustainable_extraction_limit: number;
    extraction_ratio: number;
    remaining_capacity: number;
    years_to_depletion: number | null;
    status: string;
    explanation: string;
  };
  consumption_breakdown: Record<string, number>;
  consumption_shares_pct: Record<string, number>;
  source: SourceInfo;
}

export interface RegionSustainability {
  region_id: string;
  risk: {
    score: number;
    level: string;
    explanation: string;
    factors: { name: string; value: number; weight: number; contribution: number }[];
    projected_threshold_year: number | null;
  };
  sustainability: {
    overall: number;
    weakest_factor: string;
    explanation: string;
    factors: { name: string; score: number; weight: number; contribution: number }[];
  };
  recommendations: {
    problem: string;
    interventions: string[];
    severity: string;
    rationale: string;
  }[];
  narrative: { forest: string; water: string };
  sources: Record<string, { status: string; name: string }>;
}

export interface RouteScored {
  id: string;
  name: string;
  distance_km: number;
  construction_cost_cr: number;
  environmental_impact: number;
  social_impact: number;
  connectivity_benefit: number;
  terrain_difficulty: number;
  affected_ecosystems: string[];
  affected_villages: string[];
  weighted_score: number;
  rank: number;
  explanation: string;
}

export interface RoutesResponse {
  scenario_id: string;
  origin: string;
  destination: string;
  weights: Record<string, number>;
  routes: RouteScored[];
  recommended_route_id: string;
}

export interface SiteScored {
  id: string;
  name: string;
  water_availability: number;
  infrastructure_access: number;
  population_proximity: number;
  environmental_sensitivity: number;
  pollution_risk: number;
  land_suitability: number;
  suitability_score: number;
  classification: string;
  rank: number;
  explanation: string;
}

export interface SitesResponse {
  scenario_id: string;
  sites: SiteScored[];
  recommended_site_id: string;
}

export interface ScenarioResult {
  region_id: string;
  baseline_sustainability: number;
  projected_sustainability: number;
  baseline_risk: number;
  projected_risk: number;
  risk_level: string;
  factors: Record<string, number>;
  explanation: string;
  source_status: string;
}

export interface WeatherResponse {
  region_id: string;
  data: { forecast: { date: string; precipitation_mm: number | null; temp_max_c: number | null; temp_min_c: number | null }[] };
  source: SourceInfo;
}

export interface NDVIResponse {
  region_id: string;
  bbox: { west: number; south: number; east: number; north: number };
  date_from: string;
  date_to: string;
  ndvi_threshold: number;
  pixel_size_m: number;
  total_valid_area_km2: number;
  vegetation_area_km2: number;
  vegetation_fraction: number;
  ndvi_mean: number;
  ndvi_min: number;
  ndvi_max: number;
  max_cloud_cover_pct: number;
  source: { status: string; name: string; notes: string };
}

export const api = {
  regions: (parentId?: string) =>
    getJson<{ regions: Region[]; source: SourceInfo | null }>(`/api/regions${parentId ? `?parent_id=${parentId}` : ""}`),
  region: (id: string) => getJson<Region & { children: string[] }>(`/api/regions/${id}`),
  forestHistory: (regionId: string) => getJson<ForestHistory>(`/api/environment/forest-history?region_id=${regionId}`),
  waterBalance: (regionId: string) => getJson<WaterBalance>(`/api/resources/water?region_id=${regionId}`),
  sustainability: (regionId: string) => getJson<RegionSustainability>(`/api/regions/${regionId}/sustainability`),
  routes: (scenarioId: string, weights: Record<string, number>) => {
    const q = new URLSearchParams({ scenario_id: scenarioId, ...Object.fromEntries(Object.entries(weights).map(([k, v]) => [k, String(v)])) });
    return getJson<RoutesResponse>(`/api/infrastructure/routes?${q.toString()}`);
  },
  sites: (scenarioId: string) => getJson<SitesResponse>(`/api/industry/site-suitability?scenario_id=${scenarioId}`),
  status: () => getJson<Record<string, { purpose: string; status: string; detail: string }>>("/api/status"),
  weather: (regionId: string) => getJson<WeatherResponse>(`/api/environment/weather?region_id=${regionId}`),
  ndvi: (lat: number, lon: number) => getJson<NDVIResponse>(`/api/environment/ndvi?lat=${lat}&lon=${lon}`),
  simulateScenario: (payload: {
    region_id: string;
    industrial_growth_pct: number;
    population_growth_pct: number;
    water_consumption_pct: number;
    forest_protection_pct: number;
    infrastructure_expansion_pct: number;
  }) => postJson<ScenarioResult>("/api/scenarios/simulate", payload),
};
