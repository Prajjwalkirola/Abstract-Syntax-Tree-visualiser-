import React, { useState } from "react";
import MonacoEditor from "@monaco-editor/react";
import { saveSource, deleteSource } from "../api/api";
import debounce from "lodash.debounce";

export default function Start({ onCodeChange }) {
  const [code, setCode] = useState("");

  // Debounced function to save code and run pipeline
  const debouncedSave = debounce((newCode) => {
    saveSource(newCode);
  }, 500);

  const handleChange = (value) => {
    setCode(value);
    onCodeChange(value);
    debouncedSave(value);
  };

  const handleClear = () => {
    setCode("");
    deleteSource();
  };

  return (
    <div>
      <h2>Enter your code</h2>
      <MonacoEditor
        height="400px"
        language="python"
        value={code}
        onChange={handleChange}
        options={{ fontSize: 16, minimap: { enabled: false } }}
      />
      <br />
      <button onClick={handleClear}>Clear</button>
    </div>
  );
} 