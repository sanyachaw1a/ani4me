"""
CSC111 Project: User Interface classes

This module contains the classes necessary to create and run the user interface
that the user will interact with in the Ani-for-Me recommendation system.

This file is Copyright (c) 2023 Hai Shi, Liam Alexander Maguire, Amelia Wu, and Sanya Chawla.
"""

from typing import Optional

from math import pi, cos, sin, ceil
import pygame

import python_ta

from anime_and_users import Anime

Coord = int | float
Position = tuple[Coord, Coord]
Colour = tuple[int, int, int]


class Button:
    """A class that represents a button in the UI.
    """
    _screen: pygame.Surface
    _height: Coord
    _width: Coord
    position: Position
    _text: str
    _current_colour: Colour
    _colour: Colour
    _hover_colour: Colour
    _text_colour: Colour
    _border_colour: Optional[Colour]
    _border_radius: int
    image: pygame.Surface
    font_style: str
    _is_centered_text: bool

    def __init__(self, screen: pygame.surface, height: Coord, width: Coord, position: Position, text: str,
                 colour: Colour, hover_colour: Colour, text_colour: Colour, font_style: Optional[str] = None,
                 border_colour: Optional[Colour] = None,
                 border_radius: int = 0, image: Optional[pygame.Surface] = None, is_centered_text: bool = True) -> None:
        """Initialize a Button object.
        """
        self._screen = screen
        self._height = height
        self._width = width
        self.position = position
        self._text = text
        self._current_colour = colour
        self._colour = colour
        self._hover_colour = hover_colour
        self._text_colour = text_colour
        if border_colour is not None:
            self._border_colour = border_colour
        else:
            self._border_colour = None
        self._border_radius = border_radius
        self.image = image
        if font_style is not None:
            self.font_style = font_style
        else:
            self.font_style = None
        self._is_centered_text = is_centered_text

    def draw(self) -> None:
        """Draw a button on a pygame screen.
        """
        btn_rect = pygame.Rect(self.position, (self._width, self._height))
        pygame.draw.rect(self._screen, self._current_colour, btn_rect, border_radius=self._border_radius)
        if self._border_colour is not None:
            pygame.draw.rect(self._screen, self._border_colour, btn_rect, 3, border_radius=self._border_radius)

        word_surf = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        if self.font_style is not None:
            font = pygame.font.SysFont(self.font_style, int(self._height * 0.5), bold=False)
        else:
            font = pygame.font.SysFont('roboto', int(self._height * 0.5), bold=False)
        img = font.render(self._text, True, self._text_colour)
        if self._is_centered_text:
            word_surf.blit(img, ((word_surf.get_width() - img.get_width()) / 2,
                                 (word_surf.get_height() - img.get_height()) / 2))
        else:
            word_surf.blit(img, (10, (word_surf.get_height() - img.get_height()) / 2))
        self._screen.blit(word_surf, self.position)

        if self.image is not None:
            img_x = self.position[0] + (self._width - self.image.get_width()) / 2
            img_y = self.position[1] + (self._height - self.image.get_height()) / 2
            self._screen.blit(self.image, (img_x, img_y))

    def _is_hovered(self, mouse_pos: Position) -> bool:
        """Return whether the button is being hovered."""
        is_hover_x = self.position[0] < mouse_pos[0] < self.position[0] + self._width
        is_hover_y = self.position[1] < mouse_pos[1] < self.position[1] + self._height
        return is_hover_y and is_hover_x

    def update_colour(self, mouse_pos) -> bool:
        """Return whether the button is being hovered over and
        change colour if it is.
        """
        if self._is_hovered(mouse_pos):
            self._current_colour = self._hover_colour
            r_val = True
        else:
            self._current_colour = self._colour
            r_val = False
        self.draw()
        return r_val

    def is_clicked(self, is_mouse_down: bool, mouse_pos: Position):
        """Return whether the button is clicked."""
        return self._is_hovered(mouse_pos) and is_mouse_down


