# Frontend Component Guide

Complete reference for all React components and their usage.

## 🎨 Common Components

### Navbar
Location: `src/components/common/Navbar.jsx`

Navigation bar with links to all pages.

**Usage:**
```jsx
import Navbar from './components/common/Navbar'

// Used in App.jsx - automatically included in main layout
```

**Props:** None

**Features:**
- Sticky positioning
- Logo with icon
- Navigation links (Home, Localize, History, Analytics)
- Responsive mobile menu

---

### LoadingSpinner
Location: `src/components/common/LoadingSpinner.jsx`

Animated loading indicator.

**Usage:**
```jsx
import LoadingSpinner from './components/common/LoadingSpinner'

<LoadingSpinner size="md" />
```

**Props:**
- `size` ('sm' | 'md' | 'lg') - Default: 'md'

**Examples:**
```jsx
<LoadingSpinner size="sm" />  {/* Small spinner */}
<LoadingSpinner size="lg" />  {/* Large spinner */}
```

---

### Alert
Location: `src/components/common/Alert.jsx`

Notification/alert component with multiple variants.

**Usage:**
```jsx
import Alert from './components/common/Alert'

<Alert 
  type="success" 
  title="Success!" 
  message="Operation completed"
  onClose={() => setShowAlert(false)}
/>
```

**Props:**
- `type` ('info' | 'success' | 'error' | 'warning') - Default: 'info'
- `title` (string) - Alert title
- `message` (string) - Alert message
- `onClose` (function) - Callback when closed

**Types:**
```jsx
<Alert type="info" message="Information" />
<Alert type="success" message="Success!" />
<Alert type="error" message="Error occurred" />
<Alert type="warning" message="Be careful!" />
```

---

### Card
Location: `src/components/common/Card.jsx`

Reusable card container component.

**Usage:**
```jsx
import Card from './components/common/Card'

<Card>
  <h2>Card Title</h2>
  <p>Card content goes here</p>
</Card>
```

**Props:**
- `children` (ReactNode) - Card content
- `className` (string) - Additional CSS classes

**Examples:**
```jsx
<Card className="border-blue-200">
  Content with custom styles
</Card>
```

---

### Badge
Location: `src/components/common/Badge.jsx`

Inline label/badge component.

**Usage:**
```jsx
import Badge from './components/common/Badge'

<Badge variant="blue">Spanish</Badge>
<Badge variant="green">99% quality</Badge>
```

**Props:**
- `variant` ('default' | 'blue' | 'green' | 'purple' | 'amber') - Default: 'default'
- `children` (ReactNode) - Badge text
- `className` (string) - Additional styles

**Variants:**
```jsx
<Badge variant="default">Neutral</Badge>
<Badge variant="blue">Primary</Badge>
<Badge variant="green">Success</Badge>
<Badge variant="purple">Special</Badge>
<Badge variant="amber">Warning</Badge>
```

---

## 🌍 Localization Components

### TextInputBox
Location: `src/components/localization/TextInputBox.jsx`

Textarea input with character counter and word count.

**Usage:**
```jsx
import TextInputBox from './components/localization/TextInputBox'

<TextInputBox
  value={text}
  onChange={setText}
  placeholder="Enter text..."
  maxLength={5000}
  rows={6}
/>
```

**Props:**
- `value` (string) - Input text value
- `onChange` (function) - Called on text change
- `placeholder` (string) - Placeholder text
- `maxLength` (number) - Max characters - Default: 5000
- `rows` (number) - Textarea rows - Default: 6

**Features:**
- Character counter
- Line counter
- Word counter
- Visual feedback near limit (90%+)

---

### LanguageSelector
Location: `src/components/localization/LanguageSelector.jsx`

Dropdown for selecting target language.

**Usage:**
```jsx
import LanguageSelector from './components/localization/LanguageSelector'

<LanguageSelector
  value={language}
  onChange={setLanguage}
  label="Target Language"
/>
```

**Props:**
- `value` (string) - Selected language code (e.g., 'es', 'fr')
- `onChange` (function) - Called when language changes
- `label` (string) - Label text - Default: 'Target Language'

**Supported Languages:**
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Japanese (ja)
- Chinese (zh)
- Hindi (hi)
- Arabic (ar)
- Russian (ru)
- Korean (ko)

---

### ToneSelector
Location: `src/components/localization/ToneSelector.jsx`

