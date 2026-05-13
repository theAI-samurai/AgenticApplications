import React from "react";
import { createRoot } from "react-dom/client";
import { A2UIApp } from "@a2ui/react";

function App() {
  // TODO: Set the correct SSE/WebSocket endpoint for A2UI protocol messages
  return <A2UIApp endpoint="/a2ui-events" />;
}

const root = createRoot(document.getElementById("root"));
root.render(<App />);
