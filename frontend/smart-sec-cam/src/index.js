import React from 'react';
import ReactDOM from 'react-dom/client'; // Updated import
import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";
import { CookiesProvider } from 'react-cookie'; // Import CookiesProvider
import './index.css';
import App from './App';
import VideoList from "./pages/VideoList";
import Login from "./pages/Login";
import Register from "./pages/Register";
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root')); // Create root
root.render(
  <React.StrictMode>
    <CookiesProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="stream" element={<App />} />
          <Route path="videos" element={<VideoList />} />
          <Route path="register" element={<Register />} />
        </Routes>
      </BrowserRouter>
    </CookiesProvider>
  </React.StrictMode>
);
