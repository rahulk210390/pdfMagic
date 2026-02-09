const defaultBaseUrl = "http://localhost:8000"

export function getApiBaseUrl() {
  const envUrl = import.meta.env.VITE_API_BASE
  if (envUrl && envUrl.length > 0) {
    return envUrl
  }
  return defaultBaseUrl
}

export async function requestPdf(endpoint, files) {
  const formData = new FormData()
  Array.from(files).forEach((file) => {
    formData.append("files", file)
  })
  const response = await fetch(`${getApiBaseUrl()}${endpoint}`, {
    method: "POST",
    body: formData
  })
  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || "Request failed")
  }
  return response.blob()
}
