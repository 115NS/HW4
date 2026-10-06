import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProducts, type Product } from '../api'
import { CATEGORY_LABELS } from '../brand/categories'
import ProductCard from '../components/ProductCard'

const featuredIds = [
  'basic-hoodie-big-yale',
  'district-vit-crewneck-vintage-bulldog',
  '2025-yale-vs-harvard-t-shirt',
  'davenport-college-crewneck',
]

const HOME_CATEGORIES = ['hoodie', 'crewneck', 't-shirt', 'quarter-zip', 'jacket']

export default function HomePage() {
  const [products, setProducts] = useState<Product[]>([])

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch(() => setProducts([]))
  }, [])

  const featured = featuredIds
    .map((id) => products.find((product) => product.product_id === id))
    .filter((product): product is Product => product !== undefined)
  const categoryCounts: Record<string, number> = {}
  for (const product of products) categoryCounts[product.category] = (categoryCounts[product.category] ?? 0) + 1

  return (
    <>
      <section className="hero">
        <div className="hero-text">
          <p className="eyebrow">New Haven · Since 1975</p>
          <h1>
            Wear your <em>Yale</em> pride.
          </h1>
          <p>
            Campus Customs has been outfitting Bulldogs, families, and alumni right across from campus for
            five decades. Find hoodies, crewnecks, tees, and more for every college, school, and team.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="button">
              Shop all products
            </Link>
            <Link to="/about" className="button button-outline">
              Our story
            </Link>
          </div>
          <ul className="hero-facts" aria-label="Store highlights">
            <li>
              <strong>1975</strong>
              <span>Founded in New Haven</span>
            </li>
            <li>
              <strong>{products.length || 102}</strong>
              <span>Styles in the shop</span>
            </li>
            <li>
              <strong>7 days</strong>
              <span>Open at 57 Broadway</span>
            </li>
          </ul>
        </div>
        <figure className="hero-mascot">
          <div className="mascot-seal">
            {/* Seal ring: the mascot's name set around the portrait, like a collegiate crest. */}
            <svg className="mascot-ring" viewBox="0 0 300 300" aria-hidden="true">
              <defs>
                <path id="mascot-ring-path" d="M150,150 m-128,0 a128,128 0 1,1 256,0 a128,128 0 1,1 -256,0" />
              </defs>
              <circle cx="150" cy="150" r="146" fill="none" stroke="rgba(255,255,255,0.35)" strokeWidth="1" />
              <circle cx="150" cy="150" r="112" fill="none" stroke="rgba(255,255,255,0.35)" strokeWidth="1" />
              <text>
                <textPath href="#mascot-ring-path" startOffset="0">
                  HANDSOME DAN XIX · YALE&apos;S BULLDOG MASCOT · SINCE 1889 ·
                </textPath>
              </text>
            </svg>
            <img
              src="/images/handsome-dan-kingman.jpg"
              alt="Handsome Dan XIX, Yale's bulldog mascot, resting on the grass in a navy Yale bandana"
              width={960}
              height={638}
            />
          </div>
          <figcaption>
            <strong>Meet Handsome Dan XIX</strong>
            <span>Yale&apos;s bulldog mascot, a tradition since 1889</span>
            <small>
              Photo:{' '}
              <a href="https://commons.wikimedia.org/wiki/File:Handsome_Dan_Kingman.jpg" target="_blank" rel="noreferrer">
                Joeshmonobody
              </a>
              ,{' '}
              <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noreferrer">
                CC BY-SA 4.0
              </a>
            </small>
          </figcaption>
        </figure>
      </section>

      <section className="highlights">
        <div>
          <span className="highlight-index">01</span>
          <h2>Residential colleges</h2>
          <p>Show your house spirit with gear for Davenport, Morse, Saybrook, Grace Hopper, and more.</p>
        </div>
        <div>
          <span className="highlight-index">02</span>
          <h2>Bulldog athletics</h2>
          <p>Cheer on Yale teams from baseball to sailing, plus pieces made for The Game against Harvard.</p>
        </div>
        <div>
          <span className="highlight-index">03</span>
          <h2>Schools &amp; family</h2>
          <p>Pieces for graduate and professional schools, and gifts for proud Yale moms, dads, and grandparents.</p>
        </div>
      </section>

      {products.length > 0 && (
        <section className="category-section">
          <div className="section-heading">
            <h2>Shop by category</h2>
          </div>
          <div className="category-tiles">
            {HOME_CATEGORIES.map((category) => (
              <Link key={category} to={`/products?category=${category}`} className="category-tile">
                <span className="category-name">{CATEGORY_LABELS[category]}</span>
                <span className="category-count">{categoryCounts[category] ?? 0} styles</span>
                <span className="category-arrow" aria-hidden="true">
                  →
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {featured.length > 0 && (
        <section>
          <div className="section-heading">
            <h2>Fan favorites</h2>
            <Link to="/products">View all →</Link>
          </div>
          <div className="product-grid">
            {featured.map((product) => (
              <ProductCard key={product.product_id} product={product} />
            ))}
          </div>
        </section>
      )}
    </>
  )
}
