import React from 'react';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from './components/LandingPage/LandingPage';
import FashionAIChat from './components/FashionChat/FashionChat';


function App(): React.ReactElement {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/chat" element={<FashionAIChat />} />
      </Routes>
    </Router>
  );
}

export default App;