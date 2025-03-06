import React from 'react';
import Header from './components/Header/Header';
import Hero from './components/Hero/Hero';
import Categories from './components/Categories/Categories';
import Brands from './components/Brands/Brands';
import './App.css';

function App(): React.ReactElement {
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

export default App;