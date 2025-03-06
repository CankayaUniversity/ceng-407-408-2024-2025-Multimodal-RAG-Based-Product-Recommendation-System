import React from 'react';
import './Card.css';

interface CardProps {
  image: string;
  title: string;
  subtitle?: string;
  type: 'category' | 'brand';
}

function Card({ image, title, subtitle, type }: CardProps): React.ReactElement {
  return (
    <div className={`card ${type}-card`}>
      <div className={`${type}-image-container`}>
        <img src={image || "https://placehold.co/300x300"} alt={title} className={`${type}-image`} />
      </div>
      <div className={`${type}-info`}>
        <p className={`${type}-title`}>{title}</p>
        {subtitle && <p className={`${type}-subtitle`}>{subtitle}</p>}
      </div>
    </div>
  );
}

export default Card;