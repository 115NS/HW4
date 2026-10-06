import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { fetchProducts, type Product } from '../api'
import { CATEGORY_LABELS } from '../brand/categories'
import ProductCard from '../components/ProductCard'

const PRICE_FILTERS: Record<string, { label: string; test: (price: number) => boolean }> = {
  'under-50': { label: 'Under $50', test: (price) => price < 50 },
  '50-75': { label: '$50 – $75', test: (price) => price >= 50 && price < 75 },
  '75-plus': { label: '$75 and up', test: (price) => price >= 75 },
}

const SORTS: Record<string, { label: string; compare: (a: Product, b: Product) => number }> = {
  name: { label: 'Name (A–Z)', compare: (a, b) => a.name.localeCompare(b.name) },
  'price-low': { label: 'Price: low to high', compare: (a, b) => a.price - b.price || a.name.localeCompare(b.name) },
  'price-high': { label: 'Price: high to low', compare: (a, b) => b.price - a.price || a.name.localeCompare(b.name) },
}

function searchText(product: Product): string {
  return [product.name, product.garment_type, product.description, ...product.search_tags, ...product.colors]
    .join(' ')
    .toLowerCase()
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  // Filters live in the URL, so they survive the back button from a product page and can be shared.
  const [params, setParams] = useSearchParams()
  // The search box keeps its own state so fast typing isn't lost while the URL catches up.
  const [query, setQuery] = useState(() => params.get('q') ?? '')
  const category = params.get('category') ?? ''
  const price = params.get('price') ?? ''
  const sort = params.get('sort') ?? 'name'

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch((err: Error) => setError(err.message))
  }, [])

  function update(key: string, value: string) {
    setParams(
      (current) => {
        const next = new URLSearchParams(current)
        if (value) next.set(key, value)
        else next.delete(key)
        return next
      },
      { replace: true },
    )
  }

  function clearFilters() {
    setQuery('')
    setParams({}, { replace: true })
  }

  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    for (const product of products ?? []) counts[product.category] = (counts[product.category] ?? 0) + 1
    return counts
  }, [products])

  const visible = useMemo(() => {
    if (!products) return []
    const words = query.toLowerCase().split(/\s+/).filter(Boolean)
    return products
      .filter((product) => !category || product.category === category)
      .filter((product) => !price || PRICE_FILTERS[price]?.test(product.price))
      .filter((product) => {
        const text = searchText(product)
        return words.every((word) => text.includes(word))
      })
      .sort((SORTS[sort] ?? SORTS.name).compare)
  }, [products, query, category, price, sort])

  const filtersActive = Boolean(query || category || price || sort !== 'name')

  return (
    <>
      <h1>Products</h1>
      {error && <p className="status error">Could not load products: {error}</p>}
      {!products && !error && <p className="status">Loading products…</p>}
      {products && (
        <>
          <form className="product-filters" role="search" onSubmit={(event) => event.preventDefault()}>
            <label className="filter-search">
              Search
              <input
                type="search"
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value)
                  update('q', event.target.value)
                }}
                placeholder="Name, college, sport, color…"
                aria-label="Search products"
              />
            </label>
            <label>
              Category
              <select value={category} onChange={(event) => update('category', event.target.value)} aria-label="Category">
                <option value="">All categories ({products.length})</option>
                {Object.entries(CATEGORY_LABELS)
                  .filter(([value]) => categoryCounts[value])
                  .map(([value, label]) => (
                    <option key={value} value={value}>
                      {label} ({categoryCounts[value]})
                    </option>
                  ))}
              </select>
            </label>
            <label>
              Price
              <select value={price} onChange={(event) => update('price', event.target.value)} aria-label="Price">
                <option value="">Any price</option>
                {Object.entries(PRICE_FILTERS).map(([value, { label }]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Sort
              <select value={sort} onChange={(event) => update('sort', event.target.value)} aria-label="Sort">
                {Object.entries(SORTS).map(([value, { label }]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
            {filtersActive && (
              <button type="button" className="filter-clear" onClick={clearFilters}>
                Clear
              </button>
            )}
          </form>
          <p className="status" aria-live="polite">
            {visible.length === products.length
              ? `${products.length} products`
              : `Showing ${visible.length} of ${products.length} products`}
          </p>
          {visible.length === 0 ? (
            <p className="status">No products match those filters. Try a different search or clear the filters.</p>
          ) : (
            <div className="product-grid">
              {visible.map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
          )}
        </>
      )}
    </>
  )
}
