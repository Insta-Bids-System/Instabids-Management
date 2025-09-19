# UI Development Guide - Parallel Web & Mobile

## 🎯 Core Philosophy

**Build UI for BOTH platforms simultaneously** - Every feature gets implemented for web (Next.js) and mobile (React Native) at the same time to maintain feature parity and prevent technical debt.

## 📐 Architecture Overview

```
InstaBids-Management/
├── packages/shared/        # SHARED LOGIC (10-15% of code)
│   ├── types/             # TypeScript interfaces
│   ├── schemas/           # Zod validation
│   └── api/               # API client functions
├── web/                   # WEB UI (45% of code)
│   └── src/components/    # Next.js + Tailwind components
└── mobile/                # MOBILE UI (45% of code)
    └── src/               # React Native components
```

## ✅ What to Share

### Always Share These:
```typescript
// packages/shared/types/[feature].ts
export interface Property {
  id: string;
  address: string;
  // Same types for both platforms
}

// packages/shared/schemas/[feature].ts
export const propertySchema = z.object({
  address: z.string().min(5),
  // Same validation everywhere
});

// packages/shared/api/[feature].ts
export const propertiesApi = {
  async getProperties() {
    // Same API calls
  }
};
```

## ❌ What NOT to Share

### Keep These Separate:
- UI Components (Button, Card, Modal)
- Styling systems (Tailwind vs StyleSheet)
- Navigation patterns
- Platform-specific features (camera, push notifications)
- Complex tables (web only)
- Touch gestures (mobile only)

## 📝 Development Workflow

### When Building a New Feature:

1. **Start with Shared Logic**
```bash
# Create types first
packages/shared/src/types/[feature].ts
packages/shared/src/schemas/[feature].ts
packages/shared/src/api/[feature].ts
```

2. **Build Web UI**
```bash
# Next.js component with Tailwind
web/src/components/[feature]/[Component].tsx
```

3. **Build Mobile UI**
```bash
# React Native component with StyleSheet
mobile/src/screens/[Feature]Screen.tsx
mobile/src/components/[Component].tsx
```

## 🎨 UI Consistency Rules

### Colors (Must Match)
```typescript
// Web (Tailwind)
'blue-600'    = '#2563EB'
'gray-600'    = '#4B5563'
'red-600'     = '#DC2626'
'green-600'   = '#059669'

// Mobile (React Native)
colors = {
  primary: '#2563EB',
  secondary: '#4B5563',
  danger: '#DC2626',
  success: '#059669',
}
```

### Spacing (Consistent Scale)
```typescript
// Web (Tailwind)
'p-4' = 16px
'p-6' = 24px
'gap-4' = 16px

// Mobile
padding: 16,
padding: 24,
gap: 16,
```

### Typography
```typescript
// Web
'text-sm' = 14px
'text-base' = 16px
'text-lg' = 18px
'font-semibold' = 600

// Mobile
fontSize: 14,
fontSize: 16,
fontSize: 18,
fontWeight: '600',
```

## 🔧 Component Examples

### Example: Property Card

**Web Version** (web/src/components/properties/PropertyCard.tsx):
```tsx
export default function PropertyCard({ property }: Props) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="font-semibold">{property.address}</h3>
      {/* Tailwind CSS classes */}
    </div>
  );
}
```

**Mobile Version** (mobile/src/components/PropertyCard.tsx):
```tsx
export default function PropertyCard({ property }: Props) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{property.address}</Text>
      {/* React Native StyleSheet */}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
  }
});
```

**Shared Logic** (packages/shared/api/properties.ts):
```typescript
// Both platforms use this
export async function getProperties(): Promise<Property[]> {
  const response = await fetch(`${API_URL}/api/properties`);
  return response.json();
}
```

## 📋 Checklist for Every Feature

When implementing a feature, ensure:

- [ ] Types defined in `packages/shared/types/`
- [ ] Validation schemas in `packages/shared/schemas/`
- [ ] API functions in `packages/shared/api/`
- [ ] Web component built with Tailwind
- [ ] Mobile component built with StyleSheet
- [ ] Both use same shared logic
- [ ] Colors match between platforms
- [ ] Spacing is consistent
- [ ] User flow is identical

## 🚀 Best Practices (2025)

### Based on Latest Expo/React Native Guidelines:

1. **Use Expo SDK 53+** - Supports new architecture
2. **Leverage EAS Build** - Cloud builds without Xcode/Android Studio
3. **NativeWind for Mobile** - Tailwind-like styling for React Native
4. **React Hook Form** - Same form library for both platforms
5. **Zod Validation** - Universal schema validation
6. **TypeScript Strict** - Full type safety everywhere
7. **Expo Router** - File-based routing like Next.js
8. **React Query/SWR** - Same data fetching for both

## 🎯 Platform-Specific Patterns

### Web-Only Features:
- Data tables with sorting/filtering
- Complex modals with multiple steps
- Keyboard shortcuts
- Hover effects
- Right-click menus

### Mobile-Only Features:
- Pull-to-refresh
- Swipe gestures
- Bottom sheets
- Haptic feedback
- Native camera integration

### Different Implementations:
```typescript
// Web: Multi-select with checkboxes
<table>
  <input type="checkbox" />
</table>

// Mobile: Multi-select with long press
<FlatList
  onLongPress={handleSelect}
/>
```

## 📊 Performance Guidelines

### Web Performance:
- Use Next.js Image optimization
- Implement virtual scrolling for long lists
- Code split with dynamic imports
- Prefetch data on hover

### Mobile Performance:
- Use FlashList for large lists
- Implement lazy loading
- Optimize images with expo-image
- Use React.memo for expensive components

## 🔄 State Management

### Shared State Pattern:
```typescript
// packages/shared/hooks/useProperties.ts
export function useProperties() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Same hook for both platforms
  return { properties, loading };
}
```

## 🧪 Testing Strategy

### Unit Tests (Shared):
- Test validation schemas
- Test API functions
- Test business logic

### Component Tests:
- Web: React Testing Library
- Mobile: React Native Testing Library
- Both use same test patterns

## 📝 File Naming Conventions

```
Web Components:
web/src/components/[feature]/[Component].tsx

Mobile Screens:
mobile/src/screens/[Feature]Screen.tsx

Mobile Components:
mobile/src/components/[Component].tsx

Shared Logic:
packages/shared/src/[type]/[feature].ts
```

## 🚨 Common Pitfalls to Avoid

1. **Don't try to share UI components** - It adds 40% complexity
2. **Don't diverge business logic** - Keep it in shared/
3. **Don't skip mobile when building web** - Build both together
4. **Don't use web-only libraries in shared/** - Check platform compatibility
5. **Don't ignore platform conventions** - iOS/Android have different UX

## ✅ Success Metrics

- **Feature Parity**: 100% features on both platforms
- **Code Sharing**: 10-15% shared logic
- **Development Speed**: 1.15x vs web-only
- **Maintenance**: Easy with clear separation
- **User Experience**: Native feel on each platform

---

**Remember**: Build once for logic, twice for UI. This is the fastest path to shipping both platforms with high quality.