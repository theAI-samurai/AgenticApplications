# A2UI Frontend Setup Instructions

This directory will contain a true A2UI frontend using the official @a2ui/react renderer.

## 1. Initialize the frontend

```
cd ui/a2ui_frontend
npm init -y
```

## 2. Install A2UI renderer and React

```
npm install react react-dom @a2ui/react
```

## 3. Create a basic entry point (src/index.jsx)

- Render the <A2UIApp /> component from @a2ui/react
- Connect it to the backend SSE/WebSocket endpoint (to be implemented)

## 4. Develop the AG-UI → A2UI translation layer

- This will be a Python service that listens to AG-UI protocol events and emits A2UI protocol messages.
- It can be a FastAPI route or a standalone proxy server.

## 5. Serve the frontend

- Use a simple static server (e.g., serve, http-server, or integrate with FastAPI).

---

Next steps:
- Run the above commands to set up the frontend.
- I will now scaffold the src/ directory and a basic React entry point.