class FivePointGraph:
    """Five point graph for displaying rating.
    """
    screen: pygame.Surface
    ratings: Optional[list[int]]
    _size: Coord
    position: Position
    colour_one: Colour
    colour_two: Colour
    dot_colour: Colour
    line_colour: Colour
    graph_colour: tuple[int, int, int, int]
    ratings: list[int]
    rating_alpha: int
    font_style: str

    def __init__(self, screen: pygame.Surface, ratings: Optional[list[int]],
                 size: Coord, position: Position, colour_one: Colour,
                 colour_two: Colour, dot_colour: Colour, line_colour: Colour,
                 graph_colour: tuple[int, int, int, int], rating_alpha: int, font_style: str) -> None:
        """ Initialize a FivePointGraph object.
        """
        self.screen = screen
        self.ratings = ratings
        self._size = size
        self.position = position
        self.colour_one = colour_one
        self.colour_two = colour_two
        self.dot_colour = dot_colour
        self.line_colour = line_colour
        self.graph_colour = graph_colour
        self.rating_alpha = rating_alpha
        self.font_style = font_style

    def draw(self) -> None:
        """Draw a graph that displays ratings for
        5 categories(animation, sound, character, enjoyment, story).
        """
        radius = self._size / 2

        # Draw the empty graph
        polygon_25_points = self.get_points(complex(0, - radius * 0.25))
        polygon_50_points = self.get_points(complex(0, - radius * 0.5))
        polygon_75_points = self.get_points(complex(0, - radius * 0.75))
        polygon_100_points = self.get_points(complex(0, - radius))
        legend_points = self.get_points(complex(0, - radius * 1.25))

        pygame.draw.polygon(self.screen, self.colour_one, polygon_100_points)
        pygame.draw.polygon(self.screen, self.colour_two, polygon_75_points)
        pygame.draw.polygon(self.screen, self.colour_one, polygon_50_points)
        pygame.draw.polygon(self.screen, self.colour_two, polygon_25_points)

        legend_font = pygame.font.SysFont(self.font_style, 20, bold=True)
        legend_title = ['ANIMATION', 'SOUND', 'CHARACTER', 'ENJOYMENT', 'STORY']
        for i, title in enumerate(legend_title):
            text = legend_font.render(title, True, (46, 81, 162))
            self.screen.blit(text, (legend_points[i][0] - text.get_width() / 2,
                                    legend_points[i][1]))

    def update(self, ratings: list[float]) -> None:
        """Update the drawn graph that displays ratings
        with a new list of ratings.
        """
        self.draw()
        # Draw the anime's rating
        radius = self._size / 2
        relative_rating_graph_points, rating_graph_points = self._get_rating_points(complex(0, - radius), ratings)

        shape_surf = pygame.Surface((self._size, self._size), pygame.SRCALPHA)
        pygame.draw.polygon(shape_surf, self.graph_colour, relative_rating_graph_points)
        self.screen.blit(shape_surf, self.position)

        pygame.draw.line(self.screen, self.line_colour, rating_graph_points[0], rating_graph_points[1], 3)
        pygame.draw.line(self.screen, self.line_colour, rating_graph_points[1], rating_graph_points[2], 3)
        pygame.draw.line(self.screen, self.line_colour, rating_graph_points[2], rating_graph_points[3], 3)
        pygame.draw.line(self.screen, self.line_colour, rating_graph_points[3], rating_graph_points[4], 3)
        pygame.draw.line(self.screen, self.line_colour, rating_graph_points[4], rating_graph_points[0], 3)

        for point1 in rating_graph_points:
            pygame.draw.circle(self.screen, self.dot_colour, point1, 5)

        rating_surf = pygame.Surface((self._size, self._size), pygame.SRCALPHA)
        font = pygame.font.SysFont(self.font_style, 64, bold=False)
        img = font.render(f"{ratings[0]}", True, (23, 41, 81))
        img.set_alpha(self.rating_alpha)
        rating_surf.blit(img, ((rating_surf.get_width() - img.get_width()) / 2,
                               (rating_surf.get_height() - img.get_height()) / 2))
        self.screen.blit(rating_surf, self.position)

    def get_points(self, position: complex) -> list[Position]:
        """Return the points of the graph's nodes."""
        theta = 2 * pi / 5
        points = []
        for _ in range(5):
            screen_x_pos = position.real + self._size / 2 + self.position[0]
            screen_y_pos = position.imag + self._size / 2 + self.position[1]
            points.append((screen_x_pos, screen_y_pos))
            position *= complex(cos(theta), sin(theta))
        return points

    def _get_rating_points(self, position: complex, ratings: list[float]) -> tuple[list[Position], list[Position]]:
        """Return the position on the screen that the ratings should appear on the graph."""
        theta = 2 * pi / 5
        points = []
        for _ in range(5):
            x_position = position.real
            y_position = position.imag
            points.append((x_position, y_position))
            position *= complex(cos(theta), sin(theta))

        screen_points = []
        relative_points = []

        for i in range(5):
            rating_x = points[i][0] * ratings[i] / 10
            rating_y = points[i][1] * ratings[i] / 10
            screen_x_pos = rating_x + self._size / 2 + self.position[0]
            screen_y_pos = rating_y + self._size / 2 + self.position[1]
            relative_points.append((rating_x + self._size / 2, rating_y + self._size / 2))
            screen_points.append((screen_x_pos, screen_y_pos))
        return relative_points, screen_points


