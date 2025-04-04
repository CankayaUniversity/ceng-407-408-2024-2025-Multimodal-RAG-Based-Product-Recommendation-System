import "./Avatar.css"

interface AvatarProps {
  image?: string
  fallback: string
  alt: string
  className?: string
}

function Avatar({ image, fallback, alt, className = "" }: AvatarProps) {
  return (
    <div className={`avatar ${className}`}>
      {image ? (
        <div className="avatar-image">
          <img src={image || "https://placehold.co/32x32"} alt={alt} className={`${className}-image`} />
        </div>
      ) : (
        <div className="avatar-fallback">{fallback}</div>
      )}
    </div>
  )
}

export default Avatar

