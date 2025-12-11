#!/usr/bin/env python3
"""
Terminal Slideshow Presenter
Navigate through markdown slides in fullscreen terminal mode.

Controls:
    NAVIGATION
    n, SPACE, RIGHT, ENTER        - Next slide
    p, LEFT, BACKSPACE            - Previous slide
    f                             - First slide
    l                             - Last slide
    g                             - Go to slide (enter number)

    SCROLLING (for tall slides)
    j, DOWN                       - Scroll down
    k, UP                         - Scroll up

    SPEAKER NOTES
    s                             - Toggle notes panel
    +, =                          - Expand notes panel
    -, _                          - Shrink notes panel

    VIEW OPTIONS
    i                             - Show slide index
    h, ?                          - Show help
    r                             - Refresh screen

    q, x, ESC                     - Quit
"""

import os
import sys
import re
import glob
import tty
import termios
import unicodedata


def get_display_width(text):
    """Calculate the display width of a string, accounting for wide Unicode characters."""
    width = 0
    for char in text:
        # East Asian Width categories: F (Fullwidth), W (Wide) take 2 columns
        # All others take 1 column
        ea_width = unicodedata.east_asian_width(char)
        if ea_width in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width


def truncate_to_width(text, max_width, add_indicator=False):
    """Truncate text to fit within max_width display columns.

    If add_indicator is True and truncation occurs, adds '…' at the end.
    """
    current_width = 0
    result = ''
    truncated = False

    # If adding indicator, reserve 1 column for it
    effective_max = max_width - 1 if add_indicator else max_width

    for char in text:
        char_width = 2 if unicodedata.east_asian_width(char) in ('F', 'W') else 1
        if current_width + char_width > effective_max:
            truncated = True
            break
        result += char
        current_width += char_width

    if truncated and add_indicator:
        result += '…'

    return result


