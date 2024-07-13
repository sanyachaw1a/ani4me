"""
CSC111 Project: Review and ReccomenderGraph classes

This module contains the classes and functions relevant to creating and loading a reccomender tree and saving
and writing user profiles.

This file is Copyright (c) 2023 Hai Shi, Liam Alexander Maguire, Amelia Wu, and Sanya Chawla.
"""
from __future__ import annotations
import datetime
import re

import python_ta

import anime_and_users as aau


class Review:
    """An edge that connects a user and an anime which contains the ratings the user gave

    Instance Attributes
    - endpoints: The two nodes linked by this review
    - ratings: the ratings that the user gave for the individual categories
    Representation invariants:
         - all(0 <= self.ratings[rating] <= 10 for rating in self.ratings)
    """
    endpoints: tuple[aau.User, aau.Anime]
    ratings: dict[str, int]

    def __init__(self, e1: aau.User, e2: aau.Anime, ratings: dict[str, int]) -> None:
        """Add a review and connect the two endpoints
        Preconditions:
            - user and anime both need to exist in the ReccomenderGraph
            - the user and anime cannot be previously linked
        """
        self.ratings = ratings
        self.endpoints = (e1, e2)
        e1.reviews[e2] = self
        e2.reviews[e1] = self


class ReccomenderGraph:
    """A class for a graph of nodes, where the nodes are users and animes, and edges are reviews

    Instance Attributes
    - users: a list of user nodes
    - animes: a list of anime nodes
    """
    users: dict[str, aau.User]
    animes: dict[int, aau.Anime]

    def __init__(self) -> None:
        """initialize an empty ReccomenderGraph
        """
        self.users = {}
        self.animes = {}

    def insert_user(self, user: aau.User) -> None:
        """Add a user into the graph
        Preconditions:
            - user is a valid User object
            - user.username not in a.users
        """
        self.users[user.username] = user

    def insert_anime(self, anime: aau.Anime) -> None:
        """Add an anime into the graph
        Preconditions:
            - anime is a valid Anime object
            - anime.get_title not in a.animes
        """
        self.animes[anime.get_uid()] = anime

    def add_friends(self, user: str, friend_user: str) -> None:
        """Connect this user and the friend_user together
        Preconditions:
            - user in self.users and friend_user in self.users
        """
        self.users[user].friends_list.append(self.users[friend_user])
        self.users[friend_user].friends_list.append(self.users[user])

    def get_all_path_scores(self, user: aau.User) -> list[tuple[aau.Anime, float]]:
        """Find all anime at a path length of 3 and calculate a path score for each anime based on
        the reviews given to it and the user's priorities, and returns the anime with the top 10 path scores
        Preconditions:
            - user in self.users
        """
        watched_animes = user.favorite_animes.union(set(user.reviews))
        paths = [pa for pa in user.get_all_path_scores_helper(0, [], list(watched_animes)) if len(pa) > 2]
        scores = []
        for path in paths:
            scores.append((path[-1].endpoints[1], self.calculate_path_score(path, user)))

        scores_sorted = sorted(scores, key=lambda x: x[1], reverse=True)[0:10]
        if len(scores_sorted) < 10:
            return scores_sorted
        else:
            return scores_sorted[0:10]

    def calculate_path_score(self, path: list[Review], user: aau.User) -> float:
        """Helper function for get_all_path_scores that calculates the path score for the given path
        Preconditions:
            - user in self.users
            - all(review.endpoints[0] in self.users and review.endpoints[1] in self.animes for review in path
        """

        anime = path[-1].endpoints[1]
        sim_rating = user.calculate_similarity_rating(anime)
        review_sums = {'story': 0, 'animation': 0, 'sound': 0, 'character': 0, 'enjoyment': 0, 'overall': 0}

        for i in range(1, len(path)):
            for rating in path[i].ratings:
                review_sums[rating] += path[i].ratings[rating]
        review_averages = {category: review_sums[category] / (len(path) - 1) for category in review_sums}
        user_review = {category: review_sums[category] / (len(path) - 1) for category in path[0].ratings}
        weighted_avg = sum([user.weights[key] * review_averages[key] for key in user.priorities if
                            key not in ('num-episodes', 'overall', 'enjoyment')])
        user_review_avg = sum([user.weights[key] * user_review[key] for key in user.priorities if
                               key not in ('num-episodes', 'overall', 'enjoyment')])
        total_avg = ((weighted_avg * 0.5 + review_averages['overall'] * 0.1 + review_averages['enjoyment'] * 0.1
                      + user_review_avg * 0.2 + ((user_review['overall'] + user_review['enjoyment']) / 2) * 0.1)
                     + sim_rating) / 2
        return total_avg