class AnimeSpotlight:
    """An object representing a selected anime
    from given recommendations.
    """
    screen: pygame.Surface
    background_colour: Colour
    position: Position
    height: Coord
    width: Coord
    margin: Coord
    title_height: Coord
    anime: Optional[str]
    anime_colour: Colour
    graph: FivePointGraph
    font_size: int
    curr_font_size: int
    title_font: pygame.font.Font
    font_style: str

    def __init__(self, screen: pygame.Surface, background_colour: Colour,
                 top_bar_height_percentage: float, width_percentage: float,
                 anime_colour: Colour, colour_one: Colour, colour_two: Colour,
                 dot_colour: Colour, line_colour: Colour, graph_colour: tuple[int, int, int, int], rating_alpha: int,
                 font_style: str, title_font_size: int) -> None:
        """Initialize an AnimeSpotlight object.
        """
        self.screen = screen
        self.background_colour = background_colour
        self.position = (20, screen.get_height() * top_bar_height_percentage)
        self.height = screen.get_height() * (1 - top_bar_height_percentage)
        self.width = screen.get_width() * width_percentage
        self.margin = self.width * 0.1
        self.title_height = self.margin + self.height * 0.3
        self.anime = None
        self.ratings = None
        self.anime_colour = anime_colour
        self.font_style = font_style
        self.graph = FivePointGraph(screen=screen,
                                    ratings=None,
                                    size=self.width - 2 * self.margin,
                                    position=(self.margin + 20, self.position[1] + self.title_height),
                                    colour_one=colour_one,
                                    colour_two=colour_two,
                                    dot_colour=dot_colour,
                                    line_colour=line_colour,
                                    graph_colour=graph_colour,
                                    rating_alpha=rating_alpha,
                                    font_style=font_style)
        self.font_size = title_font_size
        self.curr_font_size = self.font_size
        self.title_font = pygame.font.SysFont(font_style, self.font_size, bold=False)

    def draw(self) -> None:
        """Draw a rectangular object that stores the AnimeSpotlight object.
        """
        anime_spotlight_rect = pygame.Rect(self.position, (self.width, self.height))
        pygame.draw.rect(self.screen, self.background_colour, anime_spotlight_rect)
        self.graph.draw()

    def redraw(self) -> None:
        """Redraw the graph attribute with ratings.
        """
        self.draw()
        self.format_and_display_title()
        rating_order = ['overall', 'animation', 'sound', 'character', 'enjoyment', 'story']
        ratings = [self.ratings[rating_order[i]] for i in range(6)]
        self.graph.update(ratings)

    def update(self, anime: Anime) -> None:
        """Update graph attribute with a given Anime object.
        """
        self.anime = anime.get_title()
        # self.ratings = list(anime.ratings.values()) Use this if ratings attribute is a dict
        self.ratings = anime.calculate_average_ratings()
        self.draw()
        self.format_and_display_title()
        rating_order = ['overall', 'animation', 'sound', 'character', 'enjoyment', 'story']
        ratings = [self.ratings[rating_order[i]] for i in range(6)]
        self.graph.update(ratings)

    def format_and_display_title(self) -> None:
        """A method that formats and displays a title
        according to the object's attributes.
        """
        self.title_font = pygame.font.SysFont(self.font_style, self.font_size, bold=False)
        formatted_lines = self.format_title_lines()
        self.adjust_font_size(formatted_lines)
        new_formatted_lines = self.format_title_lines()
        self.display_formatted_text(new_formatted_lines)

    def format_title_lines(self) -> list[str]:
        """Takes a title to be rendered and returns a list of string where each string is a segment of the original
        to be rendered so that each new line fits to the screen.
        """
        final_lines = []
        title = self.anime
        curr_line = title
        text = self.title_font.render(title, True, self.anime_colour)
        curr_line_width = text.get_width()
        title_progress = ''
        rest = ''

        while title_progress != title:
            while curr_line_width > self.width - 2 * self.margin:
                curr_line, part, new_rest = curr_line.rpartition(' ')
                rest = part + new_rest + rest
                text = self.title_font.render(curr_line, True, self.anime_colour)
                curr_line_width = text.get_width()
            final_lines.append(curr_line)
            title_progress += curr_line
            curr_line = rest
            new_text = self.title_font.render(curr_line, True, self.anime_colour)
            curr_line_width = new_text.get_width()
            rest = ''
        return final_lines

    def adjust_font_size(self, lines: list[str]) -> None:
        """Decreases the font size (self.anime_font) to ensure the title fits."""
        self.curr_font_size = self.font_size
        self.update_font()
        num_lines = len(lines)
        line_render = self.title_font.render(lines[0], True, (0, 0, 0))
        line_render_height = line_render.get_height()
        render_height = num_lines * line_render_height
        i = 0
        while render_height > 100:
            i += 1
            self.title_font.get_height()
            self.curr_font_size -= 1
            self.update_font()

            line_render = self.title_font.render(lines[0], True, (0, 0, 0))
            line_render_height = line_render.get_height()
            render_height = num_lines * line_render_height
        self.update_font()

    def update_font(self) -> None:
        """A method that updates the title font according to
        self.font_style and self.curr_font_size.
        """
        self.title_font = pygame.font.SysFont(self.font_style, self.curr_font_size, bold=False)

    def display_formatted_text(self, lines: list[str]) -> None:
        """Helper method that neatly displays the formatted lines."""
        text_renders = {}
        # total_title_height = 0
        for index, line in enumerate(lines):
            text_render = self.title_font.render(line, True, self.anime_colour)
            text_renders[index] = text_render
            # total_title_height += text_render.get_height()

        # self.title_height = self.margin + total_title_height
        title_surf = pygame.Surface((self.width, self.title_height), pygame.SRCALPHA)
        # Display each line
        for index, text_render in text_renders.items():
            title_surf.blit(text_render, ((title_surf.get_width() - text_render.get_width()) / 2,
                                          index * text_render.get_height()
                                          + (title_surf.get_height() - text_render.get_height()) / 2 - 40))
            self.screen.blit(title_surf, self.position)


