// The site's mark: a simple heraldic shield with a serif Y, drawn in SVG (no external assets).
export default function YaleShield({ size = 36 }: { size?: number }) {
  return (
    <svg className="yale-shield" width={size} height={size * 1.15} viewBox="0 0 40 46" aria-hidden="true">
      <path d="M3 3h34v19c0 11-7.5 18.5-17 21C10.5 40.5 3 33 3 22V3z" fill="currentColor" />
      <path d="M6 6h28v16c0 9-6 15.2-14 17.6C12 37.2 6 31 6 22V6z" fill="none" stroke="rgba(255,255,255,0.55)" strokeWidth="1" />
      <text x="20" y="29" textAnchor="middle" fontFamily="var(--serif)" fontSize="22" fontWeight="700" fill="#fff">
        Y
      </text>
    </svg>
  )
}
