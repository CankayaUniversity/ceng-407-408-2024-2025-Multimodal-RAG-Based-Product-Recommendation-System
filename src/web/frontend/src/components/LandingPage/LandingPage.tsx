import React from 'react';
import Header from '../Header/Header';
import Hero from '../Hero/Hero';
import Categories from '../Categories/Categories';
import Brands from '../Brands/Brands';
import './LandingPage.css';

function LandingPage(): React.ReactElement {
  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <Hero />
        <Categories />
        <Brands />
      </main>
    </div>
  );
}

export default LandingPage;