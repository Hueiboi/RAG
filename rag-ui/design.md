# RAG Chatbot — Design System

## Visual Direction

Dark tech aesthetic — không phải "hacker terminal" hay "neon cyberpunk", mà là **professional dev tool**: tối, tập trung, thông tin nổi bật. Gần với tone của Linear, Vercel Dashboard, hay Raycast.

---

## Color Palette

```
--bg-base:        #0A0A0F   /* nền chính — gần black, hơi tím lạnh */
--bg-surface:     #111118   /* card, panel, sidebar */
--bg-elevated:    #1A1A24   /* hover state, input background */
--bg-border:      #2A2A38   /* border, divider */

--accent-primary: #6366F1   /* indigo — màu chủ đạo, CTA, active state */
--accent-glow:    #6366F140 /* indigo với opacity — glow effect */

--text-primary:   #F0F0FF   /* text chính — trắng hơi lạnh */
--text-secondary: #8888AA   /* text phụ, placeholder, metadata */
--text-muted:     #44445A   /* disabled, timestamp */

--status-success: #22C55E   /* upload thành công */
--status-error:   #EF4444   /* lỗi */
--status-loading: #6366F1   /* đang xử lý */
```

---

## Typography

```
Display/Heading:  Inter (700) — clean, tech, không serif
Body/Chat:        Inter (400) — dễ đọc ở size nhỏ
Code/Monospace:   JetBrains Mono — cho code block trong chat response
```

Scale:
```
--text-xs:   11px  /* timestamp, metadata */
--text-sm:   13px  /* secondary info */
--text-base: 15px  /* chat message body */
--text-lg:   17px  /* heading nhỏ */
--text-xl:   22px  /* page title */
```

---

## Layout

```
┌─────────────────────────────────────────────┐
│  Header: Logo + UserBadge + SignOut          │
├──────────┬──────────────────────────────────┤
│          │                                  │
│ Sidebar  │  Chat Area                       │
│          │                                  │
│ Upload   │  [Bot bubble]                    │
│ file     │            [User bubble]         │
│          │                                  │
│ Doc list │                                  │
│          │                                  │
├──────────┴──────────────────────────────────┤
│  [📎] [Input message...]         [Send →]   │
└─────────────────────────────────────────────┘
```

---

## Component Specs

### Chat Bubbles
```
User message:
  background: --accent-primary
  color: white
  border-radius: 18px 18px 4px 18px
  align: right
  max-width: 70%

Bot message:
  background: --bg-surface
  border: 1px solid --bg-border
  border-radius: 18px 18px 18px 4px
  align: left
  max-width: 80%
  font: JetBrains Mono cho code block bên trong
```

### Input Area
```
background: --bg-elevated
border: 1px solid --bg-border
border-radius: 12px
focus: border-color --accent-primary, box-shadow 0 0 0 2px --accent-glow
padding: 12px 16px
```

### Upload Button
```
icon: paperclip
style: ghost button, text-secondary
hover: text-primary, background --bg-elevated
khi có file: hiển thị filename badge với màu accent-primary
```

### UserBadge (Header)
```
avatar: initials từ email (H cho hieub1508@...)
background: --accent-primary
size: 32px, border-radius: 50%
email: text-secondary, text-sm
```

### Sign Out Button
```
style: ghost, text-secondary
hover: text-error (#EF4444)
icon: LogOut từ lucide-react
```

---

## Signature Element

**Glow effect trên bot message đầu tiên** — khi bot trả lời, bubble xuất hiện với subtle indigo glow fade in:

```css
box-shadow: 0 0 20px var(--accent-glow);
animation: glowFade 1.5s ease-out forwards;

@keyframes glowFade {
  0%   { box-shadow: 0 0 20px var(--accent-glow); }
  100% { box-shadow: none; }
}
```

Nhẹ, không gây distraction, nhưng làm cho response của AI cảm giác "alive".

---

## Spacing System

```
--space-1: 4px
--space-2: 8px
--space-3: 12px
--space-4: 16px
--space-6: 24px
--space-8: 32px
```

