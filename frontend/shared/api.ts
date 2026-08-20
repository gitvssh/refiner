import { API_ORIGIN } from "@/shared/config/site";

export type Analysis = {
  coverage_score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  strengths: string[];
};

export type Refinement = {
  analysis: Analysis;
  rewritten_resume: string;
  export_token: string;
  export_expires_in_seconds: number;
};

async function errorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: string };
    return body.detail ?? "The request could not be completed.";
  } catch {
    return "The request could not be completed.";
  }
}

export async function createRefinement(
  file: File,
  jobDescription: string,
): Promise<Refinement> {
  const form = new FormData();
  form.append("resume", file);
  form.append("job_description", jobDescription);
  const response = await fetch(`${API_ORIGIN}/api/v1/refinements`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) {
    throw new Error(await errorMessage(response));
  }
  return (await response.json()) as Refinement;
}

export async function consumePdfExport(exportToken: string): Promise<Blob> {
  const response = await fetch(`${API_ORIGIN}/api/v1/exports/pdf`, {
    method: "POST",
    headers: { "X-Export-Token": exportToken },
  });
  if (!response.ok) {
    throw new Error(await errorMessage(response));
  }
  return response.blob();
}
