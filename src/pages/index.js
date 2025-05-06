import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);
const [error, setError] = useState(null)
 

const sendPrompt = async () => {
  if (!prompt.trim()) return;
  setLoading(true);
  setError(null);
  try {
    const res = await axios.post("/api/chat", { prompt });
    setReply(res.data.reply);
  } catch (err) {
    setReply("Error: failed to connect to GPT server.");
    setError(JSON.stringify(err, null, 2));
  } finally {
    setLoading(false);
  }
};

  return (
    <main style={{ padding: "2rem", maxWidth: "600px", margin: "0 auto" }}>
      <h1>GPT Chat</h1>
      {error && (
  <div style={{ marginTop: "1rem", color: "red", whiteSpace: "pre-wrap" }}>
    <strong>Error detail:</strong>
    <div>{error}</div>
  </div>
)}
      <textarea
        rows={4}
        style={{ width: "100%", marginBottom: "1rem" }}
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Ask something..."
      />
      <button onClick={sendPrompt} disabled={loading}>
        {loading ? "Loading..." : "Send"}
      </button>
      <div style={{ marginTop: "2rem", whiteSpace: "pre-wrap" }}>
        <strong>Reply:</strong>
        <div>{reply}</div>
      </div>
    </main>
  );
}