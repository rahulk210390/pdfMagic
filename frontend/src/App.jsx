import { useMemo, useState } from "react"
import { requestPdf } from "./api.js"

const operations = [
  {
    key: "merge-pdf",
    label: "Merge PDFs",
    endpoint: "/merge-pdf",
    accept: ".pdf",
    helper: "Upload multiple PDF files to merge in order."
  },
  {
    key: "images-to-pdf",
    label: "Images to PDF",
    endpoint: "/images-to-pdf",
    accept: "image/*",
    helper: "Upload images to convert into a single PDF."
  },
  {
    key: "merge-files",
    label: "Merge PDFs + Images",
    endpoint: "/merge-files",
    accept: ".pdf,image/*",
    helper: "Upload any mix of PDFs and images to merge."
  }
]

export default function App() {
  const [activeKey, setActiveKey] = useState(operations[0].key)
  const [files, setFiles] = useState([])
  const [status, setStatus] = useState("idle")
  const [message, setMessage] = useState("")

  const activeOperation = useMemo(
    () => operations.find((operation) => operation.key === activeKey),
    [activeKey]
  )

  const handleFilesChange = (event) => {
    setFiles(event.target.files || [])
    setMessage("")
  }

  const downloadBlob = (blob, filename) => {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!files || files.length === 0) {
      setMessage("Please select at least one file.")
      return
    }
    setStatus("loading")
    setMessage("")
    try {
      const blob = await requestPdf(activeOperation.endpoint, files)
      const filename = `${activeOperation.key}.pdf`
      downloadBlob(blob, filename)
      setStatus("success")
      setMessage("PDF generated successfully.")
    } catch (error) {
      setStatus("error")
      setMessage(error.message || "Something went wrong.")
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>PdfMagic</h1>
        <p>
          Merge PDFs, convert images to PDF, and combine images with PDFs locally
          or on the web.
        </p>
      </header>
      <section className="panel">
        <div className="tabs">
          {operations.map((operation) => (
            <button
              key={operation.key}
              type="button"
              className={operation.key === activeKey ? "tab active" : "tab"}
              onClick={() => {
                setActiveKey(operation.key)
                setFiles([])
                setMessage("")
              }}
            >
              {operation.label}
            </button>
          ))}
        </div>
        <form onSubmit={handleSubmit} className="form">
          <label className="label">
            {activeOperation.helper}
            <input
              type="file"
              accept={activeOperation.accept}
              multiple
              onChange={handleFilesChange}
            />
          </label>
          <button className="primary" type="submit" disabled={status === "loading"}>
            {status === "loading" ? "Processing..." : "Create PDF"}
          </button>
        </form>
        {message && (
          <div className={`message ${status}`}>
            {message}
          </div>
        )}
      </section>
    </div>
  )
}