class Slideshow:
    def __init__(self, slides_dir):
        self.slides_dir = slides_dir
        self.slides = self._load_slides()
        self.current_index = 0
        self.scroll_offset = 0  # For scrolling tall slides
        self.show_notes = False  # Toggle for persistent notes panel
        self.notes_height = 6   # Height of notes panel (excluding border)

    def _load_slides(self):
        """Load all slide files in order."""
        pattern = os.path.join(self.slides_dir, '*.md')
        files = sorted(glob.glob(pattern))

        slides = []
        for filepath in files:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse slide content and speaker notes
            parts = content.split('## Speaker Notes')
            slide_content = parts[0].strip()
            speaker_notes = parts[1].strip() if len(parts) > 1 else ''

            # Extract title from first line
            lines = slide_content.split('\n')
            title = lines[0].replace('# ', '') if lines else 'Untitled'

            slides.append({
                'filepath': filepath,
                'filename': os.path.basename(filepath),
                'title': title,
                'content': slide_content,
                'notes': speaker_notes
            })

        return slides

    def _get_terminal_size(self):
        """Get terminal dimensions."""
        try:
            size = os.get_terminal_size()
            return size.columns, size.lines
        except OSError:
            return 80, 24

    def _clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name != 'nt' else 'cls')

    def _fit_line_to_width(self, line, width):
        """Ensure a line fits exactly within the terminal width.

        Returns a string that is exactly `width` display columns:
        - Truncates if too long
        - Pads with spaces if too short
        """
        display_width = get_display_width(line)

        if display_width > width:
            # Truncate to fit
            return truncate_to_width(line, width)
        elif display_width < width:
            # Pad with spaces to fill the line
            return line + ' ' * (width - display_width)
        else:
            return line

    def _prepare_slide_content(self, text, width):
        """Prepare slide content: center horizontally and fit to width.

        Returns a list of lines, each exactly `width` display columns.
        """
        lines = text.split('\n')
        result = []

        # Find the maximum display width of content
        max_content_width = 0
        for line in lines:
            dw = get_display_width(line)
            if dw > max_content_width:
                max_content_width = dw

        # Calculate left padding for centering
        # If content wider than or equal to terminal, no padding
        if max_content_width >= width:
            left_padding = 0
        else:
            left_padding = (width - max_content_width) // 2

        for line in lines:
            line_width = get_display_width(line)

            # If this line + padding would exceed terminal width, truncate the line first
            if left_padding + line_width > width:
                # Truncate the line content to fit (with indicator showing truncation)
                line = truncate_to_width(line, width - left_padding, add_indicator=True)
                line_width = get_display_width(line)

            # Add left padding for centering
            padded_line = ' ' * left_padding + line

            # Pad right side to fill terminal width exactly
            padded_width = get_display_width(padded_line)
            if padded_width < width:
                padded_line = padded_line + ' ' * (width - padded_width)

            result.append(padded_line)

        return result

    def _extract_ascii_art(self, content):
        """Extract the ASCII art diagram from slide content."""
        lines = content.split('\n')
        art_lines = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                art_lines.append(line)

        return '\n'.join(art_lines) if art_lines else content

    def _wrap_text(self, text, width):
        """Wrap text to fit within specified width."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_len = len(word)
            if current_length + word_len + (1 if current_line else 0) <= width:
                current_line.append(word)
                current_length += word_len + (1 if len(current_line) > 1 else 0)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_len

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else ['']

    def _render_notes_panel(self, width, panel_height):
        """Render the speaker notes panel at the bottom of the screen."""
        slide = self.slides[self.current_index]
        notes_text = slide['notes'].strip() if slide['notes'] else '(No speaker notes)'

        # Box drawing
        top_border = '┌' + '─' * (width - 2) + '┐'
        bottom_border = '└' + '─' * (width - 2) + '┘'
        title_line = '│ SPEAKER NOTES' + ' ' * (width - 17) + '│'
        separator = '├' + '─' * (width - 2) + '┤'

        # Wrap notes text to fit inside the box (width - 4 for borders and padding)
        inner_width = width - 4
        wrapped_lines = []
        for paragraph in notes_text.split('\n'):
            if paragraph.strip():
                wrapped_lines.extend(self._wrap_text(paragraph.strip(), inner_width))
            else:
                wrapped_lines.append('')

        # Build notes content lines
        content_lines = []
        available_content_lines = panel_height - 4  # Subtract borders and title

        for i in range(available_content_lines):
            if i < len(wrapped_lines):
                line_content = wrapped_lines[i]
                padding = inner_width - len(line_content)
                content_lines.append('│ ' + line_content + ' ' * padding + ' │')
            else:
                content_lines.append('│' + ' ' * (width - 2) + '│')

        # Print the panel with dim styling
        print('\033[2m', end='')  # Dim text
        print(top_border)
        print('\033[1;2m', end='')  # Bold + dim for title
        print(title_line)
        print('\033[2m', end='')  # Back to just dim
        print(separator)
        for line in content_lines:
            print(line)
        print(bottom_border, end='')
        print('\033[0m', end='')  # Reset

    def _render_slide(self):
        """Render the current slide to terminal with scroll support."""
        self._clear_screen()
        width, height = self._get_terminal_size()

        slide = self.slides[self.current_index]

        # Extract ASCII art content
        content = self._extract_ascii_art(slide['content'])

        # Prepare content: center and fit each line to terminal width
        content_lines = self._prepare_slide_content(content, width)
        total_content_height = len(content_lines)

        # Calculate available height based on notes panel visibility
        # Reserve: 1 line for status bar, optionally notes_height + 4 for notes panel
        notes_panel_height = self.notes_height + 4 if self.show_notes else 0
        available_height = height - 1 - notes_panel_height

        # Check if content needs scrolling
        needs_scroll = total_content_height > available_height

        # Clamp scroll offset to valid range
        if needs_scroll:
            max_scroll = total_content_height - available_height
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
        else:
            self.scroll_offset = 0

        # Determine which lines to display
        if needs_scroll:
            # Show scrolled portion of content
            start_line = self.scroll_offset
            end_line = start_line + available_height
            visible_lines = content_lines[start_line:end_line]
            top_padding = 0
        else:
            # Center content vertically
            visible_lines = content_lines
            top_padding = max(0, (available_height - total_content_height) // 2)

        # Build the full screen buffer
        screen_lines = []

        # Add top padding (empty lines fitted to width)
        for _ in range(top_padding):
            screen_lines.append(' ' * width)

        # Add visible content
        screen_lines.extend(visible_lines)

        # Add bottom padding to fill remaining space
        bottom_padding = available_height - len(screen_lines)
        for _ in range(bottom_padding):
            screen_lines.append(' ' * width)

        # Print all content lines
        for line in screen_lines:
            print(line)

        # Render notes panel if enabled
        if self.show_notes:
            self._render_notes_panel(width, notes_panel_height)
            print()  # Newline before status bar

        # Print status bar
        self._render_status_bar(width, needs_scroll, total_content_height, available_height)

    def _render_status_bar(self, width, needs_scroll=False, total_lines=0, visible_lines=0):
        """Render the bottom status bar."""
        slide = self.slides[self.current_index]

        # Status info
        position = f"[{self.current_index + 1}/{len(self.slides)}]"

        # Scroll indicator if content is scrollable
        if needs_scroll:
            scroll_pos = self.scroll_offset + 1
            scroll_max = total_lines - visible_lines + 1
            scroll_indicator = f" ↕{scroll_pos}/{scroll_max}"
        else:
            scroll_indicator = ""

        # Notes indicator
        notes_indicator = " [notes ON]" if self.show_notes else ""

        # Help hints - show scroll keys if scrollable
        if needs_scroll:
            help_hint = "[j/k]scroll [s]notes [n]ext [p]rev [q]uit"
        else:
            help_hint = "[s]notes [n]ext [p]rev [h]elp [q]uit"

        # Build status bar
        status = f" {position}{scroll_indicator}{notes_indicator}  {slide['title']}"

        # Calculate padding, ensuring we don't exceed terminal width
        min_spacing = 2
        available_for_padding = width - len(status) - len(help_hint) - min_spacing

        if available_for_padding < 1:
            # Terminal too narrow - truncate title
            max_title_len = width - len(position) - len(scroll_indicator) - len(help_hint) - 8
            if max_title_len > 3:
                truncated_title = slide['title'][:max_title_len - 1] + '…'
                status = f" {position}{scroll_indicator}  {truncated_title}"
                available_for_padding = width - len(status) - len(help_hint) - min_spacing

        padding = max(1, available_for_padding)

        # Build the full status line, ensuring it fits exactly in terminal width
        status_line = f"{status}{' ' * padding}{help_hint}"

        # Pad or truncate to exact width
        if len(status_line) < width:
            status_line = status_line + ' ' * (width - len(status_line))
        else:
            status_line = status_line[:width]

        # Use dim/inverse colors for status bar
        print('\033[7m', end='')  # Inverse video
        print(status_line, end='')
        print('\033[0m', end='')  # Reset
        sys.stdout.flush()

    def _render_index(self, selected_index=None):
        """Render slide index with optional selection highlight."""
        self._clear_screen()
        width, height = self._get_terminal_size()

        # Use selected_index for highlight, default to current_index
        highlight = selected_index if selected_index is not None else self.current_index

        print('\033[1m' + '═' * width + '\033[0m')
        print('\033[1mSLIDE INDEX\033[0m')
        print('═' * width)
        print()

        for i, slide in enumerate(self.slides):
            if i == highlight:
                # Highlighted selection - inverse video
                marker = '▶ '
                num = f"{i + 1:2d}"
                line = f"{marker}{num}. {slide['title']}"
                # Pad to fill width for full highlight bar
                line = line + ' ' * (width - len(line))
                print(f'\033[7m{line}\033[0m')
            else:
                marker = '  '
                num = f"{i + 1:2d}"
                print(f"{marker}{num}. {slide['title']}")

        print()
        print('─' * width)
        print('[↑/k]up [↓/j]down [ENTER]select [ESC/q]cancel')
        sys.stdout.flush()

    def _render_help(self):
        """Render help screen."""
        self._clear_screen()
        width, height = self._get_terminal_size()

        help_text = """
