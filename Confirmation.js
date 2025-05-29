import React, { useEffect, useState } from "react";
import { getAST, getTree } from "../api/api";

export default function Confirmation({ code }) {
  const [ast, setAst] = useState({});
  const [treeUrl, setTreeUrl] = useState("");
  const [history, setHistory] = useState([]);
  const [selectedIdx, setSelectedIdx] = useState(0);

  useEffect(() => {
    // Add new code to history if changed
    setHistory((prev) => {
      if (prev.length === 0 || prev[prev.length - 1] !== code) {
        return [...prev, code];
      }
      return prev;
    });
  }, [code]);

  useEffect(() => {
    if (history.length === 0) return;
    getAST().then((res) => setAst(res.data));
    getTree().then((res) => {
      const url = URL.createObjectURL(res.data);
      setTreeUrl(url);
    });
  }, [selectedIdx, history]);

  return (
    <div>
      <h2>Confirmation</h2>
      <div style={{ marginBottom: 20 }}>
        <label>Timeline: </label>
        <input
          type="range"
          min={0}
          max={history.length - 1}
          value={selectedIdx}
          onChange={e => setSelectedIdx(Number(e.target.value))}
          style={{ width: 300 }}
        />
        <span style={{ marginLeft: 10 }}>Step {selectedIdx + 1} / {history.length}</span>
      </div>
      <div style={{ display: "flex", gap: 20 }}>
        <div>
          <h3>Code</h3>
          <pre>{history[selectedIdx]}</pre>
        </div>
        <div>
          <h3>AST (JSON)</h3>
          <pre>{JSON.stringify(ast, null, 2)}</pre>
        </div>
        <div>
          <h3>AST Tree</h3>
          {treeUrl && <img src={treeUrl} alt="AST Tree" style={{ maxWidth: 300 }} />}
        </div>
      </div>
    </div>
  );
} 