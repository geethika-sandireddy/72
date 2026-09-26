interface Props {
  eyebrow: string
  title: string
  description?: string
  align?: 'left' | 'center'
}

export function SectionHeading({ eyebrow, title, description, align = 'left' }: Props) {
  return (
    <div className={`mb-8 max-w-2xl ${align === 'center' ? 'mx-auto text-center' : ''}`}>
      <div className={`flex items-center gap-2.5 ${align === 'center' ? 'justify-center' : ''}`}>
        <span className="h-px w-8 bg-gradient-to-r from-transparent to-primary" />
        <span className="eyebrow !text-primary">{eyebrow}</span>
      </div>
      <h2 className="mt-3 text-pretty font-display text-3xl font-bold leading-tight tracking-tight text-foreground sm:text-4xl">
        {title}
      </h2>
      {description && (
        <p className="mt-3 text-pretty leading-relaxed text-muted-foreground">{description}</p>
      )}
    </div>
  )
}