Dropdown for selecting tone/style.

**Usage:**
```jsx
import ToneSelector from './components/localization/ToneSelector'

<ToneSelector
  value={tone}
  onChange={setTone}
  label="Tone"
/>
```

**Props:**
- `value` (string) - Selected tone
- `onChange` (function) - Called on tone change
- `label` (string) - Label text - Default: 'Tone'

**Available Tones:**
- `formal` - Professional and structured
- `casual` - Friendly and relaxed
- `marketing` - Persuasive and engaging
- `technical` - Precise and accurate
- `neutral` - Objective and balanced

---

### LocalizeButton
Location: `src/components/localization/LocalizeButton.jsx`

Main action button for localization.

**Usage:**
```jsx
import LocalizeButton from './components/localization/LocalizeButton'

<LocalizeButton
  onClick={handleLocalize}
  loading={isLoading}
  disabled={!text}
  fullWidth={true}
/>
```

**Props:**
- `onClick` (function) - Click handler
- `loading` (boolean) - Show loading state - Default: false
- `disabled` (boolean) - Disable button - Default: false
- `fullWidth` (boolean) - Full width button - Default: true

**States:**
```jsx
<LocalizeButton onClick={fn} />           {/* Normal */}
<LocalizeButton onClick={fn} loading />   {/* Loading */}
<LocalizeButton onClick={fn} disabled />  {/* Disabled */}
```

---

### OutputDisplayPanel
Location: `src/components/localization/OutputDisplayPanel.jsx`

Display localized text with metadata.

**Usage:**
```jsx
import OutputDisplayPanel from './components/localization/OutputDisplayPanel'

<OutputDisplayPanel result={localizationResult} />
```

**Props:**
- `result` (object) - Localization result from API
- `onCopy` (boolean) - Show copy button - Default: true

**Result Object Structure:**
```javascript
{
  localized_text: "string",
  tone_applied: "string",
  sentiment_preserved: "string",
  quality_score: number (0-100),
  detected_language: "string",
  cultural_adaptations: ["list", "of", "adaptations"]
}
```

**Features:**
- Copy to clipboard button
- Quality score badge
- Tone and sentiment badges
- Cultural adaptations list
- Detected language display

---

### ExplanationPanel
Location: `src/components/localization/ExplanationPanel.jsx`

Display localization explanation.

**Usage:**
```jsx
import ExplanationPanel from './components/localization/ExplanationPanel'

<ExplanationPanel explanation={result.explanation} />
```

**Props:**
- `explanation` (string) - Explanation text

**Returns:** `null` if no explanation

---

### RatingSystem
Location: `src/components/localization/RatingSystem.jsx`

1-5 star rating with optional comment.

**Usage:**
```jsx
import RatingSystem from './components/localization/RatingSystem'

<RatingSystem
  requestId={result.request_id}
  onSubmit={() => console.log('Submitted!')}
/>
```

**Props:**
- `requestId` (string) - ID of localization request
- `onSubmit` (function) - Called after successful submission

**Features:**
- 1-5 star rating
- Hover preview
- Optional comment (max 500 chars)
- Loading state
- Success/error feedback

**Validation:**
- Rating is required (1-5)
- Comment max 500 characters
- Request ID is sent to backend

---

## 📄 Page Components

### HomePage
Location: `src/pages/HomePage.jsx`

Landing page with features and call-to-action.

**Route:** `/`

**Sections:**
- Hero section
- Features grid (6 items)
- How it works example
- CTA buttons

---

### LocalizationDashboard
Location: `src/pages/LocalizationDashboard.jsx`

Main localization interface.

**Route:** `/dashboard`

**Layout (3-column grid):**
1. **Input Column:**
   - Text input box
   - Language selector
   - Tone selector
   - Localize button

2. **Output Column (2x width):**
   - Output display panel
   - Explanation panel
   - Rating system

**State Management:**
```javascript
{
  text: "",
  target_language: "es",
  tone: "neutral",
  result: null,
  loading: false,
  error: null
}
```

---

### HistoryPage
Location: `src/pages/HistoryPage.jsx`

View past localizations with pagination.

**Route:** `/history`

**Features:**
- Paginated list (10 items/page)
- Filter by language
- Copy buttons
- Metadata display
- Refresh button

**Display Info per Item:**
- Badges (language, tone, sentiment, quality)
- Original text
- Localized text
- Explanation
- Timestamp

---