╔═══════════════════════════════════════════════════════════════╗
║                     SLIDESHOW CONTROLS                        ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║   NAVIGATION                                                  ║
║   ──────────                                                  ║
║   n, SPACE, →, ENTER       Next slide                         ║
║   p, ←, BACKSPACE          Previous slide                     ║
║   f                        First slide                        ║
║   l                        Last slide                         ║
║   g                        Go to slide number                 ║
║                                                               ║
║   SCROLLING (for tall slides)                                 ║
║   ───────────────────────────                                 ║
║   j, ↓                     Scroll down                        ║
║   k, ↑                     Scroll up                          ║
║                                                               ║
║   SPEAKER NOTES                                               ║
║   ─────────────                                               ║
║   s                        Toggle notes panel on/off          ║
║   +, =                     Expand notes panel                 ║
║   -, _                     Shrink notes panel                 ║
║                                                               ║
║   VIEW OPTIONS                                                ║
║   ────────────                                                ║
║   i                        Show slide index                   ║
║   r                        Refresh/redraw screen              ║
║   h, ?                     Show this help                     ║
║                                                               ║
║   q, x, ESC                Quit slideshow                     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

                Press any key to return to slide...
"""
        print(help_text)
        sys.stdout.flush()

    def _get_keypress(self):
        """Get a single keypress from terminal."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)

            # Handle escape sequences (arrow keys, etc.)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A':  # Up arrow
                        return 'UP'
                    elif ch3 == 'B':  # Down arrow
                        return 'DOWN'
                    elif ch3 == 'C':  # Right arrow
                        return 'RIGHT'
                    elif ch3 == 'D':  # Left arrow
                        return 'LEFT'
                return 'ESC'

            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _get_number_input(self, prompt):
        """Get a number input from user."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            print(f"\n{prompt}", end='', flush=True)

            # Read number
            num_str = ''
            while True:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

                if ch in '\r\n':
                    break
                elif ch == '\x7f':  # Backspace
                    if num_str:
                        num_str = num_str[:-1]
                        print('\b \b', end='', flush=True)
                elif ch == '\x1b':  # Escape
                    return None
                elif ch.isdigit():
                    num_str += ch
                    print(ch, end='', flush=True)

            return int(num_str) if num_str else None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def next_slide(self):
        """Go to next slide."""
        if self.current_index < len(self.slides) - 1:
            self.current_index += 1
            self.scroll_offset = 0  # Reset scroll on slide change
            return True
        return False

    def prev_slide(self):
        """Go to previous slide."""
        if self.current_index > 0:
            self.current_index -= 1
            self.scroll_offset = 0  # Reset scroll on slide change
            return True
        return False

    def goto_slide(self, index):
        """Go to specific slide by index (1-based)."""
        if 1 <= index <= len(self.slides):
            self.current_index = index - 1
            self.scroll_offset = 0  # Reset scroll on slide change
            return True
        return False

    def scroll_down(self, lines=3):
        """Scroll down within current slide."""
        self.scroll_offset += lines

    def scroll_up(self, lines=3):
        """Scroll up within current slide."""
        self.scroll_offset = max(0, self.scroll_offset - lines)

    def run(self):
        """Main slideshow loop."""
        if not self.slides:
            print("No slides found!")
            return

        # Hide cursor
        print('\033[?25l', end='')

        try:
            self._render_slide()

            while True:
                key = self._get_keypress()

                # Scroll down within slide
                if key in ('j', 'DOWN'):
                    self.scroll_down()
                    self._render_slide()

                # Scroll up within slide
                elif key in ('k', 'UP'):
                    self.scroll_up()
                    self._render_slide()

                # Next slide
                elif key in ('n', ' ', '\r', '\n', 'RIGHT'):
                    self.next_slide()
                    self._render_slide()

                # Previous slide
                elif key in ('p', '\x7f', 'LEFT'):  # \x7f is backspace
                    self.prev_slide()
                    self._render_slide()

                # First slide
                elif key == 'f':
                    self.current_index = 0
                    self.scroll_offset = 0
                    self._render_slide()

                # Last slide
                elif key == 'l':
                    self.current_index = len(self.slides) - 1
                    self.scroll_offset = 0
                    self._render_slide()

                # Go to slide
                elif key == 'g':
                    num = self._get_number_input("Go to slide: ")
                    if num is not None:
                        self.goto_slide(num)
                    self._render_slide()

                # Toggle speaker notes panel
                elif key == 's':
                    self.show_notes = not self.show_notes
                    self._render_slide()

                # Resize notes panel
                elif key == '+' or key == '=':
                    if self.show_notes:
                        self.notes_height = min(self.notes_height + 2, 20)
                        self._render_slide()

                elif key == '-' or key == '_':
                    if self.show_notes:
                        self.notes_height = max(self.notes_height - 2, 2)
                        self._render_slide()

                # Index
                elif key == 'i':
                    selected = self.current_index
                    self._render_index(selected)

                    while True:
                        key2 = self._get_keypress()

                        # Navigate up
                        if key2 in ('k', 'UP'):
                            selected = max(0, selected - 1)
                            self._render_index(selected)

                        # Navigate down
                        elif key2 in ('j', 'DOWN'):
                            selected = min(len(self.slides) - 1, selected + 1)
                            self._render_index(selected)

                        # Select current and go to slide
                        elif key2 in ('\r', '\n', ' '):
                            self.goto_slide(selected + 1)
                            break

                        # Cancel/exit index
                        elif key2 in ('q', 'ESC', '\x1b', 'i'):
                            break

                    self._render_slide()

                # Help
                elif key in ('h', '?'):
                    self._render_help()
                    self._get_keypress()
                    self._render_slide()

                # Refresh
                elif key == 'r':
                    self._render_slide()

                # Quit
                elif key in ('q', 'x', 'ESC', '\x03'):  # \x03 is Ctrl+C
                    break

        finally:
            # Show cursor and clear screen
            print('\033[?25h', end='')
            self._clear_screen()
            print("Slideshow ended.")


def main():
    # Determine slides directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    slides_dir = os.path.join(script_dir, 'slides')

    if not os.path.isdir(slides_dir):
        print(f"Error: Slides directory not found: {slides_dir}")
        sys.exit(1)

    # Check for slides
    slides = glob.glob(os.path.join(slides_dir, '*.md'))
    if not slides:
        print(f"Error: No slides found in {slides_dir}")
        sys.exit(1)

    print(f"Loading {len(slides)} slides...")
    print("Press any key to start, or 'q' to quit.")

    # Wait for keypress
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    if ch.lower() == 'q':
        print("\nQuitting.")
        sys.exit(0)

    # Run slideshow
    slideshow = Slideshow(slides_dir)
    slideshow.run()


if __name__ == '__main__':
    main()
