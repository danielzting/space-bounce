"""
UI Elements for PyGame.
"""
import pygame

def draw_text(surface, fg, bg, font, text, rect):
    """Draw text and automatically wrap words to fit into rect. Return text that didn't fit."""
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        image = font.render(text[:i], 1, fg, bg)
        image.set_colorkey(bg)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text

class Button(object):
    """Generic PyGame button class."""
    def __init__(self, surface, rect, fg=None, bg=None, font=None, text=None, image=None):
        """Initiate meta variables; button creation will be done in subclasses."""
        # Descriptors
        self.surface = surface
        self.rect = rect
        self.fg = fg
        self.bg = bg
        self.font = font
        self.text = text
        self.image = image
        # Border variables
        self.top_border = rect[1] # Y of top left of rect
        self.right_border = rect[0] + rect[2] # X of top left of rect plus width
        self.bottom_border = rect[1] + rect[3] # Y of top left of rect plus height
        self.left_border = rect[0] # X of top left of rect

    @property
    def hovered(self):
        """Return a boolean representing if mouse is hovering over button."""
        row, col = pygame.mouse.get_pos()
        if self.left_border <= row <= self.right_border and self.top_border <= col <= self.bottom_border:
            return True

    @property
    def clicked(self):
        """Return a boolean representing if any mouse button has clicked (but not released) the button."""
        if not all(val == 0 for val in pygame.mouse.get_pressed()):
            if self.hovered:
                return True

class TextButton(Button):
    """Text PyGame button class."""
    def __init__(self, surface, fg, bg, font, text, rect):
        """Create a customizable text button."""
        # Initiate boundary variables
        super().__init__(surface, rect, fg=fg, bg=bg, font=font, text=text)
        # Render font
        text_surface = font.render(text, True, fg)
        text_rect = text_surface.get_rect()
        # Center text on button
        text_rect.center = (self.left_border + (self.right_border - self.left_border) / 2,
            self.top_border + (self.bottom_border - self.top_border) / 2)
        # Render text and button (which is really just a rect)
        if bg:
            pygame.draw.rect(surface, bg, (rect[0], rect[1], rect[2], rect[3]))
        surface.blit(text_surface, text_rect)

    def toggle_bg(self, bg):
        """Change a button's background color."""
        # Save change to bg
        self.bg = bg
        # Render font
        text_surface = self.font.render(self.text, True, self.fg)
        text_rect = text_surface.get_rect()
        # Center text on button
        text_rect.center = (self.left_border + (self.right_border - self.left_border) / 2,
            self.top_border + (self.bottom_border - self.top_border) / 2)
        # Render text and button
        pygame.draw.rect(self.surface, bg, (self.rect[0], self.rect[1], self.rect[2], self.rect[3]))
        self.surface.blit(text_surface, text_rect)

class ImageButton(Button):
    """Image PyGame button class."""
    def __init__(self, surface, image, rect):
        """Create a customizable image button."""
        # Initiate boundary variables
        super().__init__(surface, rect, image=image)
        # Load and render image
        img = pygame.image.load(image)
        surface.blit(img, (rect[0], rect[1], rect[2], rect[3]))
