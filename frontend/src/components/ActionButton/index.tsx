import type { ButtonHTMLAttributes, ReactNode } from 'react';

export default function ActionButton({ children, className = '', ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { children: ReactNode }) {
  return <button className={`toolbar-btn ${className}`} {...props}>{children}</button>;
}