class RecommendationDisplay:
    """A class that represents the
    display for final anime recommendations in pygame.
    """
    screen: pygame.Surface
    width: Coord
    height: Coord
    position: Position
    margin: Coord
    title_height: Coord
    anime_button_colour: Colour
    anime_button_hover_colour: Colour
    title_colour: Colour
    recommendation_text_colour: Colour
    generate_button_colour: Colour
    generate_button_hover_colour: Colour
    generate_button: Button
    anime_font: pygame.font.Font
    font_style: str
    section_title_colour: Colour

    def __init__(self, screen: pygame.Surface, top_bar_height_percentage: float,
                 width_percentage: float, anime_button_colour: Colour, anime_button_hover_colour: Colour,
                 title_colour: Colour, generate_button_colour: Colour, generate_button_hover_colour: Colour,
                 recommendation_text_colour: Colour, font_style: str, section_title_colour: Colour) -> None:
        """Initializes a new RecommendationDisplay object.
        """
        self.screen = screen
        self.position = (
            screen.get_width() * (1 - width_percentage) + 20, screen.get_height() * top_bar_height_percentage)
        self.height = screen.get_height() * (1 - top_bar_height_percentage)
        self.width = screen.get_width() * width_percentage
        self.margin = self.width * 0.05
        self.title_height = self.height * 0.1
        self.anime_button_colour = anime_button_colour
        self.anime_button_hover_colour = anime_button_hover_colour
        self.title_colour = title_colour
        self.generate_button_colour = generate_button_colour
        self.generate_button_hover_colour = generate_button_hover_colour
        self.anime_font = pygame.font.SysFont(font_style, int(self.height * 0.06), bold=False)
        self.recommendation_text_colour = recommendation_text_colour
        generate_button_width = self.width * 0.3
        generate_button_height = self.title_height
        self.generate_button = Button(screen=self.screen,
                                      height=generate_button_height,
                                      width=generate_button_width,
                                      position=(self.screen.get_width() - self.margin - generate_button_width,
                                                self.position[1] + self.margin / 2),
                                      text='GENERATE',
                                      colour=self.generate_button_colour,
                                      hover_colour=self.generate_button_hover_colour,
                                      text_colour=self.title_colour,
                                      border_radius=50,
                                      font_style=font_style)
        self.font_style = font_style
        self.section_title_colour = section_title_colour

    def draw(self) -> None:
        """A method that draws the RecommendationDisplay according to it's
        font and stored title colour, etc.
        """
        # Section title
        title_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        img = self.anime_font.render('Recommendations', True, self.section_title_colour)
        title_surf.blit(img, (self.margin, 30))
        self.screen.blit(title_surf, self.position)
        self.generate_button.draw()

    def update(self, animes: list[Anime], spotlight: AnimeSpotlight) -> dict[str: tuple[Anime, Button]]:
        """Updates recommendations according to list of anime provided and returns the buttons created in a dict mapping
        the anime title to its button on the display. This makes checking for button clicks possible.
        """
        # potentially sort them
        button_height = (self.height - 2 * self.margin - self.title_height) / len(animes)
        button_width = self.width - 2 * self.margin

        anime_buttons = {}
        for index, anime in enumerate(animes):
            title = self.shorten_title(anime.get_title())
            title = f"{index + 1}. {title}"
            anime_button = Button(screen=self.screen,
                                  height=button_height,
                                  width=button_width,
                                  position=(self.position[0] + self.margin,
                                            self.position[1] + self.margin + self.title_height + index * button_height),
                                  text=title,
                                  colour=self.anime_button_colour,
                                  hover_colour=self.anime_button_hover_colour,
                                  text_colour=self.recommendation_text_colour,
                                  font_style=self.font_style,
                                  is_centered_text=False)
            anime_button.draw()
            anime_buttons[anime.get_title()] = (anime, anime_button)
        # print(animes)
        spotlight.update(animes[0])
        return anime_buttons

    def shorten_title(self, text) -> str:
        """A method that shortens the title displayed in pygame.
        """
        render = self.anime_font.render(text, True, (0, 0, 0))
        render_width = render.get_width()

        while render_width > 600:
            if text[-3:] == '...':
                text = text[:-3]
            text = text[:-1] + '...'
            render = self.anime_font.render(text, True, (0, 0, 0))
            render_width = render.get_width()

        return text


