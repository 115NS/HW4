import { useEffect, useRef, useState, type FormEvent } from 'react'
import { matchPath, useLocation } from 'react-router-dom'
import { fetchChatHistory, sendChatMessage, type ChatMessage } from '../api'
import { useAuth } from '../auth'
import ProductCard from './ProductCard'

const QUICK_STARTS = ['What hoodies do you have?', 'What do you have in stock?', 'Help me find Yale gear.']
const MASCOT_SRC = '/images/handsome-dan-kingman.jpg'
// Other parts of the site (e.g. "Ask about this item" on a product page) open the chat with this event.
export const OPEN_CHAT_EVENT = 'campus-customs:open-chat'

// App remounts this component (key = user id) when someone logs in or out,
// so one shopper's conversation is never shown to the next.
export default function ChatWidget() {
  const { user } = useAuth()
  const location = useLocation()
  const greeting: ChatMessage = {
    role: 'assistant',
    content: user
      ? `Hi ${user.first_name || user.name}! I’m the Campus Customs assistant. Ask me about our Yale gear.`
      : 'Hi! I’m the Campus Customs assistant. Ask me about our Yale gear.',
    uiOnly: true,
  }
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([greeting])
  const [input, setInput] = useState('')
  const [waiting, setWaiting] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  // Logged-in shoppers pick up their saved conversation. userId is fixed for each mount.
  const userId = user?.id
  useEffect(() => {
    if (userId === undefined) return
    let cancelled = false
    fetchChatHistory()
      .then((saved) => {
        if (!cancelled) setMessages((current) => [current[0], ...saved, ...current.slice(1)])
      })
      .catch(() => undefined)
    return () => {
      cancelled = true
    }
  }, [userId])

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'end' })
  }, [messages, waiting, open])

  useEffect(() => {
    const openChat = () => setOpen(true)
    window.addEventListener(OPEN_CHAT_EVENT, openChat)
    return () => window.removeEventListener(OPEN_CHAT_EVENT, openChat)
  }, [])

  // On a single-product page, tell the agent which product "this" refers to.
  const productMatch = matchPath('/products/:productId', location.pathname)
  const onProductPage = Boolean(productMatch)

  // Before the first message: quick-start questions (plus one about the product being viewed).
  // After a reply: the agent's own follow-up suggestions for that reply.
  const conversationStarted = messages.some((message) => !message.uiOnly)
  const lastMessage = messages[messages.length - 1]
  const chips = waiting
    ? []
    : !conversationStarted
      ? [...(onProductPage ? ['What sizes of this are in stock?'] : []), ...QUICK_STARTS]
      : lastMessage.role === 'assistant'
        ? (lastMessage.suggestions ?? [])
        : []

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    void send(input)
  }

  // Both typed messages and clicked suggestions go through this same flow.
  async function send(rawText: string) {
    const text = rawText.trim()
    if (!text || waiting) return
    const history = messages
    const page = { path: location.pathname, product_id: productMatch?.params.productId ?? null }
    setMessages([...messages, { role: 'user', content: text }])
    setInput('')
    setWaiting(true)
    try {
      const reply = await sendChatMessage(text, history, page)
      setMessages((current) => [...current, reply])
    } catch (err) {
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: (err as Error).message || 'Sorry, something went wrong. Please try again.',
          uiOnly: true,
        },
      ])
    } finally {
      setWaiting(false)
    }
  }

  return (
    <div className="chat">
      {open && (
        <section className="chat-panel" aria-label="Chat with Campus Customs">
          <header className="chat-header">
            <span className="mascot-avatar chat-avatar">
              <img src={MASCOT_SRC} alt="" />
            </span>
            <div className="chat-title">
              <span>Campus Customs Assistant</span>
              <small>Styles, sizes &amp; stock · Yale Bulldog Blue</small>
            </div>
            <button type="button" onClick={() => setOpen(false)} aria-label="Close chat">
              ×
            </button>
          </header>
          <div className="chat-messages">
            {messages.map((message, index) => (
              <div key={index} className={`chat-turn ${message.role}`}>
                <div className={`chat-bubble ${message.role}`}>{message.content}</div>
                {message.products && message.products.length > 0 && (
                  <div className="chat-products" aria-label={`${message.products.length} matching products`}>
                    {message.products.map((product) => (
                      <ProductCard key={product.product_id} product={product} imageLoading="eager" />
                    ))}
                  </div>
                )}
              </div>
            ))}
            {chips.length > 0 && (
              <div className="chat-suggestions" aria-label="Suggested questions">
                {chips.map((chip) => (
                  <button key={chip} type="button" className="chat-chip" onClick={() => void send(chip)}>
                    {chip}
                  </button>
                ))}
              </div>
            )}
            {waiting && (
              <div className="chat-bubble assistant typing" aria-label="Assistant is typing">
                <span />
                <span />
                <span />
              </div>
            )}
            <div ref={endRef} />
          </div>
          <form className="chat-input" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Type a message…"
              aria-label="Chat message"
              autoFocus
            />
            <button type="submit" disabled={!input.trim() || waiting}>
              Send
            </button>
          </form>
        </section>
      )}
      <button
        type="button"
        className="chat-toggle"
        onClick={() => setOpen((value) => !value)}
        aria-label={open ? 'Close chat' : 'Open chat'}
      >
        {open ? (
          <span className="chat-toggle-close">×</span>
        ) : (
          <>
            <span className="mascot-avatar chat-toggle-avatar">
              <img src={MASCOT_SRC} alt="" />
            </span>
            <span className="chat-toggle-label">Chat</span>
          </>
        )}
      </button>
    </div>
  )
}
