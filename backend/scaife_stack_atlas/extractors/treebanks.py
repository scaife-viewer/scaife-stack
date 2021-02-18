import json
import os

from django.conf import settings

from lxml import etree

from .constants import CRITO_VERSION_PART, TREEBANK_PATH


def transform_headwords(words):
    inbounds = set(w["id"] for w in words)
    for word in words:
        if word["head_id"] not in inbounds:
            word["original_head_id"] = word["head_id"]
            word["head_id"] = 0
    return words


def create_syntax_tree_annotation():
    exemplar = "0059-003"
    with open(TREEBANK_PATH) as f:
        tree = etree.parse(f)
    version = f"urn:cts:greekLit:{CRITO_VERSION_PART}:"
    to_create = []
    for sentence in tree.xpath("//sentence"):
        sentence_id = sentence.attrib["id"]
        sentence_obj = {
            "urn": f'urn:cite2:pedalion:syntaxTree.v1:syntaxTree-{exemplar}-{sentence.attrib["id"]}',
            "treebank_id": sentence_id,
            "words": [],
        }
        for word in sentence.xpath(".//word"):
            id_val = int(word.attrib["id"])
            head_val = int(word.attrib["head"])

            word_obj = {
                "id": id_val,
                "gloss": word.attrib.get("gloss", ""),
                "value": word.attrib["form"],
                "head_id": head_val,
                "relation": word.attrib["relation"],
                "lemma": word.attrib.get("lemma", ""),
                "tag": word.attrib.get("postag", ""),
            }

            sentence_obj["words"].append(word_obj)

        sentence_obj["words"] = transform_headwords(sentence_obj["words"])
        # NOTE: We assume a 1:1 relationship between sentences and text parts at this time
        ref = f'{sentence.attrib["subdoc"]}.{sentence.attrib["id"]}'
        sentence_obj["references"] = [f"{version}{ref}"]

        subdoc = sentence.attrib.get("subdoc")
        if subdoc:
            citation = f"{subdoc} ({sentence_id})"
        else:
            citation = f"({sentence_id})"
        sentence_obj["citation"] = citation
        to_create.append(sentence_obj)

    version_part = version.rsplit(":")[-2]
    output_path = os.path.join(
        settings.SV_ATLAS_DATA_DIR,
        "annotations",
        "syntax-trees",
        f"syntax_trees_{version_part}.json",
    )
    json.dump(
        to_create, open(output_path, "w"), ensure_ascii=False, indent=2,
    )
