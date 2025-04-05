import "./SuggestionItem.css"

interface SuggestionItemProps {
  title: string
  subtitle: string
  image: string
}

function SuggestionItem({ title, subtitle, image }: SuggestionItemProps) {
  return (
    <div className="suggestion-item">
      <div className="suggestion-item-image-container">
      <img src={image || "https://placehold.co/48x48"}  /> {/* alt={title} className={`${className}-image`} */}
      </div>
      <div className="suggestion-item-content">
        <h3 className="suggestion-item-title">{title}</h3>
        <p className="suggestion-item-subtitle">{subtitle}</p>
      </div>
    </div>
  )
}

export default SuggestionItem

