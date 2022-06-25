
# PPA
A simple script written in fitz that adds highlight annotations to page margins.

## How does it work?
Assume we have a PDF file with some highlighted text and annotations:

![](demo/annot.png)

Run:
```python
make_printable(Path("example.pdf"))
```
Before             |  After
:-------------------------:|:-------------------------:
![](demo/example.png)  |  ![](demo/printable.png)

Customize font size and color at line 38:
```python
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
```