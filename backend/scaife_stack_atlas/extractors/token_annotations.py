import csv
import os

from django.conf import settings

from lxml import etree

from .constants import CRITO_VERSION_PART, PUNCTUATION_POSTAG, TREEBANK_PATH
from .lookups import POSTAG_LOOKUP, UNMAPPED_TAGS


# NOTE: Retrieve from POSTAG_LOOKUP
def _bail(tag):
    if tag in UNMAPPED_TAGS:
        return True
    return not tag


def _pos(tag):
    if _bail(tag):
        return ""
    return POSTAG_LOOKUP[tag]["part_of_speech"]


def _case(tag):
    if _bail(tag):
        return ""
    return POSTAG_LOOKUP[tag]["case"]


def _mood(tag):
    if _bail(tag):
        return ""
    return POSTAG_LOOKUP[tag]["mood"]


def transform_token(ref, pos, token):
    idx = pos + 1
    return {
        "ve_ref": f"{ref}.t{idx}",
        "value": token["value"],
        "word_value": token["form"],
        "lemma": token["lemma"],
        "gloss": token["gloss"],
        "part_of_speech": _pos(token["postag"]),
        "tag": token["postag"],
        "case": _case(token["postag"]),
        "mood": _mood(token["postag"]),
    }


def aldt_to_tokens(path):
    with open(path) as f:
        tree = etree.parse(f)

    all_tokens = []
    for sentence in tree.xpath("//sentence"):
        tokens = []
        prefix = None
        for pos, word in enumerate(sentence.xpath(".//word")):
            if word.attrib["postag"] == PUNCTUATION_POSTAG:
                if pos == 0:
                    prefix = word
                else:
                    prior_token = tokens[pos - 1]
                    prior_token[
                        "value"
                    ] = f'{prior_token["value"]}{word.attrib["form"]}'
                tokens.append({})
            else:
                data = {}
                data.update(word.attrib)
                data["value"] = data["form"]
                tokens.append(data)
        if prefix:
            first_token = tokens[1]
            first_token["value"] = f'{prefix.form}{prior_token["value"]}'
        ref = f'{sentence.attrib["subdoc"]}.{sentence.attrib["id"]}'
        tokens = [t for t in tokens if t]
        tokens = [transform_token(ref, pos, t) for pos, t in enumerate(tokens)]
        all_tokens.extend(tokens)
    return all_tokens


def write_token_annotations(path, tokens):
    with open(path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=list(tokens[0].keys()))
        writer.writeheader()
        for token in tokens:
            writer.writerow(token)


def create_token_annotations():
    """
    Extracts token annotations from the Crito treebank
    """
    tokens = aldt_to_tokens(TREEBANK_PATH)
    output_path = os.path.join(
        settings.SV_ATLAS_DATA_DIR,
        "annotations",
        "token-annotations",
        f"{CRITO_VERSION_PART}.csv",
    )
    write_token_annotations(output_path, tokens)