### AnalyticsDashboard
Location: `src/pages/AnalyticsDashboard.jsx`

Localization analytics and statistics.

**Route:** `/analytics`

**Metrics:**
1. Total Localizations
2. Average Quality Score %
3. Number of Languages Used
4. Average User Rating

**Charts:**
- Top Languages (bar chart)
- Tone Distribution (bar chart)

**Data Source:** Fetched from `/history` endpoint

---

## 🔌 API Service

Location: `src/services/api.js`

### Functions

#### checkHealth()
```javascript
await checkHealth()  // Returns boolean
```

#### localize(payload)
```javascript
await localize({
  text: "Hello world",
  target_language: "es",
  tone: "casual"
})
// Returns: { localized_text, explanation, quality_score, ... }
```

#### getHistory(options)
```javascript
await getHistory({
  page: 1,
  limit: 10,
  target_language: "es"  // optional
})
// Returns: { items, total, page, page_size }
```

#### submitFeedback(payload)
```javascript
await submitFeedback({
  request_id: "uuid",
  rating: 5,
  comment: "Great!"
})
// Returns: { success: true }
```

#### batchLocalize(texts)
```javascript
await batchLocalize([
  { text: "Hello", target_language: "es" },
  { text: "Goodbye", target_language: "fr" }
])
// Returns: [result1, result2]
```

---

## 🛠️ Creating New Components

### Template

```jsx
// src/components/category/MyComponent.jsx

export default function MyComponent({ prop1, prop2 = 'default' }) {
  return (
    <div className="...">
      {/* Component content */}
    </div>
  )
}
```

### Best Practices

1. **Naming:** PascalCase for components
2. **Props:** Define with JSDoc comments
3. **Styling:** Use TailwindCSS classes
4. **State:** Use `useState` for local state
5. **Side Effects:** Use `useEffect` carefully
6. **Exports:** Use `export default`
7. **Documentation:** Add usage examples

### Example

```jsx
/**
 * MyButton - Custom button component
 * 
 * @param {Object} props
 * @param {string} props.label - Button text
 * @param {function} props.onClick - Click handler
 * @param {boolean} [props.disabled] - Disabled state
 * 
 * @example
 * <MyButton label="Click me" onClick={() => alert('clicked')} />
 */
export default function MyButton({ label, onClick, disabled = false }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
    >
      {label}
    </button>
  )
}
```

---

## 📚 Styling Guide

### Responsive Breakpoints

```jsx
<div className="
  block           {/* base */}
  sm:block         {/* >640px */}
  md:block         {/* >768px */}
  lg:block         {/* >1024px */}
  xl:block         {/* >1280px */}
  2xl:block        {/* >1536px */}
">
```

### Common Patterns

```jsx
{/* Spacing */}
<div className="p-4 mb-6">Content</div>

{/* Colors */}
<div className="bg-blue-600 text-white">Content</div>

{/* Flexbox */}
<div className="flex items-center justify-between gap-4">
  <div>Left</div>
  <div>Right</div>
</div>

{/* Grid */}
<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
  {items.map(item => <div key={item.id}>{item}</div>)}
</div>

{/* Shadows & Borders */}
<div className="rounded-lg border border-slate-200 shadow-sm">
  Content
</div>

{/* Hover & Transitions */}
<button className="hover:bg-blue-700 transition-colors">
  Button
</button>
```

---

## 🎯 Component Tree

```
App
├── Navbar
└── Routes
    ├── HomePage
    │   └── (static content)
    ├── LocalizationDashboard
    │   ├── Card
    │   │   ├── TextInputBox
    │   │   ├── LanguageSelector
    │   │   └── ToneSelector
    │   ├── LocalizeButton
    │   ├── Alert (error)
    │   └── Output Section
    │       ├── Card
    │       │   └── OutputDisplayPanel
    │       ├── Card
    │       │   └── ExplanationPanel
    │       └── Card
    │           └── RatingSystem
    ├── HistoryPage
    │   ├── Card (filters)
    │   ├── LoadingSpinner
    │   ├── Alert (error)
    │   └── Card (history items)
    │       ├── Badge (metadata)
    │       ├── Card (text display)
    │       └── Card (explanation)
    └── AnalyticsDashboard
        ├── Card (metrics)
        ├── LoadingSpinner
        ├── Card (charts)
        └── Badge (stats)
```

---

**Last Updated:** March 2026
