import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, formatPrice, type Product } from '../api'
import { OPEN_CHAT_EVENT } from '../components/ChatWidget'

function stockLabel(quantity: number): string {
  if (quantity === 0) return 'Sold out'
  if (quantity <= 5) return `Only ${quantity} left`
  return `${quantity} in stock`
}

export default function ProductPage() {
  const { productId = '' } = useParams()
  // Results are tagged with the product id they belong to, so a stale result is ignored while the next loads.
  const [result, setResult] = useState<{ id: string; product?: Product; error?: string } | null>(null)

  useEffect(() => {
    fetchProduct(productId)
      .then((product) => setResult({ id: productId, product }))
      .catch((err: Error) => setResult({ id: productId, error: err.message }))
  }, [productId])

  const current = result?.id === productId ? result : null
  const product = current?.product ?? null
  const error = current?.error ?? null

  if (error) {
    return (
      <>
        <p className="status error">
          {error === 'Not found' ? 'We couldn’t find that product.' : `Could not load product: ${error}`}
        </p>
        <Link to="/products">← Back to products</Link>
      </>
    )
  }
  if (!product) return <p className="status">Loading product…</p>

  return (
    <>
      <Link to="/products" className="back-link">
        ← Back to products
      </Link>
      <div className="product-detail">
        <img src={product.image_url} alt={product.name} className="product-detail-image" />
        <div className="product-detail-info">
          <p className="eyebrow">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="price large">{formatPrice(product.price)}</p>
          <p>{product.description}</p>

          <h2>Colors</h2>
          <ul className="chips">
            {product.colors.map((color) => (
              <li key={color}>{color}</li>
            ))}
          </ul>

          <h2>Sizes &amp; stock</h2>
          {product.inventory.length === 0 ? (
            <p>No size information available.</p>
          ) : (
            <table className="stock-table">
              <thead>
                <tr>
                  <th>Size</th>
                  <th>Availability</th>
                </tr>
              </thead>
              <tbody>
                {product.inventory.map((item) => (
                  <tr key={item.size} className={item.quantity === 0 ? 'sold-out' : undefined}>
                    <td>{item.size}</td>
                    <td>{stockLabel(item.quantity)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <p className="status">{product.total_stock} units in stock across all sizes</p>
          <div className="product-actions">
            <button type="button" className="button" onClick={() => window.dispatchEvent(new Event(OPEN_CHAT_EVENT))}>
              Ask about this item
            </button>
            <Link to="/products" className="button button-ghost">
              Keep browsing
            </Link>
          </div>
          <ul className="trust-list">
            <li>Official Yale merchandise</li>
            <li>Shop in person at 57 Broadway, New Haven</li>
            <li>Stock shown live from our inventory</li>
          </ul>
        </div>
      </div>
    </>
  )
}
