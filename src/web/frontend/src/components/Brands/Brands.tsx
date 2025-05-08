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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:3001/api/trends")
      .then((res) => res.json())
      .then((data) => {
        if (data.trends) {
          setBrands(data.trends);
        }
        setLoading(false);
      })
      .catch((error) => {
        console.error("Failed to fetch trends:", error);
        setLoading(false);
      });
  }, []);

  // Generate placeholder items
  const placeholders = Array(8).fill(null).map((_, index) => ({
    id: `placeholder-${index}`,
    title: "Loading...",
    image: "",
    url: ""
  }));

  return (
    <section className="brands-section">
      <h2 className="section-title">Latest Trends</h2>
      <div className="brand-grid">
        {loading ? (
          // Show placeholders while loading
          placeholders.map((placeholder) => (
            <div key={placeholder.id} className="card-placeholder">
              <Card
                type="brand"
                image=""
                title="Loading..."
                subtitle=""
                url=""
                isLoading={true}
              />
              <div className="loading-shimmer"></div>
            </div>
          ))
        ) : (
          // Show actual brand data when loaded
          brands.map((brand) => (
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
                isLoading={false}
              />
            </a>
          ))
        )}
        
        {/* If no brands were loaded but loading is complete, show a message */}
        {!loading && brands.length === 0 && (
          <div className="no-trends-message">
            No trend data available at the moment. Please check back later.
          </div>
        )}
      </div>
    </section>
  );
}

export default Brands;
