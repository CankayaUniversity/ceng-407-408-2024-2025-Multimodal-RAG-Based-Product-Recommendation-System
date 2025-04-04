import type React from "react"
import type { ButtonHTMLAttributes } from "react"
import "./Button.css"

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "ghost"
  size?: "default" | "icon"
  className?: string
  children: React.ReactNode
}

function Button({ variant = "default", size = "default", className = "", children, ...props }: ButtonProps) {
  const baseClass = "button"
  const variantClass = `button-${variant}`
  const sizeClass = `button-${size}`

  return (
    <button className={`${baseClass} ${variantClass} ${sizeClass} ${className}`} {...props}>
      {children}
    </button>
  )
}

export default Button

