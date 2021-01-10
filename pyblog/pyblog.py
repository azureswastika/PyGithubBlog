from argparse import ArgumentParser
from os.path import getctime
from pathlib import Path
from random import randint, sample
from string import ascii_letters, punctuation
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from markdown import markdown


class PathDescriptor:
    def __set__(self, obj, value):
        if not value.exists():
            raise OSError("There is no such folder: {}".format(str(value.absolute())))
        obj.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Pyblog:
    templates = PathDescriptor()
    blog = PathDescriptor()
    data = PathDescriptor()

    def __init__(self, templates: str, blog: str, data: str) -> None:
        self.templates = Path(templates)
        self.blog = Path(blog)
        self.data = Path(data)
        self.loader = FileSystemLoader(self.templates)
        self.env = Environment(loader=self.loader)

    def create_pages(self):
        try:
            page = self.env.get_template("page.html")
        except TemplateNotFound:
            raise TemplateNotFound(
                "Make sure that file page.html exists"
                "and is located in the /templates folder"
            )
        else:
            for item in self.markdown2html():
                html = page.render(title=item["title"], content=item["html"])
                title = self.process_title(item["title"])
                with open(
                    self.blog.joinpath("{}.html".format(title)), "w", encoding="utf-8"
                ) as file:
                    file.write(html)

    def process_title(self, title: str) -> str:
        if title == "":
            title = "".join(sample(ascii_letters, randint(5, 20)))
        if self.blog.joinpath('{}.html'.format(title)).exists():
            title += "".join(sample(ascii_letters, randint(1, 3)))
            self.process_title(title)
        for el in punctuation:
            if el in title:
                title = title.replace(el, "_")

        return title.lower()

    def markdown2html(self) -> Dict[str, str]:
        return [
            {
                "title": text.split("\n")[0].strip("#"),
                "html": markdown(text, extensions=["fenced_code"]),
            }
            for text in self.get_text()
        ]

    def get_text(self) -> List[str]:
        return [open(path, encoding="utf-8").read() for path in self.get_markdown()]

    def get_markdown(self) -> List[str]:
        return sorted([file for file in self.data.glob("*.md")], key=getctime)[::-1]


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-t", "--templates", default="templates", type=str, nargs="?")
    parser.add_argument("-b", "--blog", default="blog", type=str, nargs="?")
    parser.add_argument("-d", "--data", default="data", type=str, nargs="?")
    args = parser.parse_args()
    blog = Pyblog(args.templates, args.blog, args.data)
    print(blog.create_pages())


if __name__ == "__main__":
    main()
