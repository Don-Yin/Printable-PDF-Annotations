import math
from pathlib import Path

import fitz
from fitz.utils import getColor


def make_printable_annot_wise(page: fitz.Page, annot: fitz.Annot, init_empty_margin_rect: fitz.Rect):
    # ----find nearest vertices to the upper right corner of the page----
    vertices_distance = [{"coords": i, "distance": math.dist(i, (page.rect[2], 0))} for i in annot.vertices]
    vertices_distance.sort(key=lambda x: x["distance"])
    coords_right_upper_annot = vertices_distance[0]["coords"]

    # ----find rects of the words rightward of the annot----
    rects_right_words = [i for i in page.get_text("words") if i[0] > coords_right_upper_annot[0]]
    left_x_right_words = [int(i[0]) for i in rects_right_words]

    # ----find the leftmost word of the second column----
    try:
        x_coord_right_column = max(left_x_right_words, key=left_x_right_words.count)
    except ValueError:  # if there is no second column
        x_coord_right_column = None

    # ----coordinates of the initial words of the second column----
    init_words_right_column = [i for i in rects_right_words if int(i[0]) == x_coord_right_column]

    # ----detect whether there are any words in the right margin area
    words_in_margin = page.get_text("words", clip=init_empty_margin_rect)
    if words_in_margin:
        note_area_rect = init_empty_margin_rect + (0, max([i[3] for i in words_in_margin]), 0, 0)
    else:
        note_area_rect = init_empty_margin_rect

    # ----add padding----
    note_area_rect += (24, 24, -24, -24)

    # ----add annotation to right margin----
    annot_ = page.add_freetext_annot(
        rect=note_area_rect,
        text=annot.info["content"],
        fontsize=12,
        fontname="helv",
        border_color=None,
        text_color=getColor("black"),
        fill_color=None,
        rotate=0,
        align=fitz.TEXT_ALIGN_LEFT,
    )

    annot_.update()

    distances = [
        {"word": i, "product_distance": abs(math.dist(i[:2], coords_right_upper_annot) - math.dist(i[:2], note_area_rect[:2]))}
        for i in init_words_right_column
    ]
    distances.sort(key=lambda x: x["product_distance"])

    if x_coord_right_column:
        annot_ = page.add_line_annot(p1=coords_right_upper_annot, p2=distances[0]["word"][:2])
        annot_.set_colors({"stroke": annot.colors["stroke"], "fill": annot.colors["stroke"]})
        annot_.update()

        annot_ = page.add_line_annot(p1=distances[0]["word"][:2], p2=(init_empty_margin_rect[0], distances[0]["word"][1]))
        annot_.set_colors({"stroke": annot.colors["stroke"], "fill": annot.colors["stroke"]})
        annot_.update()

        annot_ = page.add_line_annot(p1=(init_empty_margin_rect[0], distances[0]["word"][1]), p2=note_area_rect[:2])
        annot_.set_colors({"stroke": annot.colors["stroke"], "fill": annot.colors["stroke"]})
        annot_.update()

        annot_ = page.add_line_annot(p1=note_area_rect[:2], p2=(note_area_rect[0] + 24, note_area_rect[1]))
        annot_.set_colors({"stroke": annot.colors["stroke"], "fill": annot.colors["stroke"]})
        annot_.update()
    else:
        annot_ = page.add_line_annot(p1=coords_right_upper_annot, p2=note_area_rect[:2])
        annot_.set_colors({"stroke": annot.colors["stroke"], "fill": annot.colors["stroke"]})
        annot_.update()

        annot_ = page.add_line_annot(p1=note_area_rect[:2], p2=(note_area_rect[0] + 24, note_area_rect[1]))
        annot_.set_colors({"stroke": annot.colors["stroke"], "fill": annot.colors["stroke"]})
        annot_.update()


def make_printable_page_wise(page: fitz.Page):
    # ----expand page on x-axis----
    expand_ratio = 0.3  # this decides how much the page gets expanded
    page.set_mediabox(page.rect + (0, 0, page.rect[2] * expand_ratio, 0))
    init_empty_margin_rect = page.rect + (max([i[2] for i in page.get_text("words")]), 0, 0, 0)

    # ----sort annotations on the page by position----
    annots = page.annots()
    annots = [{"annot": i, "distance": min([math.dist((0, 0), j) for j in i.vertices])} for i in annots]
    annots.sort(key=lambda x: x["distance"])
    annots = [i["annot"] for i in annots]

    # ----make annotations printable----
    for i in annots:
        make_printable_annot_wise(page, i, init_empty_margin_rect)
    return page


def make_printable(path_to_file: Path):
    """
    Args:
        path_to_file (Path): Path to the file to be made printable.
    Raises:
        Exception: If the file contains no annotation.
    Save:
        The file is saved in the same directory as the original file.
    """
    doc = fitz.open(path_to_file)
    if not doc.has_annots():
        raise Exception("This PDF has no annotations.")

    for page in doc:
        page = make_printable_page_wise(page)

    doc.save(path_to_file.with_suffix(".printable.pdf"))


if __name__ == "__main__":
    path_to_file = Path("example.pdf")
    make_printable(path_to_file)
