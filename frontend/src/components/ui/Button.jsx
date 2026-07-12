const Button = ({ children, variant = 'primary', className = '', ...props }) => {
  const variants = {
    primary: 'bg-[#008080] text-white hover:bg-[#006666]',
    secondary: 'bg-[#f5f5f5] text-[#333333] hover:bg-[#eaeaea]',
    outline: 'border border-[#008080] bg-white text-[#008080] hover:bg-[#f2fafa]',
    ghost: 'bg-transparent text-[#008080] hover:bg-[#f2fafa]',
  }

  return (
    <button
      type="button"
      className={`rounded-md px-4 py-2 font-medium transition-colors ${variants[variant] || variants.primary} ${className}`.trim()}
      {...props}
    >
      {children}
    </button>
  )
}

export default Button
