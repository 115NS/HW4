import { Link } from 'react-router-dom'
import { CATEGORY_LABELS } from '../brand/categories'
import YaleShield from './YaleShield'

const FOOTER_CATEGORIES = ['hoodie', 'crewneck', 't-shirt', 'quarter-zip', 'jacket']

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <YaleShield size={34} />
          <div>
            <p className="footer-title">Yale Bulldog Blue</p>
            <p>Campus Customs has outfitted Bulldogs, families, and alumni from across the street from campus since 1975.</p>
          </div>
        </div>
        <div>
          <h2>Visit</h2>
          <ul>
            <li>57 Broadway, New Haven, CT 06511</li>
            <li>Open 7 days a week</li>
            <li>(203) 789-2157</li>
            <li>team@campuscustoms.com</li>
          </ul>
        </div>
        <div>
          <h2>Shop</h2>
          <ul>
            <li>
              <Link to="/products">All products</Link>
            </li>
            {FOOTER_CATEGORIES.map((category) => (
              <li key={category}>
                <Link to={`/products?category=${category}`}>{CATEGORY_LABELS[category]}</Link>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="footer-legal">
        <p>Campus Customs · 57 Broadway, New Haven, CT 06511 · Open 7 days a week</p>
        <p className="footer-note">
          A class project inspired by Yale Bulldog Blue. Not an official store site. Handsome Dan XIX photo:{' '}
          <a href="https://commons.wikimedia.org/wiki/File:Handsome_Dan_Kingman.jpg" target="_blank" rel="noreferrer">
            Joeshmonobody
          </a>
          ,{' '}
          <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noreferrer">
            CC BY-SA 4.0
          </a>
          .
        </p>
      </div>
    </footer>
  )
}
