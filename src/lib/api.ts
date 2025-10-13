const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return {
    "Content-Type": "application/json",
    ...(token ? { "Authorization": `Bearer ${token}` } : {})
  };
}

export async function evaluateFlowchart(imageBase64: string) {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/api/evaluate-flowchart`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ image: imageBase64 }),
  });

  if (response.status === 401) {
    localStorage.removeItem('token');
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Evaluation failed: ${response.statusText}`);
  }

  return response.json();
}

export async function evaluatePseudocode(code: string) {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/api/evaluate-pseudocode`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ code }),
  });

  if (response.status === 401) {
    localStorage.removeItem('token');
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Evaluation failed: ${response.statusText}`);
  }

  return response.json();
}
