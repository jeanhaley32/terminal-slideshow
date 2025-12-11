# Slide Development Guidelines

Instructions for creating ASCII slides compatible with the terminal slideshow presenter.

## Terminal Constraints

| Constraint | Value | Notes |
|------------|-------|-------|
| **Target Width** | 72 columns | Safe for 80-column terminals with centering margin |
| **Maximum Width** | 76 columns | Absolute limit; wider content will be truncated |
| **Recommended Height** | 20-24 lines | Fits standard 24-line terminals |
| **Maximum Height** | 40 lines | Taller content shows overflow indicator |

## File Format

```markdown
# SLIDE N: Title Here

```
[ASCII art content goes here]
```

## Speaker Notes

Optional notes for the presenter. Not displayed on slide.
```

- File naming: `NN-slug-name.md` (e.g., `01-title.md`, `A1-appendix.md`)
- Files are loaded in alphabetical order
- Use prefix `A1-`, `A2-` for appendix slides

## Box Drawing Characters

### Recommended Box Characters

```
Single-line boxes (preferred):
┌───────────────────────────────────────────────────────────────────────┐
│  Content here                                                         │
├───────────────────────────────────────────────────────────────────────┤
│  More content                                                         │
└───────────────────────────────────────────────────────────────────────┘

Double-line boxes (for emphasis):
╔═══════════════════════════════════════════════════════════════════════╗
║  Important content                                                    ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Character Reference

| Purpose | Single | Double |
|---------|--------|--------|
| Top-left | `┌` | `╔` |
| Top-right | `┐` | `╗` |
| Bottom-left | `└` | `╚` |
| Bottom-right | `┘` | `╝` |
| Horizontal | `─` | `═` |
| Vertical | `│` | `║` |
| T-junction (down) | `┬` | `╦` |
| T-junction (up) | `┴` | `╩` |
| T-junction (right) | `├` | `╠` |
| T-junction (left) | `┤` | `╣` |
| Cross | `┼` | `╬` |

## Width Templates

### Standard 72-Column Box

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  [68 characters of content space]                                    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

- Total width: 72 characters
- Inner content: 68 characters (72 - 2 borders - 2 padding spaces)

### Ruler for Measuring (72 columns)

```
|----+----|----+----|----+----|----+----|----+----|----+----|----+----|--
0        10        20        30        40        50        60        70 72
```

## Content Patterns

### Title Slide

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                                                                      │
│                         PRESENTATION TITLE                           │
│                                                                      │
│                           Subtitle Here                              │
│                                                                      │
│                                                                      │
│                            Author Name                               │
│                              Date                                    │
│                                                                      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Section Header

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                          SECTION TITLE                               │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Bullet List

```
┌──────────────────────────────────────────────────────────────────────┐
│                          TOPIC TITLE                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  • First point goes here                                             │
│  • Second point with more detail                                     │
│  • Third point                                                       │
│    - Sub-point if needed                                             │
│    - Another sub-point                                               │
│  • Fourth point                                                      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Two-Column Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│                            COMPARISON                                │
├─────────────────────────────────┬────────────────────────────────────┤
│          LEFT SIDE              │           RIGHT SIDE               │
├─────────────────────────────────┼────────────────────────────────────┤
│  • Point A                      │  • Point X                         │
│  • Point B                      │  • Point Y                         │
│  • Point C                      │  • Point Z                         │
└─────────────────────────────────┴────────────────────────────────────┘
```

### Progress/Score Bar

```
│  Label Here      ███████░░░  7/10   ← Optional annotation            │
│  Another Item    ████░░░░░░  4/10                                    │
│  Third Item      █░░░░░░░░░  1/10   ← Warning note                   │
```

Bar characters:
- Filled: `█` (full block)
- Empty: `░` (light shade)
- Alternative empty: `▒` (medium shade)

### Flow Diagram

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Step 1    │ ───▶ │   Step 2    │ ───▶ │   Step 3    │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   Step 4    │
                     └─────────────┘
```

Arrow characters: `→` `←` `↑` `↓` `▶` `◀` `▲` `▼` `───▶`

