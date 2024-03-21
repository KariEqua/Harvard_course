import os
import random
import re
import sys
from collections import Counter

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]: .4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]: .4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    page_probs = {}
    n = len(corpus)
    page_value = corpus[page]
    num_links = len(page_value)
    for key, value in corpus.items():
        if key in page_value:
            page_probs[key] = (1 - damping_factor) / n + damping_factor / num_links
        else:
            page_probs[key] = (1 - damping_factor) / n
    return page_probs


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank_dict = {}
    key_list = list(corpus.keys())
    samples = [random.choice(key_list)]
    for i in range(n-1):
        # chose next sample site using transition_model
        page_probs = transition_model(corpus, samples[-1], damping_factor)
        probs = list(page_probs.values())
        weights = [int(prob * 100) for prob in probs]
        pages = list(page_probs.keys())
        samples.append(random.choices(pages, weights=weights, k=1)[0])
    count_samples = Counter(samples)
    for key, value in corpus.items():
        pagerank_dict[key] = count_samples[key] / n

    return pagerank_dict


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    n = len(corpus)
    value = 1 / n
    pagerank_dict = {key: value for key in corpus}
    page_list = list(pagerank_dict.keys())
    while True:
        max_change = 0
        for key, value in pagerank_dict.items():
            pagerank_sum = 0
            for corpus_key, corpus_value in corpus.items():
                num_links = len(corpus_value)
                if num_links == 0:
                    corpus_value = page_list
                    num_links = n
                if key not in corpus_value:
                    continue
                pagerank_sum += pagerank_dict[corpus_key] / num_links
            new_pagerank = (1 - damping_factor) / n + damping_factor * pagerank_sum
            pagerank_change = abs(value - new_pagerank)
            pagerank_dict[key] = new_pagerank
            max_change = max(max_change, pagerank_change)
        if max_change <= 0.001:
            break

    return pagerank_dict


if __name__ == "__main__":
    main()