class PreferenceMeter(Button):
    """
    An object that represents a preference meter where users
    can indicate their preference for a category over another(
    between ['STORY', 'ANIMATION', 'SOUND', 'CHARACTER']).
    """
    value: float | int
    meter_colour: Colour
    curr_meter_rect: Optional[pygame.Rect]

    def __init__(self, screen: pygame.Surface, height: Coord, width: Coord, position: Position, colour: Colour,
                 border_colour: Colour, meter_colour: Colour) -> None:
        """
        Initialize a new PreferenceMeter object.
        """
        Button.__init__(self, screen, height, width, position, '', colour, colour, colour, border_colour=border_colour)
        self.meter_colour = meter_colour
        self.value = 1
        self.curr_meter_rect = None

    def draw(self) -> None:
        """Draw a button representing the PreferenceMeter object.
        """
        btn_rect = pygame.Rect(self.position, (self._width, self._height))
        pygame.draw.rect(self._screen, self._current_colour, btn_rect)
        if self.curr_meter_rect is not None:
            pygame.draw.rect(self._screen, self.meter_colour, self.curr_meter_rect)
        pygame.draw.rect(self._screen, self._border_colour, btn_rect, 3)
        self.update((0, 55))

    def update(self, mouse_pos: Position) -> None:
        """Update the drawn button according to the position of the mouse.
        """
        mouse_y = mouse_pos[1]
        meter_height = self.position[1] + self._height - mouse_y
        # Update the value
        self.value = ceil(meter_height / self._height * 10)
        # Update the drawing
        meter_position = (self.position[0], mouse_y)
        meter_rect = pygame.Rect(meter_position, (self._width, meter_height))
        self.curr_meter_rect = meter_rect
        btn_rect = pygame.Rect(self.position, (self._width, self._height))
        pygame.draw.rect(self._screen, self._current_colour, btn_rect)
        pygame.draw.rect(self._screen, self.meter_colour, meter_rect)
        pygame.draw.rect(self._screen, self._border_colour, btn_rect, 3)


