export default function Input({
  label,
  id,
  error,
  className = '',
  ...props
}) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-ink">
          {label}
        </label>
      )}
      <input
        id={id}
        className={`px-3 py-2 rounded-md border text-sm text-ink bg-white
          placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-teal
          focus:border-teal transition-colors duration-150
          ${error ? 'border-red-500' : 'border-gray-300'}
          ${className}`}
        {...props}
      />
      {error && <span className="text-xs text-red-600">{error}</span>}
    </div>
  );
}