def tag_keywords_and_strip(query: str) -> set[str]:
    """Takes a query for an anime and simplfies it into its keywords, with only
    alphanumeric characters and all lowercase
    Preconditions:
            - len(query) > 0
            - len(re.sub('[^0-9a-zA-z@]+', ' ', query)) > 0
            - any(word not in connecting_words for word in re.sub('[^0-9a-zA-z@]+', ' ', query).split(' '))
    """
    query_cleaned = re.sub('[^0-9a-zA-z@]+', ' ', query)
    query_keywords = query_cleaned.split(' ')
    connecting_words = ['in', 'the', 'and', 'wa', 'no', 'of', 'to', 'ova', 'kun', 'a']
    cleaned_query_keywords = set()
    for keyword in query_keywords:
        if keyword.lower() in connecting_words or keyword in ('', '\n'):
            pass
        else:
            cleaned_query_keywords.add(keyword.lower())

    return cleaned_query_keywords


def search(query: str, graph: ReccomenderGraph) -> dict[str, aau.Anime]:
    """Searches for all animes in a ReccomenderGraph with at least a 33% keyword match and returns them.
    Preconditions:
            - query is spelled correctly
            - graph is a valid ReccomenderGraph
    """
    search_res = []
    query_tags = tag_keywords_and_strip(query)
    searched = False
    search_res_dict = {}
    try:
        for anime in graph.animes:
            anime_tags = graph.animes[anime].get_tags()
            if len(anime_tags) < len(query_tags):
                if len(query_tags.intersection(anime_tags)) == len(anime_tags):
                    search_res.append((graph.animes[anime], len(query_tags.intersection(anime_tags)) / len(query_tags)))
                    searched = True
            if not searched:
                if len(query_tags.intersection(anime_tags)) / len(query_tags) >= 0.5:
                    search_res.append((graph.animes[anime], len(query_tags.intersection(anime_tags)) / len(query_tags)))
            searched = False
    except ZeroDivisionError:
        print('Invalid query (your query must have alphanumeric characters and must not only contain common words '
              'such as or, and). Please enter a valid query and try again.')

    search_res = sorted(search_res, key=lambda x: x[1], reverse=True)
    for item in search_res:
        search_res_dict[f'{item[0].get_title()}, {item[0].get_uid()}'] = item[0]

    return search_res_dict


def read_file(files: list[str]) -> ReccomenderGraph:
    """Creates a ReccomenderGraph given the animes. profiles, and reviews formatted in a CSV file in the format:
    Reviews:
        index 0 is uid, 1 is anime id, 2 is overall rating, and then the rest are the ratings for each category
        (ex. {'Overall': '8', 'Story': '8', 'Animation': '8', 'Sound': '10', 'Character': '9', 'Enjoyment': '8'})
    Profiles:
        index 1 username, index 2 onwards favorite anime
    Anime:
        index 1 is id, index 2 is title, next idxs are genres until dates,
        start dates first index after, end date second index after, last index is number of episodes
    Preconditions:
            - files are formatted correctly in the specified format
            - files[0] is the anime file, files[1] is the user file, files[2] is the reviews file
    """
    graph = ReccomenderGraph()
    with open(files[0], 'r',
              encoding="utf-8") as reader:
        line = reader.readline()

        while line != '':
            lines = line.split(',')
            anime_id = lines[0]
            title = lines[1]
            genres = set()
            i = 2
            while all(char.isalpha() for char in lines[i]):
                genres.add(lines[i])
                i += 1

            start_date = datetime.datetime.strptime(lines[i], '%m/%d/%Y').date()
            end_date = datetime.datetime.strptime(lines[i + 1], '%m/%d/%Y').date()
            num_episodes = int(lines[i + 2])
            graph.insert_anime(aau.Anime(title, num_episodes, genres, (start_date, end_date), int(anime_id)))
            line = reader.readline()

    with open(files[1], 'r',
              encoding="utf-8") as reader:
        line = reader.readline()

        while line != '':
            lines = line.split(',')
            if lines[0][-1] == '\n':
                username = lines[0][0:len(lines[0]) - 1]
            else:
                username = lines[0]
            favorite_animes = set()
            for i in range(1, len(lines)):
                favorite_animes.add(graph.animes[int(lines[i])])

            graph.insert_user(aau.User(username=username, fav_animes=favorite_animes))
            line = reader.readline()

    with open(files[2], 'r',
              encoding="utf-8") as reader:
        line = reader.readline()

        while line != '':
            lines = line.split(',')
            user = graph.users[lines[0]]
            anime = graph.animes[int(lines[1])]
            ratings = {'story': int(lines[4]), 'animation': int(lines[5]), 'sound': int(lines[6]),
                       'character': int(lines[7]), 'overall': int(lines[3]), 'enjoyment': int(lines[8])}
            Review(user, anime, ratings)
            line = reader.readline()

    return graph