class PreferenceMeterDisplay:
    """A class representing the pygame
    display for a preference meter.
    """
    screen: pygame.surface
    height: Coord
    width: Coord
    meters: dict[str: PreferenceMeter]
    position: Position
    colour: Colour
    border_colour: Colour
    meter_colour: Colour
    font: pygame.font.Font
    text_height: Coord
    text_colour: Colour

    def __init__(self, screen: pygame.surface, height_percentage: float, offset_x_percentage: float, colour: Colour,
                 border_colour: Colour, meter_colour: Colour, text_colour: Colour, font_style: str) -> None:
        """Initialize a new PreferenceMeterDisplay object.
        """
        self.screen = screen
        self.height = screen.get_height() * height_percentage * 0.6
        self.width = screen.get_width() * 0.03
        self.meters = {}
        self.position = (screen.get_width() * offset_x_percentage,
                         screen.get_height() * height_percentage * 0.1)
        self.colour = colour
        self.border_colour = border_colour
        self.meter_colour = meter_colour
        self.font = pygame.font.SysFont(font_style, int(screen.get_height() * 0.025), bold=False)
        self.text_height = screen.get_height() * height_percentage * 0.7
        self.text_colour = text_colour

    def draw_display(self) -> None:
        """Draw a display for the preference meter with the indicators
        ['STORY', 'ANIMATION', 'SOUND', 'CHARACTER'].
        """
        meter_names = ['STORY', 'ANIMATION', 'SOUND', 'CHARACTER']

        for i, meter_name in enumerate(meter_names):
            position_x = self.position[0] + i * self.width * 5 / 2
            meter = PreferenceMeter(self.screen,
                                    self.height,
                                    self.width,
                                    (position_x, self.position[1]),
                                    self.colour,
                                    self.border_colour,
                                    self.meter_colour)
            meter.draw()
            text = self.font.render(meter_name, True, self.text_colour)
            offset_x = text.get_width() / 2
            self.screen.blit(text, (position_x + self.width / 2 - offset_x, self.text_height + 8))

            self.meters[meter_name] = meter

    def draw_meter_titles(self) -> None:
        """A method to draw the titles for each category in the pygame screen.
        """
        meter_names = ['STORY', 'ANIMATION', 'SOUND', 'CHARACTER']

        for i, meter_name in enumerate(meter_names):
            position_x = self.position[0] + i * self.width * 5 / 2
            text = self.font.render(meter_name, True, (255, 255, 255))
            offset_x = text.get_width() / 2
            self.screen.blit(text, (position_x + self.width / 2 - offset_x, self.text_height + 8))

    def get_preferences(self) -> dict[str: int]:
        """Return a dict where the keys are the categories(with 'num-epidodes' included)
        and the corresponding values are the user's given information.
        """
        prio = {'story': self.meters['STORY'].value,
                'animation': self.meters['ANIMATION'].value,
                'sound': self.meters['SOUND'].value,
                'character': self.meters['CHARACTER'].value,
                'num-episodes': 27}
        return prio


class DropDownMenuButton(Button):
    """
    A class representing a button on a drop down menu for the
    user to interact with.
    """
    selected_colour: Colour
    default_colour: Colour
    is_toggled: bool
    original_pos: Position

    def __init__(self, screen: pygame.surface, height: Coord, width: Coord, position: Position, genre: str,
                 colour: Colour, selected_colour: Colour, border_colour: Colour, genre_hover_colour: Colour,
                 font_style: str) -> None:
        """Initialize a DropDownMenuButton object.
        """
        Button.__init__(self, screen, height, width, position, genre, colour, genre_hover_colour, (0, 0, 0),
                        font_style, border_colour)
        self.selected_colour = selected_colour
        self.default_colour = colour
        self.is_toggled = False
        self.original_pos = position

    def update(self) -> None:
        """Update the colour of the button if it is toggled.
        """
        self.is_toggled = not self.is_toggled
        if self.is_toggled:
            self._colour = self.selected_colour
            self.draw()
        else:
            self._colour = self.default_colour
            self.draw()


