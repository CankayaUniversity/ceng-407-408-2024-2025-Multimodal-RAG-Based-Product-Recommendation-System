import React from "react";
import "./Card.css";

interface CardProps {
  image: string;
  title: string;
  subtitle?: string;
  type: "category" | "brand";
  url?: string;
}

function Card({
  image,
  title,
  subtitle,
  type,
  url,
}: CardProps): React.ReactElement {
  const handleClick = () => {
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <div
      className={`card ${type}-card`}
      onClick={handleClick}
      style={{ cursor: url ? "pointer" : "default" }}
    >
      <div className={`${type}-image-container`}>
        <img
          src={image || "https://placehold.co/300x300"}
          alt={title}
          onError={(e) => {
            e.currentTarget.src = "https://placehold.co/300x300";
          }}
          className={`${type}-image`}
        />
      </div>
      <div className={`${type}-info`}>
        <p className={`${type}-title`}>{title}</p>
        {subtitle && <p className={`${type}-subtitle`}>{subtitle}</p>}
      </div>
    </div>
  );
}

export default Card;
