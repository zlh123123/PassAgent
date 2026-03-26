export type RichTextStyle = "bold" | "italic" | "underline" | "strikethrough";

export interface RichTextValue {
  content: string;
  styles: RichTextStyle[];
}

export interface ImagePoint {
  x: number;
  y: number;
  kind: "passpoint" | "grid";
}

export interface ImageFactor {
  image_id: string;
  title: string;
  src: string;
  tags: string[];
  use_grid: boolean;
  points: ImagePoint[];
}

export interface LocationFactor {
  location_id: string;
  label: string;
  lat: number;
  lng: number;
}

export interface PassInfinityDraft {
  title: string;
  text: string;
  rich_text: RichTextValue;
  images: ImageFactor[];
  locations: LocationFactor[];
}

export interface PassInfinityAnalysis {
  normalized_content: PassInfinityDraft;
  encoded_text: string;
  policy_result: {
    valid: boolean;
    summary: string;
    warnings: string[];
    factors_used: string[];
    factor_counts: Record<string, number>;
  };
}

export interface PassInfinityArtifact extends PassInfinityAnalysis {
  artifact_id: string;
  title: string;
  created_at: string | null;
  updated_at: string | null;
}
