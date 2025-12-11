# Terminal Slideshow

A lightweight terminal-based presentation tool using ASCII art slides. Perfect for developer presentations, tech talks, and keeping your audience focused on content.

## Intended Workflow

This tool is designed to be used with AI assistants (Claude, ChatGPT, etc.) to generate slides. The ASCII art format with strict 72-character line widths is tedious for humans to create manually, but AI can generate properly formatted slides quickly from a topic outline.

**Typical workflow:**
1. Describe your presentation topic and structure to an AI
2. AI generates the markdown slide files following the format rules
3. Review and iterate with the AI as needed
4. Present using this tool

The slide templates and format rules in this README serve as a reference for AI to follow when generating your slides.

## Features

- **Pure terminal** - No GUI, no browser, just your terminal
- **ASCII art slides** - Clean, readable box-drawing characters
- **Keyboard navigation** - Intuitive vim-style controls
- **Speaker notes** - Hidden notes for each slide
- **Scroll support** - Handle tall slides gracefully
- **Zero dependencies** - Pure Python 3, no pip install needed

## Quick Start

```bash
# Clone the repo
git clone https://github.com/yourusername/terminal-slideshow.git
cd terminal-slideshow

# Run the demo
python3 slideshow.py
```

## Controls

| Key | Action |
|-----|--------|
| `n`, `SPACE`, `→` | Next slide |
| `p`, `←` | Previous slide |
| `j`, `↓` | Scroll down (tall slides) |
| `k`, `↑` | Scroll up |
| `g` | Go to slide number |
| `f` | First slide |
| `l` | Last slide |
| `s` | Show speaker notes |
| `i` | Show slide index |
| `h`, `?` | Help |
| `r` | Refresh screen |
| `q` | Quit |

## Creating Slides

Slides are markdown files in the `slides/` directory, loaded in alphabetical order.

### File Format

```markdown
# SLIDE N: Title Here

\`\`\`
┌──────────────────────────────────────────────────────────────────────┐
│                         YOUR CONTENT HERE                            │
└──────────────────────────────────────────────────────────────────────┘
\`\`\`

## Speaker Notes

Notes for the presenter (press 's' to view).
```

### Key Rules

1. **Every line must be exactly 72 characters** - This ensures borders align
2. **No emojis** - Use ASCII alternatives (`*`, `[x]`, `-->`)
3. **Use the templates** - Sample slides show each form factor

### Slide Templates Included

| File | Purpose |
|------|---------|
| `01-title.md` | Title slide with presenter info |
| `02-agenda.md` | Numbered agenda/outline |
| `03-content.md` | Standard content with sections |
| `04-two-column.md` | Side-by-side comparison |
| `05-diagram.md` | Flow diagrams with arrows |
| `06-list.md` | Bullet point lists |
| `07-emphasis.md` | Double-border for emphasis |
| `08-closing.md` | Thank you / Q&A slide |

## Validation

Check that all slides have correct 72-character line widths:

```bash
python3 -c "
import glob
for f in sorted(glob.glob('slides/*.md')):
    in_code = False
    for i, line in enumerate(open(f), 1):
        line = line.rstrip('\n')
        if line.strip().startswith('\`\`\`'):
            in_code = not in_code
        elif in_code and line and len(line) != 72:
            print(f'{f}:{i}: {len(line)} chars')
"
```

## Box Drawing Reference

```
Single-line (standard):
┌───┬───┐
│   │   │
├───┼───┤
│   │   │
└───┴───┘

Double-line (emphasis):
╔═══╦═══╗
║   ║   ║
╠═══╬═══╣
║   ║   ║
╚═══╩═══╝
```

## Why Terminal Slides?

- **No context switching** - Stay in your terminal
- **Version control friendly** - Plain text diffs nicely
- **Distraction free** - No animations, no transitions, just content
- **Works anywhere** - SSH into a server and present
- **Hacker aesthetic** - Because ASCII art is cool

## License

MIT License - See [LICENSE](LICENSE) for details.
