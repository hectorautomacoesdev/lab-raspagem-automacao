import { NavLink } from 'react-router-dom'
import { nav } from '../nav'

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="px-3 py-4 text-sm">
      {nav.map((group) => (
        <div key={group.title} className="mb-5">
          <p className="px-2 mb-1 text-xs font-semibold uppercase tracking-wider text-slate-400">
            {group.title}
          </p>
          <ul className="space-y-0.5">
            {group.items.map((item) => (
              <li key={item.slug}>
                <NavLink
                  to={`/${item.slug}`}
                  onClick={onNavigate}
                  className={({ isActive }) =>
                    [
                      'block rounded-md px-2 py-1.5 transition-colors',
                      isActive
                        ? 'bg-indigo-600 text-white font-medium'
                        : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800',
                    ].join(' ')
                  }
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  )
}
