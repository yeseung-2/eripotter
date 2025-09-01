import * as React from "react"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline"
}

function Badge({ className = "", variant, ...props }: BadgeProps) {
  const baseClasses = "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors"
  
  // className이 있으면 완전히 그것만 사용 (variant 무시)
  if (className) {
    return (
      <div className={`${baseClasses} ${className}`} style={{ backgroundColor: undefined, color: undefined }} {...props} />
    )
  }
  
  const variantClasses = {
    default: "border border-transparent bg-blue-600 text-white hover:bg-blue-700",
    secondary: "border border-transparent bg-gray-100 text-gray-800 hover:bg-gray-200", 
    destructive: "border border-transparent bg-red-600 text-white hover:bg-red-700",
    outline: "border border-gray-300 text-gray-700 hover:bg-gray-50",
  }
  
  const finalVariant = variant || "default"
  const classes = `${baseClasses} ${variantClasses[finalVariant]}`
  
  return (
    <div className={classes} {...props} />
  )
}

export { Badge }
