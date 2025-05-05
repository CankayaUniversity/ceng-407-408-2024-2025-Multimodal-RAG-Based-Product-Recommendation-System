import React, { useEffect, useState } from "react";
import Card from "../Card/Card";
import "./Brands.css";

interface Brand {
  id: string;
  title: string;
  image: string;
  url: string;
}

function Brands(): React.ReactElement {
  const [brands, setBrands] = useState<Brand[]>([]);

  useEffect(() => {
    fetch("http://localhost:3001/api/trends")
      .then((res) => res.json())
      .then((data) => {
        if (data.trends) {
          setBrands(data.trends);
        }
      })
      .catch((error) => {
        console.error("Failed to fetch trends:", error);
      });
  }, []);

  return (
    <section className="brands-section">
      <h2 className="section-title">Latest Trends</h2>
      <div className="brand-grid">
        {brands.map((brand) => (
          <a
            key={brand.id}
            href={brand.url}
            target="_blank"
            rel="noopener noreferrer"
            className="card-link-wrapper"
            aria-label={`Go to article: ${brand.title}`}
          >
            <Card
              type="brand"
              image={brand.image}
              title={brand.title}
              subtitle=""
              url={brand.url}
            />
          </a>
        ))}
      </div>
    </section>
  );
}

export default Brands;
