import { useState, type ChangeEvent, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import type { RegisterInput } from '../api'
import { useAuth } from '../auth'

const MIN_PASSWORD_LENGTH = 8

const emptyForm: RegisterInput = {
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  confirm_password: '',
}

export default function CreateAccountPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState<RegisterInput>(emptyForm)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  function update(event: ChangeEvent<HTMLInputElement>) {
    setForm({ ...form, [event.target.name]: event.target.value })
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    // Quick checks here for instant feedback; the backend validates everything again.
    if (form.password.length < MIN_PASSWORD_LENGTH) {
      setError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters.`)
      return
    }
    if (form.password !== form.confirm_password) {
      setError('Passwords do not match.')
      return
    }
    setSubmitting(true)
    try {
      await register(form)
      navigate('/')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="form-page">
      <p className="eyebrow">Join Yale Bulldog Blue</p>
      <h1>Create account</h1>
      <p className="form-intro">With an account, our shopping assistant remembers your conversation between visits.</p>
      <form className="form" onSubmit={handleSubmit}>
        <label>
          First name
          <input name="first_name" autoComplete="given-name" value={form.first_name} onChange={update} required />
        </label>
        <label>
          Last name
          <input name="last_name" autoComplete="family-name" value={form.last_name} onChange={update} required />
        </label>
        <label>
          Email
          <input type="email" name="email" autoComplete="email" value={form.email} onChange={update} required />
        </label>
        <label>
          Password
          <input
            type="password"
            name="password"
            autoComplete="new-password"
            minLength={MIN_PASSWORD_LENGTH}
            value={form.password}
            onChange={update}
            required
          />
          <span className="hint">At least {MIN_PASSWORD_LENGTH} characters.</span>
        </label>
        <label>
          Confirm password
          <input
            type="password"
            name="confirm_password"
            autoComplete="new-password"
            value={form.confirm_password}
            onChange={update}
            required
          />
        </label>
        {error && (
          <p className="status error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" className="button" disabled={submitting}>
          {submitting ? 'Creating account…' : 'Create account'}
        </button>
      </form>
      <p>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  )
}