class DropDownMenu:
    """ A class representing a drop down menu
    in the user interface.
    """
    clicked_buttons: set[str]
    button_collection: dict[str: DropDownMenuButton]
    is_deployed: bool
    font_style: str
    coordinates: tuple[int, int, int, int]

    def __init__(self, font_style: str) -> None:
        """Initialize a DropDownMenu object.
        """
        self.clicked_buttons = set()
        self.button_collection = {}
        self.is_deployed = False
        self.font_style = font_style
        self.coordinates = (0, 0, 0, 0)

    def add_button(self, name: str, button: DropDownMenuButton) -> None:
        """Add a button with the given name to the drop down menu on
        the user interface.
        """
        self.button_collection[name] = button

    def draw_menu(self, screen: pygame.Surface, base_pos: Position, size: tuple[Coord, Coord],
                  menu_bg_colour: Colour) -> None:
        """Draw a menu in pygame following the given size and position.
        """
        self.coordinates = base_pos[0] - 3, base_pos[1] - 3, base_pos[0] + size[0] + 6, base_pos[1] + size[1] + 6
        for button in self.button_collection.values():
            menu_outline_rect = pygame.Rect(base_pos[0] - 3, base_pos[1] - 3, size[0] + 6, size[1] + 6)
            menu_bg_rect = pygame.Rect(base_pos[0], base_pos[1], size[0], size[1])
            pygame.draw.rect(screen, (37, 65, 130), menu_outline_rect)
            pygame.draw.rect(screen, menu_bg_colour, menu_bg_rect)
            button.draw()

    def update(self) -> None:
        """Update self.is_deployed to the opposite bool value.
        """
        self.is_deployed = not self.is_deployed

    def clicked_off(self, is_clicking: bool, mouse_pos: Position) -> bool:
        """Return whether the mouse is clicking within the coordinates
        of the menu and it is off.
        """
        mouse_x_off = not (self.coordinates[0] <= mouse_pos[0] <= self.coordinates[2])
        mouse_y_off = not (self.coordinates[1] <= mouse_pos[1] <= self.coordinates[3])
        is_mouse_off = mouse_x_off or mouse_y_off
        if is_clicking and is_mouse_off:
            return True
        else:
            return False


class TextInputBox(Button):
    """A class representing a box in the user interface
    where the user can input text.
    """
    input_text: str
    font: pygame.font.Font
    is_active: bool
    text_colour: Colour
    colour_active: Colour
    colour_passive: Colour
    colour_invalid: Colour
    curr_colour: Colour
    text_pos: Position
    bg_colour: Colour

    def __init__(self, screen: pygame.Surface, height: Coord, width: Coord, position: Position,
                 font: pygame.font.Font, colour_passive: Colour, colour_active: Colour, text_colour: Colour,
                 bg_colour: Colour, border_colour: Colour) -> None:
        """Initialize a TextInputBox object.
        """
        Button.__init__(self, screen, height, width, position, '', (0, 0, 0), (0, 0, 0), (0, 0, 0),
                        border_colour=border_colour)
        self.input_text = ''
        self.font = font
        self.is_active = False
        self.text_colour = text_colour
        self.colour_passive = colour_passive
        self.colour_active = colour_active

        self.curr_colour = colour_passive
        self.bg_colour = bg_colour

    def draw(self) -> None:
        """Draw a rectangle in the pygame user interface that represents the text
        input box.
        """
        btn_rect = pygame.Rect(self.position, (self._width, self._height))
        pygame.draw.rect(self._screen, self.curr_colour, btn_rect, 5)

    def update_activity(self) -> None:
        """Update self.is_active and assign self.curr_colour to a colour
        depending on whether it is True or False.
        Draw the text input box.
        """
        self.is_active = not self.is_active
        if self.is_active:
            self.curr_colour = self.colour_active
        else:
            self.curr_colour = self.colour_passive
        self.draw()

    def update_text(self) -> None:
        """Update the text in the rectangle representing the text input box with
        self.input_text and the self.text_colour.
        """
        text_bg = pygame.Rect((self.position[0] + 6, self.position[1] + 6), (self._width - 12, self._height - 12))
        pygame.draw.rect(self._screen, self.bg_colour, text_bg)
        text = self.font.render(self.input_text, True, self.text_colour)
        text_pos = (
            self.position[0] - text.get_width() / 2 + self._width / 2,
            self.position[1] - text.get_height() / 2 + self._height / 2
        )
        self._screen.blit(text, text_pos)


