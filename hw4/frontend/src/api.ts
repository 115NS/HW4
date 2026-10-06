export type InventoryItem = {
  size: string
  quantity: number
}

export type Product = {
  product_id: string
  name: string
  garment_type: string
  category: string
  description: string
  colors: string[]
  search_tags: string[]
  image_file_path: string
  image_url: string
  price: number
  inventory: InventoryItem[]
  total_stock: number
}

// The fields every product card needs. Products from /api/products and product cards
// returned by /api/chat (backend models.ProductCard) both have them, so both render with ProductCard.
export type ProductSummary = Pick<Product, 'product_id' | 'name' | 'price' | 'description' | 'image_url'> &
  Partial<Pick<Product, 'garment_type' | 'total_stock'>>

export type ChatProductCard = ProductSummary & {
  garment_type: string
  total_stock: number
}

export type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
  products?: ChatProductCard[]
  // Follow-up questions the agent suggests; shown as clickable chips under its latest reply.
  suggestions?: string[]
  // UI-only messages (the greeting, error notices) are never sent to the agent as history.
  uiOnly?: boolean
}

export type PageContext = {
  path: string
  product_id: string | null
}

export type User = {
  id: number
  name: string
  first_name: string | null
  last_name: string | null
  email: string
  created_at: string
}

export type RegisterInput = {
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string
}

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(response.status === 404 ? 'Not found' : `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

async function postJson<T>(url: string, body?: unknown): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body ?? {}),
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    // FastAPI sends { detail: "message" } for our errors, or a list for request-shape errors.
    const detail = data?.detail
    throw new Error(typeof detail === 'string' ? detail : 'Please check the form and try again.')
  }
  return data as T
}

export async function fetchCurrentUser(): Promise<User | null> {
  return (await getJson<{ user: User | null }>('/api/auth/me')).user
}

export async function login(email: string, password: string): Promise<User> {
  return (await postJson<{ user: User }>('/api/auth/login', { email, password })).user
}

export async function register(input: RegisterInput): Promise<User> {
  return (await postJson<{ user: User }>('/api/auth/register', input)).user
}

export async function logout(): Promise<void> {
  await postJson('/api/auth/logout')
}

export function fetchProducts(): Promise<Product[]> {
  return getJson<Product[]>('/api/products')
}

export function fetchProduct(productId: string): Promise<Product> {
  return getJson<Product>(`/api/products/${encodeURIComponent(productId)}`)
}

// Sends the new message, the earlier turns, and the current page to the FastAPI agent.
// The backend uses `history` only for guests; logged-in shoppers' history comes from the database.
export async function sendChatMessage(message: string, history: ChatMessage[], page: PageContext): Promise<ChatMessage> {
  const data = await postJson<{ reply: string; products: ChatProductCard[]; suggestions?: string[] }>('/api/chat', {
    message,
    history: history
      .filter((turn) => !turn.uiOnly)
      .map(({ role, content, products }) => ({
        role,
        content,
        product_ids: (products ?? []).map((product) => product.product_id),
      })),
    page,
  })
  return { role: 'assistant', content: data.reply, products: data.products, suggestions: data.suggestions ?? [] }
}

// The logged-in shopper's saved conversation (empty for guests).
export async function fetchChatHistory(): Promise<ChatMessage[]> {
  const data = await getJson<{ messages: { role: 'user' | 'assistant'; content: string; products: ChatProductCard[] }[] }>(
    '/api/chat/history',
  )
  return data.messages.map(({ role, content, products }) => ({ role, content, products }))
}

export function formatPrice(price: number): string {
  return `$${price.toFixed(2)}`
}
