"""
CSC111 Project: Anime and User classes

This module contains the classes and functions relevant to the User and Anime classes
and calculating the similarity score for Animes.

This file is Copyright (c) 2023 Hai Shi, Liam Alexander Maguire, Amelia Wu, and Sanya Chawla.
"""
from __future__ import annotations
import datetime
import re
from typing import Optional

import python_ta

import graph as g


class Anime:
    """A class representing a anime node in the ReccomenderTree

    Private Instance Attributes
    - title: the title of the anime
    - num_episodes: the number of episodes the anime has
    - genres: the genres of the anime
    - air_dates: the dates that the anime aired between
    - UID: the unique identifier for the anime
    - tags: the search tags for this anime
    Instance Attributes
    - reviews: the reviews for this anime
    Representation Invariants:
        - self._num_episodes > 0
        - (self.air_dates[1] - self.air_dates[0]).days > 0
        - len(self._tags) != 0
    """
    _title: str
    _num_episodes: int
    _genres: set[str]
    _air_dates: tuple[datetime.date, datetime.date]
    _uid: int
    reviews: dict[User, g.Review]
    _tags: set[str]

    def __init__(self, title: str, num_episodes: int, genres: set[str],
                 air_dates: tuple[datetime.date, datetime.date], uid: int) -> None:
        """Initialize a new anime
        Preconditions
            - (air_dates[1] - air_dates[0]).days > 0
            - num_episodes > 0
        """
        self._title = title
        self._num_episodes = num_episodes
        self._genres = genres
        self._air_dates = air_dates
        self._uid = uid
        self.reviews = {}
        self._tags = g.tag_keywords_and_strip(self._title)

    def get_num_episodes(self) -> int:
        """Returns the number of episodes of the anime"""
        return self._num_episodes

    def get_genres(self) -> set[str]:
        """Returns the genres of the anime"""
        return self._genres

    def get_uid(self) -> int:
        """Returns the UID of the anime"""
        return self._uid

    def get_title(self) -> str:
        """Returns the title of the anime"""
        return self._title

    def get_air_dates(self) -> tuple[datetime.date, datetime.date]:
        """Returns the air dates of the anime"""
        return self._air_dates

    def get_tags(self) -> set[str]:
        """Returns the search tags of the anime"""
        return self._tags

    def calculate_average_ratings(self) -> dict[str, float]:
        """Calculate the average ratings for this anime over all of its reviews.
        """
        if self.reviews == {}:
            return {'story': 0, 'animation': 0, 'sound': 0, 'character': 0, 'enjoyment': 0, 'overall': 0}
        ratings_dict = {'story': 0, 'animation': 0, 'sound': 0, 'character': 0, 'enjoyment': 0, 'overall': 0}
        for review in self.reviews:
            for key in self.reviews[review].ratings:
                ratings_dict[key] += self.reviews[review].ratings[key]

        return {section: round(ratings_dict[section] / len(self.reviews), 2) for section in ratings_dict}

    def get_all_path_scores_helper(self, depth: int, visited_nodes: list[Anime | User],
                                   added_ends: list[Anime | User]) -> list[list[g.Review]]:
        """Helper function for get_all_path_scores that calculates all the paths
        """
        # NOTE: you can optionally change the depth to 5 to get much more reccomendations,
        # but it takes more than 1 minute to calculate
        if depth == 3 or len(self.reviews) == 1:
            visited_reviews = []
            visited_path = []
            if visited_nodes[-1] not in added_ends and visited_nodes[-2] not in added_ends:
                if visited_nodes[-1].__class__.__name__ == 'Anime':
                    added_ends.append(visited_nodes[-1])
                elif visited_nodes[-2].__class__.__name__ == 'Anime':
                    added_ends.append(visited_nodes[-2])
                for i in range(0, len(visited_nodes) - 1, 2):
                    visited_reviews.append(visited_nodes[i].reviews[visited_nodes[i + 1]])
                visited_path.append(visited_reviews)
            return visited_path
        else:
            all_paths = []
            for opposite_endp in self.reviews:
                if opposite_endp not in visited_nodes:
                    visited_nodes.append(self)
                    visited_nodes.append(opposite_endp)
                    rec = opposite_endp.get_all_path_scores_helper(depth + 1, visited_nodes, added_ends)
                    visited_nodes.pop()
                    visited_nodes.pop()
                    if rec != [] and rec is not None:
                        all_paths.extend(rec)
            return all_paths


