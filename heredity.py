import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])
    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    multi = 1

    for person in people.keys():
        parents = people[person]
        gene_number, is_trait = gene_trait(person, one_gene, two_genes, have_trait)

        if parents['father'] is None or parents['mother'] is None:
            gene_param = PROBS['gene'][gene_number]
            trait_param = PROBS['trait'][gene_number][is_trait]
        else:
            mother_param, _ = gene_trait(parents['mother'], one_gene, two_genes, have_trait)
            father_param, _ = gene_trait(parents['father'], one_gene, two_genes, have_trait)
            if gene_number == 0:
                gene_param = no_genes_from_parent(mother_param) * no_genes_from_parent(father_param)
            elif gene_number == 2:
                gene_param = one_gene_from_parent(mother_param) * one_gene_from_parent(father_param)
            else:
                gene_param = (one_gene_from_parent(mother_param) * no_genes_from_parent(father_param) +
                              one_gene_from_parent(father_param) * no_genes_from_parent(mother_param))

            trait_param = PROBS['trait'][gene_number][is_trait]
        probs = gene_param * trait_param
        multi *= probs
    return multi


def no_genes_from_parent(x):
    """
        Returns probability in which parent gives no genes to child,
        where parent has x genes.
    """
    mut = PROBS['mutation']
    return x / 2 * mut + (2 - x) / 2 * (1 - mut)


def one_gene_from_parent(x):
    """
       Returns probability in which parent gives one gene to child,
       where parent has x genes.
   """
    mut = PROBS['mutation']
    return x / 2 * (1 - mut) + (2 - x) / 2 * mut


def gene_trait(person, one_gene, two_genes, have_trait):
    """
    Returns gene_number (0, 1, 2) and is_trait (True, False),
    by checking presence of given person in sets.
    """
    if person in one_gene:
        gene_number = 1
    elif person in two_genes:
        gene_number = 2
    else:
        gene_number = 0

    if person in have_trait:
        is_trait = True
    else:
        is_trait = False

    return gene_number, is_trait


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities.keys():
        gene_number, is_trait = gene_trait(person, one_gene, two_genes, have_trait)
        probabilities[person]['gene'][gene_number] += p
        probabilities[person]['trait'][is_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities.keys():
        normalize_genes(probabilities, person)
        normalize_trait(probabilities, person)


def normalize_genes(probabilities, person):
    """
    Updates the probabilities dictionary.
    Normalizing 'gene' values.
    """
    x = probabilities[person]['gene'][0]
    y = probabilities[person]['gene'][1]
    z = probabilities[person]['gene'][2]

    probabilities[person]['gene'][0] *= 1 / (x + y + z)
    probabilities[person]['gene'][1] *= 1 / (x + y + z)
    probabilities[person]['gene'][2] *= 1 / (x + y + z)


def normalize_trait(probabilities, person):
    """
    Updates the probabilities dictionary.
    Normalizing 'trait' values.
    """
    x = probabilities[person]['trait'][True]
    y = probabilities[person]['trait'][False]

    probabilities[person]['trait'][True] *= 1 / (x + y)
    probabilities[person]['trait'][False] *= 1 / (x + y)


if __name__ == "__main__":
    main()
