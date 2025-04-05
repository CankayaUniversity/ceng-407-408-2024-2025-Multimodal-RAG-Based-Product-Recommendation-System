import type { InputHTMLAttributes } from "react";
import "./Input.css";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  className?: string;
}

function Input({ className = "", ...props }: InputProps) {
  return <input className={`input ${className}`} {...props} />;
}

export default Input;