def import_profile(file: str, graph: ReccomenderGraph) -> aau.User:
    """loads a user from a csv file and adds them into the graph
    Preconditions:
        - files are formatted correctly
        - user not in graph.users.keys()
        - every anime in the user csv file exists in graph
        - avery user in the friends_list exists in graph
    """
    with open(file, 'r', encoding='utf-8') as reader:
        line = reader.readline()
        username = line.split(',')[0]

        line = reader.readline()
        animes_id = line.split(',')[0:-1]
        favorite_animes = set()
        for anime in animes_id:
            favorite_animes.add(graph.animes[int(anime)])

        line = reader.readline()
        friends_user = line.split(',')[0:-1]
        friends = []
        for user in friends_user:
            friends.append(graph.users[user])

        line = reader.readline()
        lines = line.split(',')
        date1 = datetime.datetime.strptime(lines[0], '%m/%d/%Y').date()
        date2 = datetime.datetime.strptime(lines[1], '%m/%d/%Y').date()

        line = reader.readline()
        lines = line.split(',')
        priority = {'story': int(lines[0]), 'animation': int(lines[1]), 'sound': int(lines[2]),
                    'character': int(lines[3])}

        line = reader.readline()
        reviews = {}
        while line != '':
            lines = line.split(',')
            ratings_int = []
            for k in range(1, len(lines)):
                ratings_int.append(int(lines[k]))

            reviews[graph.animes[int(lines[0])]] = ratings_int
            line = reader.readline()
        u = aau.User(username, favorite_animes, (date1, date2), reviews, priority, friends)
        graph.insert_user(u)
        return u


def import_profile_to_user(file: str, graph: ReccomenderGraph) -> aau.User:
    """loads a user from a csv file and adds them into the graph
    Preconditions:
        - files are formatted correctly
        - user not in graph.users.keys()
        - every anime in the user csv file exists in graph
        - avery user in the friends_list exists in graph
    """
    with open(file, 'r', encoding='utf-8') as reader:
        line = reader.readline()
        username = line.split(',')[0]

        line = reader.readline()
        animes_id = line.split(',')[0:-1]
        favorite_animes = set()
        for anime in animes_id:
            favorite_animes.add(graph.animes[int(anime)])

        line = reader.readline()
        if line != '' or line != '\n':
            friends_user = line.split(',')[0:-1]
            friends = []
            for user in friends_user:
                friends.append(graph.users[user])
        else:
            friends = None

        line = reader.readline()
        if line != '' or line != '\n':
            lines = line.split(',')
            date1 = datetime.datetime.strptime(lines[0], '%m/%d/%Y').date()
            date2 = datetime.datetime.strptime(lines[1], '%m/%d/%Y').date()
            date = (date1, date2)
        else:
            date = None

        line = reader.readline()
        if line != '' or line != '\n':
            lines = line.split(',')
            priority = {'story': int(lines[0]), 'animation': int(lines[1]), 'sound': int(lines[2]),
                        'character': int(lines[3])}
        else:
            priority = None

        line = reader.readline()
        if line != '' or line != '\n':
            reviews = {}
            while line != '':
                lines = line.split(',')
                ratings_int = []
                for k in range(1, len(lines)):
                    ratings_int.append(int(lines[k]))

                reviews[graph.animes[int(lines[0])]] = ratings_int
                line = reader.readline()
        else:
            reviews = None

        user = aau.User(username, favorite_animes, date, reviews, priority, friends)
        return user


def save_profile(user: aau.User, file_name: str) -> None:
    """save the user's profile into a csv file
    Preconditions:
        - user is a valid User object
    """
    with open(file_name, 'w', encoding='utf-8') as writer:
        writer.write(f"{user.username},\n")

        for anime in user.favorite_animes:
            writer.write(f"{str(anime.get_uid())},")
        writer.write('\n')

        for friend in user.friends_list:
            writer.write(f"{friend.username},")
        writer.write('\n')

        writer.write(f"{user.favorite_era[0].month}/{user.favorite_era[0].day}/{user.favorite_era[0].year},")
        writer.write(f"{user.favorite_era[1].month}/{user.favorite_era[1].day}/{user.favorite_era[1].year},\n")

        writer.write(f"{user.priorities['story']},{user.priorities['animation']},{user.priorities['sound']},"
                     f"{user.priorities['character']}\n")

        for review in user.reviews:
            rating = user.reviews[review].ratings
            writer.write(f"{review.get_uid()},{rating['story']},{rating['animation']},{rating['sound']},"
                         f"{rating['character']},{rating['enjoyment']},{rating['overall']}\n")


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)
    python_ta.check_all(config={
        'extra-imports': ['anime_and_users', 'datetime', 're'],
        'allowed-io': ['import_profile', 'save_profile', 'read_file', 'search', 'import_profile_to_user'],
        'disable': ['too-many-nested-blocks', 'too-many-locals'],
        'max-line-length': 120
    })
