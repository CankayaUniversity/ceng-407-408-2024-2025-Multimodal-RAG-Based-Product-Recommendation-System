import React from 'react';
import Card from '../Card/Card';
import './Categories.css';

interface Category {
  id: number;
  title: string;
  image: string;
}

function Categories(): React.ReactElement {
  const categories: Category[] = [
    { id: 1, title: "Women's Clothing", image: "https://placehold.co/300x300" },
    { id: 2, title: "Men's Clothing", image: "https://placehold.co/300x300" },
    { id: 3, title: "Women's Shoes", image: "https://placehold.co/300x300" },
    { id: 4, title: "Men's Shoes", image: "https://placehold.co/300x300" },
    { id: 5, title: "Women's Bags", image: "https://placehold.co/300x300" },
    { id: 6, title: "Men's Bags", image: "https://placehold.co/300x300" },
    { id: 7, title: "Women's Accessories", image: "https://placehold.co/300x300" },
    { id: 8, title: "Men's Accessories", image: "https://placehold.co/300x300" }
  ];

  return (
    <section className="categories-section">
      <h2 className="section-title">Popular categories</h2>
      <div className="category-grid">
        {categories.map((category) => (
          <Card 
            key={category.id}
            type="category"
            image={category.image}
            title={category.title}
          />
        ))}
      </div>
    </section>
  );
}

export default Categories;