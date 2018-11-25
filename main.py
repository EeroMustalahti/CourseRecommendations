import sys

from Scraper import Scraper
from Recommender import Recommender


def main():
    # Procedure to make course recommendations using content-based filtering

    # Commands to configure behaviour
    scrape_uta = sys.argv[1]  # Scrape website for courses and modules (y = yes, s = only Computer Science Program)
    scrape_student = sys.argv[2]
    recommend = sys.argv[3]  # Execute recommendation (y = yes, f = use fake student data)
    save_recommend = sys.argv[4]  # Save recommendations to file (y = yes)

    if scrape_uta == 'y':
        Scraper().scrape()
    elif scrape_uta == 's':
        Scraper().small_scrape()

    # Extract attributes from each course's HTML markup and make data structure containing course infos

    # Scrape student's NettiOpsu study record page to get HTML markup
    if scrape_student == 'y':
        Scraper().scrape_student()

    # Extract course IDs from HTML markup and make data structure containing ID's of passed courses

    # Recommend courses to student
    if recommend == 'y':
        Recommender().recommend(recommend, save_recommend)


if __name__ == "__main__":
    main()
