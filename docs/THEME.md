# AssetFlow — Design System

Design tokens and component conventions for the AssetFlow UI. **Every teammate
must use these tokens.** Do not introduce raw hex values or default Tailwind
colors in components — always reference a named token.

---

## Color palette

| Token | Value | Use for |
|---|---|---|
| `teal` (DEFAULT) | `#008080` | Primary buttons, active nav, primary actions |
| `teal-dark` | `#006666` | Button hover state |
| `teal-darker` | `#00796b` | Headings, logo text |
| `teal-light` | `#aeeeee` | Section backgrounds, accent bands |
| `teal-lighter` | `#b2ebf2` | Tabs / pills background (active & inactive) |
| `surface` | `#f5f5f5` | Page background |
| `ink` | `#333333` | Body text |
| `amber` | `#f59e0b` | Under Maintenance status text/icon |
| `amber-light` | `#fef3c7` | Under Maintenance status pill background |
| `red` | `#ef4444` | Lost status text/icon |
| `red-light` | `#fee2e2` | Lost status pill background |

> **Rule:** hover states shift one step darker on the same ramp
> (e.g. `bg-teal` → `hover:bg-teal-dark`). Never use an arbitrary hover color.

---

## Typography

- **Font:** Montserrat (imported via Google Fonts in `index.html`)
- **Fallback:** `sans-serif`
- **Base size:** 16 px, line-height 1.6

---

## Shape & elevation

| Context | Class | Approx radius |
|---|---|---|
| Buttons, inputs | `rounded-md` | 4–6 px |
| Cards, panels | `rounded-xl` | 10–14 px |
| Pills / badges | `rounded-full` | fully round |

**Optional glassmorphism (hero / login panels):**
```css
background: rgba(255, 255, 255, 0.32);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.4);
```

---

## `tailwind.config.js` extension

```js
theme: {
  extend: {
    colors: {
      teal: {
        DEFAULT: '#008080',
        dark:    '#006666',
        darker:  '#00796b',
        light:   '#aeeeee',
        lighter: '#b2ebf2',
      },
      surface: '#f5f5f5',
      ink:     '#333333',
    },
    fontFamily: {
      sans: ['Montserrat', 'sans-serif'],
    },
  },
},
```

---

## Shared component reference

All components live in `src/components/ui/`. Import from the barrel:
```js
import { Button, Card, Input, StatusPill } from '@/components/ui';
```

### `<Button>`

```jsx
// Primary (default)
<Button>Save Changes</Button>
// className applied: bg-teal hover:bg-teal-dark text-white font-medium
//                    px-4 py-2 rounded-md transition-colors duration-150

// Secondary / outline variant
<Button variant="outline">Cancel</Button>
// className: border border-teal text-teal hover:bg-teal-lighter rounded-md

// Danger variant
<Button variant="danger">Delete</Button>
// className: bg-red-600 hover:bg-red-700 text-white rounded-md
```

### `<Card>`

```jsx
// Default — white card with shadow
<Card>content</Card>
// className: bg-white rounded-xl shadow-sm p-6

// Flat variant — surface background, no shadow
<Card variant="flat">content</Card>
// className: bg-surface rounded-xl p-6

// Glass variant — for hero / login panels
<Card variant="glass">content</Card>
// style: background rgba(255,255,255,.32); backdrop-filter blur(10px)
// className: rounded-xl border border-white/40 p-8
```

### `<Input>`

```jsx
<Input label="Asset Tag" placeholder="AF-0001" />
// wrapper: flex flex-col gap-1
// label:   text-sm font-medium text-ink
// input:   w-full border border-gray-300 rounded-md px-3 py-2 text-ink
//          focus:outline-none focus:border-teal focus:ring-1 focus:ring-teal
//          transition-colors duration-150
```

### `<StatusPill>`

Default pattern: `bg-teal-lighter text-teal-darker` — extend only when a module
genuinely needs a different semantic color.

```jsx
<StatusPill status="Available" />   // bg-teal-lighter text-teal-darker
<StatusPill status="Allocated" />   // bg-blue-100 text-blue-700
<StatusPill status="Under Maintenance" /> // bg-amber-100 text-amber-700
<StatusPill status="Lost" />        // bg-red-100 text-red-700
<StatusPill status="Retired" />     // bg-gray-200 text-gray-600
```

> **Adding a new status color:** add it to `tailwind.config.js` AND to this
> table before using it anywhere, so it stays consistent across modules.

---

## Registered additional colors

*(Log every new addition here before using it in a component)*

| Color | Hex | Used for |
|---|---|---|
| — | — | — |
