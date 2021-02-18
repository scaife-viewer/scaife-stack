import os

from django.conf import settings

from lxml import etree

from .constants import CRITO_VERSION_PART, PUNCTUATION_POSTAG, TREEBANK_PATH


def aldt_to_textparts(path):
    with open(path) as f:
        tree = etree.parse(f)

    text_parts = []
    for sentence in tree.xpath("//sentence"):
        words = []
        prefix = None
        for pos, word in enumerate(sentence.xpath(".//word")):
            if word.attrib["postag"] == PUNCTUATION_POSTAG:
                if pos == 0:
                    prefix = f'{word.attrib["form"]}'
                else:
                    words[pos - 1] = f'{words[pos-1]}{word.attrib["form"]}'
                words.append("")
            else:
                words.append(word.attrib["form"])
        if prefix:
            words[1] = f"{prefix}{words[1]}"
        ref = f'{sentence.attrib["subdoc"]}.{sentence.attrib["id"]}'
        text_parts.append((ref, " ".join(w for w in words if w)))
    return text_parts


def write_textparts(path, text_parts):
    with open(path, "w") as f:
        for text_part in text_parts:
            f.write(" ".join(text_part))
            f.write("\n")


def create_version():
    """
    Extracts refs and text parts from the Crito treebank
    """
    text_parts = aldt_to_textparts(TREEBANK_PATH)
    output_path = os.path.join(
        settings.SV_ATLAS_DATA_DIR,
        "library",
        "tlg0059",
        "tlg003",
        f"{CRITO_VERSION_PART}.txt",
    )

    write_textparts(output_path, text_parts)
