import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./components/LandingPage/LandingPage";
import FashionAIChat from "./components/FashionChat/FashionChat";
import Login from "./components/Login/Login";
import Register from "./components/Register/Register";
import ProfilePage from "./components/ProfilePage/ProfilePage";
import ProfilePreferences from "./components/ProfilePreferences/ProfilePreferences";
import Dashboard from "./components/Dashboard/Dashboard";
import Wardrobe from "./components/Wardrobe/Wardrobe";
import AIStylist from "./components/AIStylist/AIStylist";
import StyleAnalysis from "./components/StyleAnalysis/StyleAnalysis";
import BrowseProducts from "./components/BrowseProducts/BrowseProducts";

function App(): React.ReactElement {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/chat" element={<FashionAIChat />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/wardrobe" element={<Wardrobe />} />
        <Route path="/stylist" element={<AIStylist />} />
        <Route path="/style-analysis" element={<StyleAnalysis />} />
        <Route path="/browse" element={<BrowseProducts />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/profile/preferences" element={<ProfilePreferences />} />
        {/* Placeholder for future routes */}
        {/* <Route path="/product/:id" element={<ProductDetail />} /> */}
        {/* <Route path="/checkout" element={<Checkout />} /> */}
        {/* <Route path="/orders" element={<OrderHistory />} /> */}
      </Routes>
    </Router>
  );
}

export default App;
