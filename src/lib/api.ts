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

export async function evaluateDocument(fileBase64: string, fileType: string) {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/api/evaluate-document`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ file: fileBase64, file_type: fileType }),
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

export async function exportEvaluationPDF(evaluationId: number): Promise<Blob> {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/api/export/pdf/${evaluationId}`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`
    },
  });

  if (response.status === 401) {
    localStorage.removeItem('token');
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    throw new Error(`Export failed: ${response.statusText}`);
  }

  return response.blob();
}

export async function exportEvaluationsCSV(): Promise<string> {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/api/export/csv`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`
    },
  });

  if (response.status === 401) {
    localStorage.removeItem('token');
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    throw new Error(`Export failed: ${response.statusText}`);
  }

  return response.text();
}

export async function compareSolutions(
  problemStatement: string,
  solution1: { type: 'flowchart' | 'pseudocode', content: string },
  solution2: { type: 'flowchart' | 'pseudocode', content: string }
) {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/api/compare-solutions`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      problem_statement: problemStatement,
      solution1,
      solution2
    }),
  });

  if (response.status === 401) {
    localStorage.removeItem('token');
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Comparison failed: ${response.statusText}`);
  }

  return response.json();
}

export async function getComparisons() {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/api/comparisons`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (response.status === 401) {
    localStorage.removeItem('token');
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch comparisons: ${response.statusText}`);
  }

  return response.json();
}

export async function exportComparison(comparisonId: number): Promise<Blob> {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/api/export/comparison/${comparisonId}`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`
    },
  });

  if (response.status === 401) {
    localStorage.removeItem('token');
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    throw new Error(`Export failed: ${response.statusText}`);
  }

  return response.blob();
}
