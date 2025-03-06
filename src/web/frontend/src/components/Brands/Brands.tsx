import React from 'react';
import Card from '../Card/Card';
import './Brands.css';

interface Brand {
  id: number;
  title: string;
  subtitle: string;
  image: string;
}

function Brands(): React.ReactElement {
  const brands: Brand[] = [
    { id: 1, title: "Nike Sportswear", subtitle: "Women", image: "https://placehold.co/300x300" },
    { id: 2, title: "Adidas Originals", subtitle: "Men", image: "https://placehold.co/300x300" },
    { id: 3, title: "Reebok", subtitle: "Women", image: "https://placehold.co/300x300" },
    { id: 4, title: "Puma", subtitle: "Men", image: "https://placehold.co/300x300" },
    { id: 5, title: "Under Armour", subtitle: "Women", image: "https://placehold.co/300x300" },
    { id: 6, title: "The North Face", subtitle: "Men", image: "https://placehold.co/300x300" },
    { id: 7, title: "Columbia", subtitle: "Women", image: "https://placehold.co/300x300" },
    { id: 8, title: "Patagonia", subtitle: "Men", image: "https://placehold.co/300x300" }
  ];

  return (
    <section className="brands-section">
      <h2 className="section-title">New arrivals</h2>
      <div className="brand-grid">
        {brands.map((brand) => (
          <Card 
            key={brand.id}
            type="brand"
            image={brand.image}
            title={brand.title}
            subtitle={brand.subtitle}
          />
        ))}
      </div>
    </section>
  );
}

export default Brands;