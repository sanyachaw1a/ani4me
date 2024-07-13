import calendar
import csv
import re
from typing import Any, List, Tuple

#when compiling from original data provided, follow the order below:
#recompile order: read_and_write_animes, read_and_write_profiles, read_and_write_reviews,
#                   write_anime_no_duplicates(), write_reviews_no_duplicates(), write_profiles_no_duplicates()
#                   , fix_inconsistent_users()

def read_uids() -> list:
    uids = []
    with open(f"uids_to_remove.csv", 'r') as reader:
        line = reader.readline()
        while line != '':
            uids.append(line[:-1])
            line = reader.readline()
    return uids

uids_to_remove = read_uids()
anime_uids_added = []
def vet_user(user: str):
    user = user.lower()
    keywords = ['nigger', 'nigga', 'retard', 'faggot', 'fag', 'pedo', 'racist', 'chink', 'fuck', 'bitch', 'whore',
                'skank', 'wanker', 'bastard', 'dyke', 'asshole', 'dick', 'lolicon', 'fap']
    return not any(keyword in user for keyword in keywords)


def read_and_write_reviews():
    big_lines = []
    # index 0 is uid, 1 is anime id, 2 is overall rating, and then the rest are the ratings for each category
    # (ex. {'Overall': '8', 'Story': '8', 'Animation': '8', 'Sound': '10', 'Character': '9', 'Enjoyment': '8'})
    with open(f"reviews(edited).csv", 'r',
              encoding="utf-8") as reader:
        line = reader.readline()
        line = line[:-9]
        counter = 0
        while line != '':
            # if you want up to a certain amount
            # while counter <= 50:
            lines = line.split(',')
            cond1 = lines[1] not in uids_to_remove
            cond2 = vet_user(lines[0])
            try:
                if (cond1 and cond2):
                    for i in range(3, 9):
                        lines[i] = re.search(r'\d+', lines[i]).group()

                    big_lines.append(lines)
            except AttributeError:
                pass

            line = reader.readline()
            line = line[:-9]
            # counter += 1
    # import pprint
    # pprint.pprint(big_lines)
    with open(f"formatted_reviews.csv", "w", newline='', encoding="utf-8") as f:
        w = csv.writer(f, delimiter=",")
        w.writerows(big_lines)


# don't limit the amount here
# people without reviews will still be in the csv file, they'll just only have a username
def read_and_write_profiles():
    big_lines = []
    # idx 1 username, idx 2 onwards favorite anime
    with open(f"profiles.csv", 'r', encoding="utf-8") as reader:
        line = reader.readline()

        while line != '':
            lines = line.split(',')
            cond2 = vet_user(lines[0])
            try:
                if (cond2):
                    for i in range(1, len(lines)):
                        if (lines[i] == '[]\n'):
                            lines[i] = ''
                        else:
                            lines[i] = re.search(r'\d+', lines[i]).group()
                        if (lines[i] in uids_to_remove or lines[i] not in anime_uids_added):
                            lines[i] = ''
                # removing blank indices
                stuff_to_remove = []
                for i in range(len(lines)):
                    if lines[i] == '':
                        stuff_to_remove.append(lines[i])
                while stuff_to_remove != []:
                    lines.remove(stuff_to_remove.pop())

                if (cond2):
                    big_lines.append(lines)
            except AttributeError:
                pass

            line = reader.readline()

    # import pprint
    # pprint.pprint(big_lines)
    with open(f"profiles_formatted.csv", "w", newline='', encoding="utf-8") as f:
        w = csv.writer(f, delimiter=",")
        w.writerows(big_lines)


# don't limit the amount here
def read_and_write_animes():
    # idx 1 is anime id, idx2 is title, next idxs are genres til dates, start dates first, end date second, last idx is
    # episodes
    big_lines = []
    with open(f"animes.csv", 'r', errors="ignore", encoding='utf-8') as reader:
        line = reader.readline()

        while line != '':
            lines = line.split(',')
            cond1 = lines[0] not in uids_to_remove

            try:
                if (cond1):
                    # fixing genres
                    anime_uids_added.append(lines[0])
                    i = 2
                    start_idx = 2
                    end_idx = 2
                    while "]" not in lines[i]:
                        end_idx += 1
                        i += 1

                    for j in range(start_idx, end_idx + 1):
                        genre = ''
                        for char in lines[j]:
                            if (char.isalpha()):
                                genre += char
                        lines[j] = genre

                    # i subtract 1 here to correct for index counting starting at 0
                    if len(lines) - end_idx - 1 != 4 or lines[end_idx + 4] == '\n' or lines[end_idx + 4] == '':
                        uids_to_remove.append(lines[0])
                        raise AttributeError
                    else:
                        months = {month: index for index, month in enumerate(calendar.month_abbr) if month}
                        start_date_numbers = re.findall(r'\b\d+\b', lines[end_idx + 1])
                        end_date_numbers = re.findall(r'\b\d+\b', lines[end_idx + 2])
                        if(len(end_date_numbers) != 2 or len(start_date_numbers) != 1):
                            uids_to_remove.append(lines[0])
                            raise AttributeError
                        start_date = str(months[lines[end_idx + 1][1:4]]) + '/' + start_date_numbers[0] \
                                     + '/' + end_date_numbers[0]
                        end_date = str(months[lines[end_idx + 2][9:12]]) + '/' + end_date_numbers[1] \
                                   + '/' + lines[end_idx + 3][1:5]

                        lines[end_idx + 4] = re.search(r'\d+', lines[end_idx + 4]).group()
                        lines[end_idx + 1] = start_date
                        lines[end_idx + 2] = end_date
                        lines.pop(end_idx + 3)

                    big_lines.append(lines)
            except AttributeError:
                pass

            # if (cond1):
            #     big_lines.append(lines)
            line = reader.readline()

    with open(f"animes_formatted.csv", "w", newline='', encoding="utf-8") as f:
        w = csv.writer(f, delimiter=",")
        w.writerows(big_lines)


