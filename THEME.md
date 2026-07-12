# AssetFlow — Design System

This is the single source of truth for styling. **Don't write raw Tailwind
color/font utility classes on screens** — use these tokens and the shared
components in `src/components/ui/` so every screen looks consistent.

## Colors

| Token           | Hex       | Use for                                  |
|-----------------|-----------|-------------------------------------------|
| `teal`          | `#008080` | Primary actions, links, active states      |
| `teal-dark`     | `#006666` | Hover/pressed state for primary            |
| `teal-darker`   | `#00796b` | Text on light teal backgrounds             |
| `teal-light`    | `#aeeeee` | Subtle hover backgrounds                   |
| `teal-lighter`  | `#b2ebf2` | Badges, secondary button backgrounds       |
| `surface`       | `#f5f5f5` | Page background                            |
| `ink`           | `#333333` | Body text                                  |

Usage in JSX: `bg-teal`, `text-teal-dark`, `bg-surface`, `text-ink`, etc.

## Typography

- Font family: **Montserrat** (`font-sans` — already the Tailwind default
  after config, so you don't need to write `font-sans` explicitly, but it
  doesn't hurt to be explicit on headings).
- Loaded via Google Fonts `<link>` tags in `index.html` — no extra setup
  needed per component.

## Radius

- **Buttons & inputs:** `rounded-md`
- **Cards & panels:** `rounded-xl`

Don't use other radius values (`rounded-sm`, `rounded-full` on containers,
etc.) unless there's a specific reason (e.g. avatars, pills).

## Shared components

Import these instead of writing raw markup:

```jsx
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
```

### Button

```jsx
<Button variant="primary">Save Asset</Button>
<Button variant="outline">Cancel</Button>
<Button variant="danger">Delete</Button>
```
Variants: `primary` (default), `secondary`, `outline`, `ghost`, `danger`.

### Card

```jsx
<Card title="Asset Details" footer={<Button>Edit</Button>}>
  <p>Laptop — Dell XPS 15, assigned to Jaimin</p>
</Card>
```

### Input

```jsx
<Input
  id="asset-name"
  label="Asset Name"
  placeholder="e.g. Dell XPS 15"
  error={errors.name}
/>
```

## Example raw classes (only if you must go outside the components)

- **Primary button:**
  `bg-teal text-white rounded-md px-4 py-2 font-medium hover:bg-teal-dark`
- **Card:**
  `bg-white rounded-xl shadow-sm border border-gray-100 p-6`
- **Input:**
  `rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-teal`

## Rule of thumb

If you're about to type `bg-[#008080]` or `bg-blue-500` or a font name other
than Montserrat — stop. Use the token or the shared component instead. This
keeps every screen (login, dashboard, asset registration, bookings,
maintenance, reports) visually consistent without every teammate re-deriving
the palette.
