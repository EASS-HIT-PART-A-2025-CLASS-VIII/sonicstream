---
description: Design system and layout rules for new feature pages
---

# SonicStream Feature Page Design Rules

Follow these rules when creating any new feature page to ensure consistent UI/UX across the application.

## 1. Layout Structure

Every feature page MUST have its own `layout.tsx` file in its directory:

```tsx
// app/[feature-name]/layout.tsx
import Sidebar from "@/components/layout/Sidebar";
import MobileNav from "@/components/layout/MobileNav";

export default function FeatureLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-black text-white">
            <Sidebar />
            <main className="md:pl-64 pb-20 md:pb-0 min-h-screen">
                <div className="container mx-auto p-6 md:p-10 max-w-7xl">
                    {children}
                </div>
            </main>
            <MobileNav />
        </div>
    );
}
```

**Key elements:**
- `<Sidebar />` - Left navigation panel
- `<MobileNav />` - Bottom navigation for mobile
- `md:pl-64` - Accounts for sidebar width on desktop
- `pb-20 md:pb-0` - Accounts for mobile nav height
- `container mx-auto p-6 md:p-10 max-w-7xl` - Content container

## 2. Page Structure

Every feature page should follow this structure:

```tsx
// app/[feature-name]/page.tsx
"use client"

import { useState } from "react";
import { Loader2, AlertCircle } from "lucide-react";

export default function FeaturePage() {
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    return (
        <div className="py-6">
            {/* Header Section */}
            <div className="mb-8">
                <h1 className="text-3xl md:text-4xl font-bold mb-2">Page Title</h1>
                <p className="text-muted-foreground">Page description</p>
            </div>

            {/* Error Message (if applicable) */}
            {error && (
                <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center gap-3">
                    <AlertCircle className="h-5 w-5 text-destructive" />
                    <p className="text-sm">{error}</p>
                </div>
            )}

            {/* Content Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {/* Content items */}
            </div>

            {/* Loading State */}
            {isLoading && (
                <div className="flex justify-center items-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
            )}

            {/* Empty State */}
            {!isLoading && items.length === 0 && !error && (
                <div className="text-center py-12 text-muted-foreground">
                    No items found. Try refreshing the page.
                </div>
            )}
        </div>
    );
}
```

## 3. Card Components

All cards should use this exact styling:

```tsx
<div className="group relative bg-[#181818] p-4 rounded-xl hover:bg-[#282828] transition-all duration-300">
    {/* Image Container */}
    <div className="relative aspect-square mb-4 rounded-lg overflow-hidden shadow-lg bg-[#282828]">
        <Image
            src={imageUrl}
            alt={title}
            width={300}
            height={300}
            className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500"
            unoptimized
        />
    </div>
    
    {/* Text Content */}
    <div className="space-y-1">
        <h3 className="font-bold text-white truncate">{title}</h3>
        <p className="text-sm text-[#a7a7a7] truncate">{subtitle}</p>
    </div>
</div>
```

**Card styling rules:**
- Background: `bg-[#181818]` → `hover:bg-[#282828]`
- Padding: `p-4`
- Border radius: `rounded-xl`
- Image container: `aspect-square mb-4 rounded-lg shadow-lg bg-[#282828]`
- Image hover: `group-hover:scale-105 transition-transform duration-500`
- Title: `font-bold text-white truncate`
- Subtitle: `text-sm text-[#a7a7a7] truncate`

## 4. Color Palette

**Primary Colors:**
- Primary (Neon Green): `bg-primary` / `text-primary` / `#1ed760`
- Background: `bg-black` / `#000000`
- Card Background: `bg-[#181818]`
- Card Hover: `bg-[#282828]`

**Text Colors:**
- Primary Text: `text-white`
- Secondary Text: `text-[#a7a7a7]` or `text-muted-foreground`
- Destructive: `text-destructive`

**Borders:**
- Subtle: `border-white/5` or `border-white/10`
- Visible: `border-white/20`

## 5. Buttons

**Primary Button (CTA):**
```tsx
<button className="h-12 px-6 bg-primary hover:bg-primary/90 text-black font-bold rounded-full transition-colors">
    Button Text
</button>
```

**Secondary Button:**
```tsx
<button className="h-12 px-6 border border-white/10 hover:bg-white/5 text-white font-semibold rounded-full transition-colors">
    Button Text
</button>
```

## 6. Grid Layouts

**Standard responsive grid:**
```tsx
<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
    {/* Items */}
</div>
```

**Breakpoints:**
- Mobile: 2 columns
- Tablet (md): 3 columns
- Desktop (lg): 4 columns
- Large Desktop (xl): 5 columns
- Gap: `gap-6` (24px)

## 7. Typography

**Page Titles:**
```tsx
<h1 className="text-3xl md:text-4xl font-bold mb-2">Title</h1>
```

**Descriptions:**
```tsx
<p className="text-muted-foreground">Description text</p>
```

**Card Titles:**
```tsx
<h3 className="font-bold text-white truncate">Card Title</h3>
```

**Card Subtitles:**
```tsx
<p className="text-sm text-[#a7a7a7] truncate">Subtitle</p>
```

## 8. Loading & Error States

**Loading Spinner:**
```tsx
<div className="flex justify-center items-center py-12">
    <Loader2 className="h-8 w-8 animate-spin text-primary" />
</div>
```

**Error Message:**
```tsx
<div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center gap-3">
    <AlertCircle className="h-5 w-5 text-destructive" />
    <p className="text-sm">{error}</p>
</div>
```

**Empty State:**
```tsx
<div className="text-center py-12 text-muted-foreground">
    No items found. Try refreshing the page.
</div>
```

## 9. Checklist for New Features

When adding a new feature page:

- [ ] Create `app/[feature-name]/layout.tsx` with Sidebar and MobileNav
- [ ] Create `app/[feature-name]/page.tsx` with standard structure
- [ ] Use `py-6` container wrapper
- [ ] Add header with `text-3xl md:text-4xl font-bold mb-2` title
- [ ] Use standard grid: `grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6`
- [ ] Style cards with `bg-[#181818]` → `hover:bg-[#282828]`
- [ ] Add loading state with `Loader2` spinner
- [ ] Add error state with destructive styling
- [ ] Add empty state message
- [ ] Use `text-[#a7a7a7]` for secondary text
- [ ] Ensure all images have `group-hover:scale-105` effect
- [ ] Test on mobile, tablet, and desktop breakpoints

## 10. Reference Pages

Use these existing pages as templates:
- **Discovery** (`app/discovery/`) - Standard grid layout
- **Favorites** (`app/favorites/`) - Similar card structure
- **Recommendations** (`app/recommendations/`) - Selection + results flow

## 11. Common Mistakes to Avoid

❌ **Don't:**
- Use custom gradients or backgrounds (stick to `bg-black`)
- Create pages without `layout.tsx` (sidebar will disappear)
- Use different card hover colors
- Mix color values (use exact hex codes)
- Use different grid breakpoints
- Forget mobile navigation spacing (`pb-20 md:pb-0`)

✅ **Do:**
- Copy existing layout.tsx exactly
- Use exact color values from this guide
- Test on all breakpoints
- Include loading/error/empty states
- Use consistent spacing (`gap-6`, `mb-8`, `py-6`)