class AirDateFilterDisplay:
    screen: pygame.Surface
    height: Coord
    width: Coord
    position: Position
    section_title_font: pygame.font.Font
    input_box_start: TextInputBox
    input_box_end: TextInputBox
    selected_year: Optional[int]
    title_colour: Colour
    font_style: str

    def __init__(self, screen: pygame.Surface, height_percentage: float, pos_x_percentage: float, text_colour: Colour,
                 input_passive_colour: Colour, input_active_colour: Colour, bg_colour: Colour, title_colour: Colour,
                 font_style: str, border_colour: Colour) -> None:
        """Initialize a AirDateFilterDisplay object.
        """
        self.screen = screen
        self.height = screen.get_height() * height_percentage * 0.6
        self.width = screen.get_width() * 0.3
        self.position = (screen.get_width() * pos_x_percentage, 0)
        self.section_title_font = pygame.font.SysFont(font_style, 25, bold=False)
        self.input_box_bg_colour: Colour
        font = pygame.font.SysFont(font_style, int(screen.get_height() * 0.035), bold=False)
        input_box_pos_start = (self.position[0] + self.width / 3, self.height / 10)
        input_box_pos_end = (self.position[0] + self.width / 1.65 - 1, self.height / 10)
        self.input_box_start = TextInputBox(screen, self.height * 0.7, self.width * 0.2, input_box_pos_start,
                                            font, input_passive_colour, input_active_colour, text_colour, bg_colour,
                                            border_colour=border_colour)
        self.input_box_end = TextInputBox(screen, self.height * 0.7, self.width * 0.2, input_box_pos_end,
                                          font, input_passive_colour, input_active_colour, text_colour, bg_colour,
                                          border_colour=border_colour)
        self.selected_year = None
        self.title_colour = title_colour
        self.font_style = font_style

    def draw(self):
        # Draw section title
        title_1 = self.section_title_font.render('YEAR', True, self.title_colour)
        self.screen.blit(title_1, (self.position[0], self.height * 0.1))
        title_2 = self.section_title_font.render('RANGE', True, self.title_colour)
        self.screen.blit(title_2, (self.position[0], self.height * 0.1 + title_1.get_height() * 0.8 + 5))
        # Draw Input Box
        self.input_box_start.draw()
        font = pygame.font.SysFont(self.font_style, int(self.screen.get_height() * 0.04), bold=False)
        dash = font.render('-', True, self.title_colour)
        self.screen.blit(dash, (self.position[0] + self.width / 1.8, self.position[1] + self.height / 4 + 2))
        self.input_box_end.draw()

    def get_year_range(self) -> tuple[int, int]:
        start_year = self.input_box_start.input_text
        end_year = self.input_box_end.input_text
        if start_year == '' or end_year == '':
            return 1961, 2021
        elif not (1961 <= int(start_year) <= 2021) or not (1961 <= int(end_year) <= 2021):
            return 1961, 2021
        else:
            return int(start_year), int(end_year)


class Text:
    """ Add Text To Screen Class"""

    _size: int
    _text: str
    _x: Coord
    _y: Coord
    _bold: False

    def __init__(self, screen: pygame.surface, size: int, text: str, x: Coord, y: Coord, bold: Optional[bool] = False):
        self._size = size
        self._text = text
        self._x = x
        self._y = y
        self._bold = bold
        self._screen = screen

    def draw(self) -> None:
        font = pygame.font.SysFont("dm sans", self._size, bold=self._bold)
        txtsurf = font.render(self._text, True, (51, 51, 51))
        self._screen.blit(txtsurf, (self._x, self._y))


COLOR_INACTIVE = (217, 217, 217)
COLOR_ACTIVE = (46, 81, 162)


# FONT = pygame.font.Font(None, 32)

class InputBox2:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = pygame.font.Font(None, 32).render(text, False, self.color)
        self.active = False

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    rv = self.text
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    rv = None
                    self.text = self.text[:-1]
                else:
                    rv = None
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = pygame.font.Font(None, 32).render(self.text, True, (51, 51, 51))
                return rv

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


class DropDown2:
    """ Drow Down Button Class """

    def __init__(self, color_menu, color_option, x, y, w, h, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.main = main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
    python_ta.check_all(config={
        'extra-imports': ['pygame', 'math', 'anime_and_users'],
        'allowed-io': ['import_profile', 'save_profile'],
        'disable': ['too-many-nested-blocks', 'too-many-instance-attributes', 'too-many-arguments', 'E1101', 'E9997',
                    'E9970', 'E9971', 'C0115', 'C0116', 'E9972', 'E9992', 'R1710', 'C0325'],
        'max-line-length': 120
    })
