# Design

## Meta

| Field | Value |
|-------|-------|
| version | 1.0 |
| last_updated | 2026-06-21 |
| author | Design System Team |

## Tokens

### Color

#### Brand Colors
| Token | Value (HEX) | Value (OKLCH) | Usage |
|-------|-------------|---------------|-------|
| rand-mint | #4ECDC4 | oklch(0.78 0.15 176) | Primary brand color, buttons, highlights |
| rand-dark | #2A7E76 | oklch(0.50 0.12 175) | Darker variant, hover states, text |
| rand-light | #A8E6CF | oklch(0.88 0.10 158) | Lighter variant, backgrounds, accents |

#### Accent Colors
| Token | Value (HEX) | Value (OKLCH) | Usage |
|-------|-------------|---------------|-------|
| ccent-orange | #FF9F43 | oklch(0.75 0.20 32) | Warnings, notifications, progress |
| ccent-coral | #FF6B6B | oklch(0.70 0.20 0) | Errors, delete actions, danger |
| ccent-lavender | #A29BFE | oklch(0.78 0.15 245) | Info, tags, decorative elements |
| ccent-sky | #74B9FF | oklch(0.78 0.15 208) | Links, secondary emphasis |

#### Functional Colors
| Token | Value (HEX) | Value (OKLCH) | Usage |
|-------|-------------|---------------|-------|
| success | #00B894 | oklch(0.65 0.18 168) | Success states, checkmarks |
| warning | #FDCB6E | oklch(0.85 0.15 45) | Warnings, pending states |
| error | #E17055 | oklch(0.60 0.18 9) | Errors, failure states |
| info | #0984E3 | oklch(0.55 0.20 207) | Information, help text |

#### Neutral Colors
| Token | Value (HEX) | Value (OKLCH) | Usage |
|-------|-------------|---------------|-------|
| 	ext-primary | #2D3436 | oklch(0.25 0.01 200) | Primary text, headings |
| 	ext-secondary | #636E72 | oklch(0.45 0.01 205) | Secondary text, descriptions |
| 	ext-light | #B2BEC3 | oklch(0.70 0.01 200) | Placeholder, disabled text |
| order | #E8ECF0 | oklch(0.92 0.01 210) | Dividers, input borders |
| ackground-primary | #FFFFFF | oklch(1.00 0 0) | Page background |
| ackground-secondary | #F8FAFC | oklch(0.98 0.005 210) | Card backgrounds |
| ackground-dark | #F1F5F9 | oklch(0.96 0.008 210) | Hover states, sections |

### Typography

#### Font Families
| Token | Value | Usage |
|-------|-------|-------|
| ont-sans | Inter, system-ui, sans-serif | Body text, headings |
| ont-mono | JetBrains Mono, Consolas, monospace | Code blocks, technical text |

#### Font Weights
| Token | Value | Usage |
|-------|-------|-------|
| ont-weight-regular | 400 | Body text |
| ont-weight-medium | 500 | Buttons, emphasized text |
| ont-weight-semibold | 600 | Headings, strong emphasis |
| ont-weight-bold | 700 | Main headings |

#### Font Sizes
| Token | Value | Line Height | Usage |
|-------|-------|-------------|-------|
| 	ext-xs | 12px | 1.4 | Captions, timestamps |
| 	ext-sm | 13px | 1.5 | Secondary text, labels |
| 	ext-base | 14px | 1.5 | Body text, forms |
| 	ext-lg | 16px | 1.5 | Primary content |
| 	ext-xl | 18px | 1.4 | Section headings |
| 	ext-2xl | 22px | 1.35 | Page subheadings |
| 	ext-3xl | 28px | 1.3 | Page headings |

### Spacing

#### Base Unit
- Base: 4px
- All spacing values are multiples of base unit

#### Spacing Scale
| Token | Value | Usage |
|-------|-------|-------|
| space-1 | 4px | Compact spacing |
| space-2 | 8px | Small spacing |
| space-3 | 12px | Medium spacing |
| space-4 | 16px | Standard spacing |
| space-5 | 20px | Large spacing |
| space-6 | 24px | Extra large spacing |
| space-8 | 32px | Section spacing |
| space-12 | 48px | Major sections |

### Border Radius
| Token | Value | Usage |
|-------|-------|-------|
| adius-sm | 4px | Small elements |
| adius-md | 8px | Buttons, inputs |
| adius-lg | 12px | Cards, containers |
| adius-xl | 16px | Large containers |

### Shadows
| Token | Value | Usage |
|-------|-------|-------|
| shadow-soft | 0 2px 8px rgba(0,0,0,0.06) | Cards, hover states |
| shadow-medium | 0 4px 16px rgba(0,0,0,0.1) | Elevated elements |
| shadow-large | 0 8px 32px rgba(0,0,0,0.15) | Modals, dropdowns |

## Components

### Button
| Property | Primary | Secondary | Ghost | Danger |
|----------|---------|-----------|-------|--------|
| Background | rand-mint | ackground-secondary | transparent | ccent-coral |
| Background Hover | rand-dark | ackground-dark | ackground-dark | error |
| Text Color | white | 	ext-primary | rand-mint | white |
| Border | none | order | rand-mint | none |
| Border Width | - | 1px | 1px | - |
| Border Radius | adius-md | adius-md | adius-md | adius-md |
| Padding | 8px 16px | 8px 16px | 8px 16px | 8px 16px |
| Font Weight | 500 | 500 | 500 | 500 |

### Input
| Property | Value |
|----------|-------|
| Height | 40px |
| Padding | 10px 12px |
| Border | 1px order |
| Border Focus | 2px rand-mint |
| Border Error | 1px ccent-coral |
| Border Radius | adius-md |
| Text Color | 	ext-primary |
| Placeholder Color | 	ext-light |
| Background | ackground-primary |

### Card
| Property | Value |
|----------|-------|
| Background | ackground-primary |
| Border | 1px order |
| Border Radius | adius-lg |
| Padding | space-4 |
| Shadow | shadow-soft |
| Hover Shadow | shadow-medium |

### Message Bubble
| Property | User | Assistant |
|----------|------|-----------|
| Background | rand-mint | ackground-secondary |
| Text Color | white | 	ext-primary |
| Border Radius | 16px 16px 4px 16px | 16px 16px 16px 4px |
| Padding | 12px 16px | 12px 16px |
| Max Width | 70% | 70% |

### Tag
| Property | Value |
|----------|-------|
| Background | ackground-dark |
| Text Color | 	ext-secondary |
| Border Radius | adius-sm |
| Padding | 4px 8px |
| Font Size | 	ext-xs |

## Layout

### Grid System
- Columns: 12
- Gutter: 16px

### Responsive Breakpoints
| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 768px | Single column |
| Tablet | 768px - 1024px | Two columns |
| Desktop | > 1024px | Full layout |

### Container
- Max Width: 1200px
- Side Padding: 24px (mobile: 16px)

## Motion

### Transitions
| Token | Duration | Easing | Usage |
|-------|----------|--------|-------|
| 	ransition-fast | 150ms | ease-out | Quick interactions |
| 	ransition-normal | 200ms | ease-out | Standard interactions |
| 	ransition-slow | 300ms | ease-out | Page transitions |

### Animations
| Name | Keyframes | Usage |
|------|-----------|-------|
| slide-in | From opacity 0, translateY 10px | Modals, dropdowns |
| ade-in | From opacity 0 | Page sections |
| scale-in | From opacity 0, scale 0.95 | Focus states |

### Reduced Motion
- Respect prefers-reduced-motion: reduce
- Provide static alternatives for all animations
