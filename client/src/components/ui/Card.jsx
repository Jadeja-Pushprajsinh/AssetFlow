export default function Card({
  children,
  title,
  footer,
  className = '',
  ...props
}) {
  return (
    <div
      className={`bg-white rounded-xl shadow-sm border border-gray-100 p-6 ${className}`}
      {...props}
    >
      {title && (
        <div className="mb-4 border-b border-gray-100 pb-3">
          <h3 className="font-semibold text-ink text-lg">{title}</h3>
        </div>
      )}

      <div className="text-ink">{children}</div>

      {footer && (
        <div className="mt-4 border-t border-gray-100 pt-3">{footer}</div>
      )}
    </div>
  );
}