def remove_anime_duplicates() -> list[tuple[str]]:
    """Removes the duplicate anime in the csv.

    Note:
    You have to return tuples here to avoid a hashing error when converting a nested list to a set
    """
    with open(f"animes_formatted.csv", 'r', errors="ignore",
              encoding='utf-8') as read_obj:
        csv_reader = csv.reader(read_obj)
        lst_of_csv = list(csv_reader)

    no_dupe_animes = list(set(tuple(anime) for anime in lst_of_csv))
    return no_dupe_animes


def write_anime_no_duplicates() -> None:
    """Write to a new file of the anime after having removed the duplicates"""
    animes = remove_anime_duplicates()
    with open(f"anime_formatted_no_duplicates.csv",
              'w', newline='',
              encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerows(animes)


# There shouldn't be any other problems but I'll leave this here in case
# def remove_user_no_reviews() -> list[list[str]]:
#     """Remove users without any reviews"""
#     with open(f"data/formatted/formatted_reviews.csv", 'r', errors="ignore") as read_obj:
#         csv_reader = csv.reader(read_obj)
#         lst_of_csv = list(csv_reader)
#
#     return lst_of_csv

def remove_review_duplicates() -> list[tuple[str]]:
    """Removes the duplicate reviews in the csv.
    Also removes reviews of anime called #NAME? (was probably some error in the csv when using excel)

    Note:
    You have to return tuples here to avoid a hashing error when converting a nested list to a set
    """
    with open(f"formatted_reviews.csv", 'r', errors="ignore") as read_obj:
        csv_reader = csv.reader(read_obj)
        lst_of_csv = list(csv_reader)

    no_dupe_reviews = list(set(tuple(review) for review in lst_of_csv))
    no_error_anime_name = [review for review in no_dupe_reviews if review[0] != "#NAME?"]
    return no_error_anime_name


def write_review_no_duplicates() -> None:
    """Write to a new file of the reviews after having removed the duplicates
    """
    reviews = remove_review_duplicates()
    with open(f"reviews_formatted_no_duplicates.csv",
              'w',
              newline='',
              encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerows(reviews)


def remove_user_duplicate() -> list[tuple[str]]:
    """Removes the duplicate users in the csv.
    Added: filtering users on their usernames with new keywords

    Note:
    You have to return tuples here to avoid a hashing error when converting a nested list to a set
    """
    with open(f"profiles_formatted.csv", 'r', errors="ignore") as read_obj:
        csv_reader = csv.reader(read_obj)
        lst_of_csv = list(csv_reader)

    no_dupe_profiles = list(set(tuple(profile) for profile in lst_of_csv if vet_user(profile[0])))
    return no_dupe_profiles


def write_profiles_no_duplicates() -> None:
    """Write to a new file of the profiles after having removed the duplicates
    """
    profiles = remove_user_duplicate()
    with open(f"profiles_formatted_no_duplicates.csv",
              'w',
              newline='',
              encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerows(profiles)


def fix_inconsistent_users() -> tuple[list[Any], list[Any]]:
    """Returns a tuple where index 0 and 1 are all reviews and profiles that have users that are both in the profiles
    and reviews data sets respectively
    """
    with open(f"reviews_formatted_no_duplicates.csv",
              'r',
              errors="ignore") as read_obj:
        csv_reader = csv.reader(read_obj)
        reviews = list(csv_reader)

    with open(f"profiles_formatted_no_duplicates.csv",
              'r',
              errors="ignore") as read_obj:
        csv_reader = csv.reader(read_obj)
        profiles = list(csv_reader)

    users_in_reviews = [user[0] for user in reviews]
    users_in_profiles = [user[0] for user in profiles]
    users_in_both = [user for user in users_in_profiles if user in users_in_reviews]

    consistent_reviews = [review for review in reviews if review[0] in users_in_both]
    consistent_profiles = [profile for profile in profiles if profile[0] in users_in_both]
    consistent_data = (consistent_reviews, consistent_profiles)

    return consistent_data


def write_consistent_users() -> None:
    """Rewrite the profiles and reviews excluding the reviews and profiles of users that aren't present in both data
    sets

    Also takes a while if you run it just be patient :)
    """
    consistent_data = fix_inconsistent_users()
    reviews, profiles = consistent_data[0], consistent_data[1]

    with open(f"profiles_formatted_no_duplicates.csv", 'w',
              newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerows(profiles)

    with open(f"reviews_formatted_no_duplicates.csv", 'w',
              newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerows(reviews)
