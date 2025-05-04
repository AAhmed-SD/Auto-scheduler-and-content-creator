# Premium Content Suite – Frontend Style Guide

## Table of Contents
1. [Philosophy & Design Goals](#philosophy--design-goals)
2. [Color & Theme](#color--theme)
3. [Glassmorphism](#glassmorphism)
4. [Typography](#typography)
5. [Buttons & Inputs](#buttons--inputs)
6. [Transitions & Animations](#transitions--animations)
7. [Layout & Spacing](#layout--spacing)
8. [Accessibility](#accessibility)
9. [Component Consistency & Reusability](#component-consistency--reusability)
10. [Example Class Usage](#example-class-usage)
11. [Best Practices & Anti-Patterns](#best-practices--anti-patterns)
12. [Resources & References](#resources--references)

---

## 1. Philosophy & Design Goals
- **Modern SaaS Aesthetic:** Clean, minimal, and professional with a focus on usability and clarity.
- **Dark Mode First:** The default experience is dark, with full support for light mode.
- **Glassmorphism:** Use of semi-transparent, blurred backgrounds for depth and modernity.
- **Consistency:** All components and pages should look and feel like part of the same product.
- **Responsiveness:** The UI must look great on all screen sizes.
- **Accessibility:** High contrast, clear focus states, and semantic HTML.

---

## 2. Color & Theme
- **Use Tailwind CSS custom properties for all colors.**
  Example:
  ```css
  @layer base {
    :root {
      --background: 210 40% 98%;
      --foreground: 222.2 84% 4.9%;
      --primary: 221.2 83.2% 53.3%;
      /* ... */
    }
    .dark {
      --background: 222.2 84% 4.9%;
      --foreground: 210 40% 98%;
      --primary: 217.2 91.2% 59.8%;
      /* ... */
    }
  }
  ```
- **Never hardcode hex codes or use Tailwind's default gray classes.**  
  Always use `bg-background`, `text-foreground`, `bg-primary`, etc.
- **Support both dark and light modes** using Tailwind's `dark:` variant.
- **Accent colors** (e.g., for status, highlights) should be defined in the theme and used consistently.

---

## 3. Glassmorphism
- **Cards & Major Sections:**  
  Use the `glass-card` class for all major containers.  
  Example:  
  ```html
  <div className="glass-card p-8">...</div>
  ```
  - `glass-card`:  
    `bg-white/20 dark:bg-black/20 backdrop-blur-md border border-white/20 dark:border-white/20 transition-all duration-300 ease-in-out rounded-2xl`
- **Overlays & Small Elements:**  
  Use the `glass` class for overlays, modals, or small UI elements.
- **Transparency:**  
  Use `/20` or `/10` for backgrounds and borders for a more pronounced glass effect.
- **No solid backgrounds** unless for very small elements (e.g., icons, badges).

---

## 4. Typography
- **Font Families:**  
  - UI: `Inter, sans-serif`
  - Headings (optional): `Playfair Display, serif`
- **Text Colors:**  
  - Main: `text-foreground`
  - Muted: `text-muted-foreground`
  - Never use `text-gray-*` or hardcoded colors.
- **Font Weights:**  
  - Headings: `font-bold`
  - Body: `font-normal` or `font-medium`
- **Hierarchy:**  
  - Use clear heading levels (`h1`, `h2`, etc.) and spacing.
- **Responsive Sizing:**  
  - Use Tailwind's responsive text utilities.

---

## 5. Buttons & Inputs
- **Buttons:**
  - `.btn-primary`: For main actions.  
    Example:  
    `bg-primary text-primary-foreground px-6 py-3 rounded-full hover:bg-primary-dark transition-all duration-300 ease-in-out transform hover:scale-105`
  - `.btn-secondary`: For secondary actions.  
    Example:  
    `bg-secondary text-secondary-foreground border border-secondary px-6 py-3 rounded-full hover:bg-secondary-dark transition-all duration-300 ease-in-out transform hover:scale-105`
  - **Glass Buttons:** Use `.premium-button-glass` for glassmorphic actions.
  - **Transitions:** All buttons should have smooth transitions and scale on hover.
- **Inputs:**
  - Use glassmorphic backgrounds:  
    `bg-white/10 dark:bg-white/10 border border-white/20 dark:border-white/20`
  - Use `text-foreground` and `placeholder:text-neutral-400`
  - **Focus States:**  
    `focus:ring-2 focus:ring-primary/20 focus:border-primary/40 transition-all duration-300`
  - **Rounded:**  
    Use `rounded-lg` for all inputs.

---

## 6. Transitions & Animations
- **Page Transitions:**
  - All pages should use a subtle fade/slide transition on route change.
  - Use `framer-motion` in the main layout (`App.tsx`) for this.
  - Example:
    ```tsx
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -16 }}
      transition={{ duration: 0.35, ease: 'easeInOut' }}
    >
      {children}
    </motion.div>
    ```
  - **Do not over-animate**: Keep transitions subtle and quick.
- **Component Transitions:**
  - Use `transition-all duration-300 ease-in-out` for interactive elements.
  - Use scale or shadow on hover for cards and buttons.

---

## 7. Layout & Spacing
- **Consistent Padding:**  
  Use Tailwind spacing utilities (`p-8`, `m-4`, etc.) for all containers.
- **Cards:**  
  Use `rounded-2xl` for cards, `rounded-lg` for smaller elements.
- **Sidebar/TopNav:**  
  Both should use glass backgrounds and match the main theme.
- **Responsive Design:**  
  Use Tailwind's responsive utilities for all layouts.

---

## 8. Accessibility
- **Contrast:**  
  Ensure all text and interactive elements have sufficient contrast in both light and dark modes.
- **Focus States:**  
  All buttons and inputs must have clear, visible focus rings.
- **Semantic HTML:**  
  Use correct HTML elements for structure (e.g., `<button>`, `<nav>`, `<main>`, `<section>`, etc.).
- **Keyboard Navigation:**  
  All interactive elements must be accessible via keyboard.

---

## 9. Component Consistency & Reusability
- **Reuse Classes:**  
  Always use shared utility classes (`glass`, `glass-card`, `btn-primary`, etc.) for consistency.
- **No Hardcoding:**  
  Never hardcode colors, spacing, or styles; always use theme variables and Tailwind classes.
- **Component Library:**  
  Build and use reusable components for cards, buttons, inputs, badges, etc.
- **Naming:**  
  Use clear, descriptive names for components and classes.

---

## 10. Example Class Usage
- `glass-card`:  
  `bg-white/20 dark:bg-black/20 backdrop-blur-md border border-white/20 dark:border-white/20 transition-all duration-300 ease-in-out rounded-2xl`
- `btn-primary`:  
  `bg-primary text-primary-foreground px-6 py-3 rounded-full hover:bg-primary-dark transition-all duration-300 ease-in-out transform hover:scale-105`
- `input`:  
  `bg-white/10 dark:bg-white/10 border border-white/20 dark:border-white/20 rounded-lg text-foreground placeholder:text-neutral-400 focus:ring-2 focus:ring-primary/20 focus:border-primary/40 transition-all duration-300`

---

## 11. Best Practices & Anti-Patterns
- **Do:**
  - Use Tailwind's utility classes and theme variables everywhere.
  - Keep the UI minimal, clean, and consistent.
  - Use glassmorphism for depth, not distraction.
  - Keep transitions subtle and fast.
  - Test in both dark and light modes.
- **Don't:**
  - Don't use hardcoded colors, spacing, or font sizes.
  - Don't use default gray classes (`text-gray-700`, etc.).
  - Don't over-animate or use long transitions.
  - Don't mix inconsistent border radii or paddings.

---

## 12. Resources & References
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Framer Motion Documentation](https://www.framer.com/motion/)
- [Glassmorphism Inspiration](https://glassmorphism.com/)
- [Accessible Color Palettes](https://www.smashingmagazine.com/2021/01/guide-color-accessibility-tools/)
- [Radix UI Primitives](https://www.radix-ui.com/primitives/docs/overview/introduction) (for accessible components)

---

## Summary
This style guide ensures a modern, glassy, and consistent SaaS UI with smooth transitions, strong dark mode support, and reusable component classes.  
**All new features and pages must follow these conventions for a cohesive, professional user experience.** 