### Status Indicators

```
│  ✓ Completed task                                                    │
│  ✗ Failed task                                                       │
│  ⚠ Warning item                                                      │
│  • Neutral item                                                      │
│  ★ Important item                                                    │
```

## Spacing Rules

1. **Outer padding**: Always 2 spaces inside box borders
2. **Section spacing**: 1 blank line between sections inside box
3. **List items**: Align bullet points, use 2-space indent for sub-items
4. **Centering**: Center titles, left-align body content

## Critical: Line Width Consistency

**Every line inside the code block MUST be exactly 72 characters.**

This is the most common source of misaligned right borders. Even if content varies, pad each line with spaces so the right border `│` or `║` always appears at column 72.

### Why This Matters

The slideshow centers content based on the widest line. If lines have inconsistent widths, the right border will appear jagged:

```
BAD (inconsistent widths):
┌──────────────────────────────────────────────────────────────────────┐
│  Short line                                                         │
│  A much longer line that pushes the border out                       │
│  Another short one                                                  │
└──────────────────────────────────────────────────────────────────────┘

GOOD (all lines exactly 72 chars):
┌──────────────────────────────────────────────────────────────────────┐
│  Short line                                                          │
│  A much longer line with padding after                               │
│  Another short one                                                   │
└──────────────────────────────────────────────────────────────────────┘
```

## Avoid Emojis and Variable-Width Unicode

**Do NOT use emojis** (🎯, 🔍, ✅, etc.) in slides. Emojis have inconsistent display widths across terminals and fonts, causing border misalignment even when character count is correct.

### Safe Alternatives

| Instead of | Use |
|------------|-----|
| 🎯 ✅ ❌ | `*` or `[ ]` `[x]` |
| ▶ ▲ ▼ ◀ | `>` `^` `v` `<` or `-->` |
| ├ └ │ (tree) | `\|--` `+--` `\|` |
| • | `*` or `-` |
| ✓ ✗ | `+` `x` or `[x]` `[ ]` |

The box-drawing characters (`┌ ─ ┐ │ └ ┘ ├ ┤`) are safe—they render as single-width in terminals.

## Common Mistakes to Avoid

| Mistake | Problem | Fix |
|---------|---------|-----|
| Lines with different lengths | Misaligned right border | Pad ALL lines to exactly 72 chars |
| Using emojis | Unpredictable width | Use ASCII alternatives |
| Lines > 76 chars | Content truncated with `…` | Keep at exactly 72 chars |
| Inconsistent box width | Misaligned borders | Use templates |
| Tab characters | Unpredictable spacing | Use spaces only |
| Trailing whitespace | Box alignment issues | Trim line endings |
| Mixed box styles | Visual inconsistency | Pick single or double, be consistent |

## Validation Checklist

Before adding a slide, verify:

- [ ] **Every line is exactly 72 characters** (most important!)
- [ ] No emojis or variable-width Unicode characters
- [ ] Box borders align vertically
- [ ] Content fits within 24 lines (or expect truncation)
- [ ] No tab characters used
- [ ] File follows naming convention `NN-name.md`
- [ ] Code block markers (```) wrap ASCII content
- [ ] Speaker notes section is present (even if empty)

## Quick Width Check

Run this Python script to verify all lines are exactly 72 characters:

```bash
python3 -c "
import glob

for filepath in sorted(glob.glob('slides/*.md')):
    in_code = False
    issues = []
    with open(filepath, 'r') as f:
        for i, line in enumerate(f, 1):
            line = line.rstrip('\n')
            if line.strip().startswith('\`\`\`'):
                in_code = not in_code
                continue
            if in_code and line and len(line) != 72:
                issues.append(f'  Line {i}: {len(line)} chars')
    if issues:
        print(f'{filepath}:')
        for issue in issues[:5]:
            print(issue)
        if len(issues) > 5:
            print(f'  ... and {len(issues)-5} more')
"
```

For a quick check of a single file:

```bash
awk '{ if (length != 72) print NR": "length" chars" }' slides/NN-name.md
```
