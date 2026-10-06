import { Link } from 'react-router-dom'
import { formatPrice, type ProductSummary } from '../api'

// Real inventory total at or below this shows a "Low stock" ribbon (data from the inventory table).
const LOW_STOCK_THRESHOLD = 15

type ProductCardProps = {
  product: ProductSummary
  // Lazy loading suits the long Products grid; chat cards load right away because lazy
  // images inside the scrollable chat panel weren't being fetched.
  imageLoading?: 'lazy' | 'eager'
}

export default function ProductCard({ product, imageLoading = 'lazy' }: ProductCardProps) {
  const lowStock = product.total_stock !== undefined && product.total_stock <= LOW_STOCK_THRESHOLD
  return (
    <Link to={`/products/${product.product_id}`} className="product-card">
      <div className="product-card-media">
        <img src={product.image_url} alt={product.name} loading={imageLoading} />
        {lowStock && <span className="product-badge">Low stock</span>}
      </div>
      <div className="product-card-body">
        {product.garment_type && <p className="product-card-kicker">{product.garment_type}</p>}
        <h3>{product.name}</h3>
        <p className="price">{formatPrice(product.price)}</p>
        <p className="product-card-desc">{product.description}</p>
        <span className="product-card-cta" aria-hidden="true">
          View details →
        </span>
      </div>
    </Link>
  )
}
