const Card = ({ title, children, footer, className = '' }) => {
  return (
    <section className={`rounded-xl border border-gray-200 bg-white p-6 shadow-sm ${className}`.trim()}>
      {title ? (
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-[#333333]">{title}</h3>
        </div>
      ) : null}
      <div>{children}</div>
      {footer ? <div className="mt-4">{footer}</div> : null}
    </section>
  )
}

export default Card
