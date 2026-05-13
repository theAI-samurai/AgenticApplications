import React, { useMemo, useState } from 'react';
import { A2UIProvider, A2UIRenderer, useA2UI } from '@a2ui/react';
import './styles.css';

function A2UIRuntime({ prompt, runToken, onStatusChange }) {
  const { processMessages } = useA2UI();

  React.useEffect(() => {
    if (!prompt || !runToken) {
      return;
    }

    onStatusChange?.('connecting');
    const source = new EventSource(
      `/a2ui-events?prompt=${encodeURIComponent(prompt)}`
    );

    source.onopen = () => {
      onStatusChange?.('streaming');
    };

    source.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        processMessages([message]);
        onStatusChange?.('live');
      } catch (error) {
        console.error('Failed to process A2UI message:', error);
        onStatusChange?.('error');
      }
    };

    source.onerror = () => {
      source.close();
      onStatusChange?.('idle');
    };

    return () => {
      source.close();
      onStatusChange?.('idle');
    };
  }, [onStatusChange, processMessages, prompt, runToken]);

  return (
    <A2UIRenderer
      surfaceId="main"
      className="surface-frame"
      fallback={
        <div className="surface-placeholder">
          <div className="surface-placeholder__pulse" />
          <div>
            <p className="surface-placeholder__label">Awaiting agent surface</p>
            <p className="surface-placeholder__text">
              Send a query to render the live A2UI dashboard.
            </p>
          </div>
        </div>
      }
    />
  );
}

export default function App() {
  const [prompt, setPrompt] = useState('add 10 and 5');
  const [activePrompt, setActivePrompt] = useState('add 10 and 5');
  const [runToken, setRunToken] = useState(1);
  const [streamState, setStreamState] = useState('idle');
  const onAction = useMemo(() => async () => {}, []);

  const onRun = (event) => {
    event.preventDefault();
    const nextPrompt = prompt.trim();
    if (!nextPrompt) {
      return;
    }
    setActivePrompt(nextPrompt);
    setRunToken((value) => value + 1);
  };

  return (
    <A2UIProvider onAction={onAction}>
      <div className="app-shell">
        <div className="ambient ambient--one" />
        <div className="ambient ambient--two" />
        <main className="dashboard">
          <section className="hero-card glass-card">
            <div className="hero-card__copy">
              <div className="eyebrow">AG-UI + A2UI + React</div>
              <h1>Demo: Financial Copilot with AG-UI + A2UI.</h1>
              <p>
                Type a financial or arithmetic query, stream the AG-UI tool execution,
                and watch the A2UI surface update live.
              </p>
            </div>
            <div className="hero-card__meta">
              <div className={`status-chip status-chip--${streamState}`}>
                <span className="status-chip__dot" />
                {streamState}
              </div>
              <div className="meta-grid">
                <div>
                  <span>Backend</span>
                  <strong>AG-UI SSE</strong>
                </div>
                <div>
                  <span>Renderer</span>
                  <strong>@a2ui/react</strong>
                </div>
                <div>
                  <span>Mode</span>
                  <strong>Live surface</strong>
                </div>
              </div>
            </div>
          </section>

          <section className="control-panel glass-card">
            <div className="panel-heading">
              <div>
                <h2>Prompt console</h2>
                <p>Enter the instruction that should trigger the agent.</p>
              </div>
              <div className="prompt-pill">Last run: {activePrompt}</div>
            </div>

            <form onSubmit={onRun} className="control-row">
              <label className="prompt-field">
                <span>Query</span>
                <input
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  placeholder="Try: subtract 12 and 4"
                />
              </label>

              <button type="submit" className="run-button">
                <span>Run</span>
                <span className="run-button__accent" />
              </button>
            </form>
          </section>

          <section className="content-grid">
            <section className="surface-panel glass-card">
              <div className="panel-heading panel-heading--tight">
                <div>
                  <h2>Live surface</h2>
                  <p>Rendered by the A2UI runtime as messages stream in.</p>
                </div>
                <div className="panel-tag">surface: main</div>
              </div>

              <A2UIRuntime
                prompt={activePrompt}
                runToken={runToken}
                onStatusChange={setStreamState}
              />
            </section>

            <aside className="inspector glass-card">
              <div className="panel-heading panel-heading--tight">
                <div>
                  <h2>System notes</h2>
                  <p>A quick read of what the UI is doing.</p>
                </div>
              </div>

              <div className="inspector-list">
                <div className="inspector-item">
                  <span>Pipeline</span>
                  <strong>Prompt → AG-UI tool call → A2UI render</strong>
                </div>
                <div className="inspector-item">
                  <span>Current prompt</span>
                  <strong>{prompt}</strong>
                </div>
                <div className="inspector-item">
                  <span>Connection</span>
                  <strong>Local SSE bridge</strong>
                </div>
              </div>
            </aside>
          </section>
        </main>
      </div>
    </A2UIProvider>
  );
}
