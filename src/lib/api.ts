const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function evaluateFlowchart(imageBase64: string) {
  const response = await fetch(`${API_BASE_URL}/api/evaluate-flowchart`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: imageBase64 }),
  });

  if (!response.ok) {
    throw new Error(`Evaluation failed: ${response.statusText}`);
  }

  return response.json();
}

export async function evaluatePseudocode(code: string) {
  const response = await fetch(`${API_BASE_URL}/api/evaluate-pseudocode`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });

  if (!response.ok) {
    throw new Error(`Evaluation failed: ${response.statusText}`);
  }

  return response.json();
}
