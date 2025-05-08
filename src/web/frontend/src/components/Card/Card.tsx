import React from "react";
import "./Card.css";

interface CardProps {
  image: string;
  title: string;
  subtitle?: string;
  type: "category" | "brand";
  url?: string;
  isLoading?: boolean;
}

function Card({
  image,
  title,
  subtitle,
  type,
  url,
  isLoading = false,
}: CardProps): React.ReactElement {
  const handleClick = () => {
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <div
      className={`card ${type}-card ${isLoading ? 'loading' : ''}`}
      onClick={handleClick}
      style={{ cursor: url ? "pointer" : "default" }}
    >
      <div className={`${type}-image-container ${isLoading ? 'loading' : ''}`}>
        {!isLoading ? (
          <img
            src={image || "https://placehold.co/300x300"}
            alt={title}
            onError={(e) => {
              e.currentTarget.src = "https://placehold.co/300x300";
            }}
            className={`${type}-image`}
          />
        ) : null}
      </div>
      <div className={`${type}-info`}>
        {isLoading ? (
          <div className={`${type}-title loading`}></div>
        ) : (
          <p className={`${type}-title`}>{title}</p>
        )}
        {subtitle && !isLoading && <p className={`${type}-subtitle`}>{subtitle}</p>}
      </div>
    </div>
  );
}

export default Card;
