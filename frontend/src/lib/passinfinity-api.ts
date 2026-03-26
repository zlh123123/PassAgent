import { apiGet, apiPost } from "@/lib/api";
import type {
  PassInfinityAnalysis,
  PassInfinityArtifact,
  PassInfinityDraft,
} from "@/components/passinfinity/types";

export interface PassInfinityPolicyResponse {
  policy: Record<string, unknown>;
}

export interface PassInfinityArtifactListResponse {
  artifacts: PassInfinityArtifact[];
}

export function getPassInfinityPolicy() {
  return apiGet<PassInfinityPolicyResponse>("/api/passinfinity/policy");
}

export function validatePassInfinityDraft(draft: PassInfinityDraft) {
  return apiPost<PassInfinityAnalysis>("/api/passinfinity/validate", draft);
}

export function savePassInfinityArtifact(draft: PassInfinityDraft) {
  return apiPost<PassInfinityArtifact>("/api/passinfinity/artifacts", draft);
}

export function listPassInfinityArtifacts() {
  return apiGet<PassInfinityArtifactListResponse>("/api/passinfinity/artifacts");
}

export function getPassInfinityArtifact(artifactId: string) {
  return apiGet<PassInfinityArtifact>(`/api/passinfinity/artifacts/${artifactId}`);
}
