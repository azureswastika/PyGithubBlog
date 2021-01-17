from json import load
from json.decoder import JSONDecodeError
from os import PathLike
from os.path import getctime
from pathlib import Path
from random import randint, sample
from shutil import rmtree
from string import ascii_letters, punctuation
from time import localtime, strftime
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from markdown import markdown


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PathDescriptor:
    def __set__(self, obj, value):
        if not value.exists():
            raise OSError("There is no such folder: {}".format(str(value.absolute())))
        obj.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Config(metaclass=Singleton):
    templates = PathDescriptor()
    blog = PathDescriptor()
    data = PathDescriptor()

    def __init__(self) -> None:
        self.__dict__.setdefault("page", "page.html")
        self.__dict__.setdefault("pagination", "pagination.html")
        self.__dict__.setdefault("max_pagination", 10)
        self.__dict__.setdefault("dateformat", "%H:%M %d.%m.%Y")
        self.parser()
        if "templates" not in self.__dict__.keys():
            self.__setattr__("templates", Path("templates"))
        if "blog" not in self.__dict__.keys():
            self.__setattr__("blog", Path("blog"))
        if "data" not in self.__dict__.keys():
            self.__setattr__("data", Path("data"))

    def __getattr__(self, key: str) -> Any:
        return self.__dict__.get(key, None)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ["templates", "blog", "data"]:
            return super().__setattr__(name, Path(value))
        return super().__setattr__(name, value)

    def parser(self):
        try:
            f = open("config.json", encoding="utf-8")
            file_data = load(f)
        except (JSONDecodeError, FileNotFoundError):
            pass
        else:
            for key in file_data.keys():
                self.__setattr__(key.replace("-", "_"), file_data[key])
            f.close()


class File:
    def __init__(self, path=None) -> None:
        config = Config()
        self.path = path
        self.markdown = open(str(self.path), "r", encoding="utf-8").read()
        self.title = self.markdown.split("\n")[0].strip("#").strip()
        self.html = markdown(self.markdown, extensions=["fenced_code"])
        self.filename = self.process_title(self.title)
        self.link = "../" + "{}.html".format(self.filename)
        self.date = strftime(config.dateformat, localtime(getctime(self.path)))

    def process_title(self, title: str) -> str:
        config = Config()
        if title == "":
            title = "".join(sample(ascii_letters, randint(3, 10)))
        if config.blog.joinpath("{}.html".format(title)).exists():
            title += "".join(sample(ascii_letters, randint(1, 3)))
            self.process_title(title)
        for el in punctuation:
            if el in title:
                title = title.replace(el, "_")
        return title.lower()


class GithubBlog:
    def __init__(self) -> None:
        config = Config()
        self.templates = config.templates
        self.blog = config.blog
        self.data = config.data
        self.page = config.page
        self.pagination = config.pagination
        self.max_pagination = config.max_pagination
        self.dateformat = config.dateformat
        self.loader = FileSystemLoader(self.templates)
        self.env = Environment(loader=self.loader)
        for file in [file for file in self.blog.glob("*")]:
            if file.is_file():
                file.unlink()
                continue
            rmtree(file)

        self.create_pages()

    def create_pages(self) -> None:
        pagination_data = list()
        try:
            page = self.env.get_template(self.page)
        except TemplateNotFound:
            raise TemplateNotFound(
                "Make sure that file {} exists and is located in the /{} folder".format(
                    self.page, str(self.templates)
                )
            )
        else:
            data = self.get_markdown()
            for index, item in enumerate(data):
                html = page.render(title=item.title, content=item.html)
                file = open(
                    str(self.blog.joinpath("{}.html".format(item.filename))),
                    "w",
                    encoding="utf-8",
                )
                file.write(html)
                file.close()
                pagination_data.append(item)
                if len(pagination_data) == self.max_pagination or len(data) == index + 1:
                    self.create_pagination(pagination_data)
                    pagination_data = list()
            print("PyGithubBlog created pages")

    def create_pagination(self, content: List[Dict[str, str]]) -> None:
        try:
            pagination = self.env.get_template(self.pagination)
        except TemplateNotFound:
            raise TemplateNotFound(
                "Make sure that file {} exists and is located in the /{} folder".format(
                    self.pagination, str(self.templates)
                )
            )
        else:
            html = pagination.render(content=content)
            if not self.blog.joinpath("page").exists():
                self.blog.joinpath("page").mkdir()
            num = len([file for file in self.blog.joinpath("page").glob("*")])
            file = open(
                str(self.blog.joinpath("page/{}.html".format(num + 1))),
                "w",
                encoding="utf-8",
            )
            file.write(html)
            file.close()

    def get_markdown(self) -> List[PathLike]:
        files = sorted([file for file in self.data.glob("*.md")], key=getctime)[::-1]
        return [File(path) for path in files]


def main() -> None:
    GithubBlog()


if __name__ == "__main__":
    main()