class User:
    """A class representing a user node in the ReccomenderTree
    Instance Attributes:
    - Username: the user's username
    - reviews: the reviews that the User has made
    - favorite_animes: the UIDS of the user's favorite animes
    - friends_list: the uid of the user's friends
    - priorities: how much the user values each aspect of an anime
    - weights: the weights of each priority
    - favorite_era: the user's favorite era of anime
    Representation Invariants:
        - all(0 <= priorities[priority] <= 10 for priority in priorities)
        - len(self.priorities) == 5
        - len(self.favorite_animes) > 0 or len(self.reviews) > 0
    """
    username: str
    reviews: dict[Anime, g.Review]
    favorite_animes: set[Anime]
    matching_genres: set[str]
    friends_list: list[User]
    priorities: dict[str, int]
    weights: dict[str, float]
    favorite_era: tuple[datetime.date, datetime.date]

    def __init__(self, username: str, fav_animes: set[Anime],
                 favorite_era: Optional[tuple[datetime.date, datetime.date]] = None,
                 review: Optional[dict[Anime, list[int]]] = None, priority: Optional[dict[str, int]] = None,
                 friend_list: Optional[list[User]] = None) -> None:
        """intialize a new user and calculate their priority weights
        Preconditions:
            - (favorite era[1] - favorite_era[0]).days > 0
            - all(priority[p] >= 0 for p in priority)
            - all(all(rating >= 0 for rating in review[anime]) for anime in review
            - len({anime for anime in review}) == len(review)
            - len(set(friend_list)) == len(friend_list)
            - Every anime in fav_animes exists in the ReccomenderGraph the user will be added into
            - Every anime in review exists in the ReccomenderGraph the user will be added into
            - Every user in friend_list exists in the ReccomenderGraph the user will be added to
        """
        self.username = username
        self.favorite_animes = fav_animes
        if friend_list is None:
            self.friends_list = []
        else:
            self.friends_list = friend_list
        if favorite_era is None:
            self.favorite_era = tuple()
        else:
            self.favorite_era = favorite_era

        self.reviews = {}
        if review is not None:
            for anime in review:
                g.Review(self, anime, {'story': review[anime][0], 'animation': review[anime][1],
                                       'sound': review[anime][2], 'character': review[anime][3],
                                       'enjoyment': review[anime][4], 'overall': review[anime][5]})

        self.priorities = {}
        self.matching_genres = set()
        self.weights = {}
        if priority is not None:
            self.priorities = priority
            self.calculate_genre_match_avg()
            self.calculate_priority_weights()

    def get_all_path_scores_helper(self, depth: int, visited_nodes: list[Anime | User],
                                   added_ends: list[Anime | User]) -> list[list[g.Review]]:
        """Helper function for get_all_path_scores that calculates all the paths
        """
        # NOTE: you can optionally change the depth to 5 to get much more reccomendations,
        # but it takes more than 1 minute to calculate
        if depth == 3:
            visited_reviews = []
            visited_path = []
            if len(visited_nodes) > 2 and visited_nodes[-1] not in added_ends and visited_nodes[-2] not in added_ends:
                if visited_nodes[-1].__class__.__name__ == 'Anime':
                    added_ends.append(visited_nodes[-1])
                elif visited_nodes[-2].__class__.__name__ == 'Anime':
                    added_ends.append(visited_nodes[-2])
                for i in range(0, len(visited_nodes) - 1, 2):
                    visited_reviews.append(visited_nodes[i].reviews[visited_nodes[i + 1]])
                visited_path.append(visited_reviews)
            return visited_path
        else:
            all_paths = []
            for opposite_endp in self.reviews:
                if opposite_endp not in visited_nodes:
                    visited_nodes.append(self)
                    visited_nodes.append(opposite_endp)
                    rec = opposite_endp.get_all_path_scores_helper(depth + 1, visited_nodes, added_ends)
                    visited_nodes.pop()
                    visited_nodes.pop()
                    if rec != [] and rec is not None:
                        all_paths.extend(rec)
            return all_paths

    def calculate_genre_match_avg(self) -> None:
        """Calculate the genres in at least 50% of the anime across the user's favorite anime and reviews with a overall
        rating higher than 4
        Preconditions:
            - self.favorite_animes != set() or self.reviews != {}
        """
        animes = self.favorite_animes.union({ani for ani in self.reviews
                                             if self.reviews[ani].ratings['overall'] > 4})
        genres_count = {}
        episodes_count = 0

        for anime in animes:
            episodes_count += anime.get_num_episodes()
            for genre in anime.get_genres():
                if genre not in genres_count:
                    genres_count[genre] = 1
                else:
                    genres_count[genre] += 1

        self.matching_genres = {re.sub('[^a-zA-Z]+', '', gen) for gen in genres_count if
                                genres_count[gen] >= int(len(animes) / 2)}
        self.priorities['num-episodes'] = int(episodes_count / len(animes))

    def calculate_priority_weights(self) -> None:
        """Calculate the priority weights for each category in priority except for num_episodes
        """
        total = sum(self.priorities.values()) - self.priorities['num-episodes']
        for priority in self.priorities:
            if priority not in ('num-episodes', 'overall', 'enjoyment'):
                self.weights[priority] = self.priorities[priority] / total

    def calculate_similarity_rating(self, anime: Anime) -> float:
        """Calculate a similarity rating between 1 and 10 to give a prediction for how much the user will like the anime
        Preconditions:
            - anime must be a valid Anime object
        """
        anime_avg_ratings = anime.calculate_average_ratings()
        weighted_avg = sum([self.weights[key] * anime_avg_ratings[key] for key in self.priorities if
                            key not in ('num-episodes', 'overall', 'enjoyment')]) / 10

        overlap_start_date = max(self.favorite_era[0], anime.get_air_dates()[0])
        overlap_end_date = min(self.favorite_era[1], anime.get_air_dates()[1])
        date_overlap_delta = max((overlap_end_date - overlap_start_date).days + 1, 0)
        user_era_length = (self.favorite_era[1] - self.favorite_era[0]).days + 1
        date_score = round(date_overlap_delta / user_era_length, 2)

        shared_members = len(self.matching_genres.intersection(anime.get_genres()))
        total_members = len(self.matching_genres.union(anime.get_genres()))
        genre_match_index = round(shared_members / total_members, 2)

        episode_rating = round(self.calculate_episode_rating(anime), 2)

        return round((0.5 * weighted_avg + 0.3 * genre_match_index + 0.1 * episode_rating + 0.1 * date_score), 2) * 10

    def calculate_episode_rating(self, anime: Anime) -> float:
        """Calulcates a normalized score for the number of standard deviations an anime is away from the
        users avereage length.
        Preconditions
            - anime must be a valid Anime object
            - self.priorities['num-episodes] > 0
        """
        stddev = 39.64
        mid = self.priorities['num-episodes']
        # NOTE: the numbers 1 and 773 come from the minimum and maximum of the episode counts (excluding outliers)
        # and the standard deviation was calulated with the outliers removed
        # outliers were animes with id [6277, 23349, 2471, 32448, 22221, 12393, 8213, 10241]
        max_std_deviations_l = (mid - 1) / stddev
        max_std_deviations_r = (773 - mid) / stddev

        if anime.get_num_episodes() < mid:
            deviations_distance = (mid - anime.get_num_episodes()) / stddev
            return 1 - (deviations_distance / max_std_deviations_l)
        else:
            deviations_distance = (anime.get_num_episodes() - mid) / stddev
            return 1 - (deviations_distance / max_std_deviations_r)

    def reccomend_based_on_friends(self) -> list:
        """Reccomend anime based on what the user's friends have watched. If the user has no friends, returns an empty
        list.
        """
        already_watched = self.favorite_animes.union(self.reviews.keys())
        animes_to_rank = set()
        scores = {}
        for friend in self.friends_list:
            friend_watched = friend.favorite_animes.union(friend.reviews.keys())
            animes_to_rank = animes_to_rank.union(friend_watched.difference(already_watched))

        for anime in animes_to_rank:
            scores[anime] = self.calculate_similarity_rating(anime)

        sorted_values = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_values) < 10:
            return sorted_values
        else:
            return sorted_values[0:10]


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)
    python_ta.check_all(config={
        'extra-imports': ['graph', 'typing', 'datetime', 're'],
        'allowed-io': ['import_profile', 'save_profile'],
        'disable': ['too-many-nested-blocks', 'too-many-instance-attributes', 'too-many-arguments'],
        'max-line-length': 120
    })
    # date1 = datetime.date(2000, 10, 1)
    # date2 = datetime.date(2005, 10, 1)
    a = g.read_file([
        'anime_formatted_no_duplicates.csv',
        'profiles_formatted_no_duplicates.csv',
        'reviews_formatted_no_duplicates.csv'])

    g.import_profile('alan.csv', a)
    d = a.users['alan']
