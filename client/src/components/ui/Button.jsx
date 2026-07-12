export default function Button({
  children,
  variant = 'primary',
  type = 'button',
  disabled = false,
  className = '',
  ...props
}) {
  const base =
    'inline-flex items-center justify-center px-4 py-2 rounded-md font-medium text-sm ' +
    'transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 ' +
    'disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary:
      'bg-teal text-white hover:bg-teal-dark focus:ring-teal',
    secondary:
      'bg-teal-lighter text-teal-darker hover:bg-teal-light focus:ring-teal',
    outline:
      'border border-teal text-teal hover:bg-teal-lighter focus:ring-teal',
    ghost:
      'text-teal hover:bg-teal-lighter focus:ring-teal',
    danger:
      'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  };

  return (
    <button
      type={type}
      disabled={disabled}
      className={`${base} ${variants[variant] ?? variants.primary} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
