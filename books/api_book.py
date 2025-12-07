import os
from dataclasses import dataclass
from functools import lru_cache

import requests
from config import BOOK_PRINT_TYPE, TIMEOUT
from dotenv import load_dotenv
from exceptions import (
    APIKeyNotExists,
    ApiServiceError,
    BookError,
    UrlNotExists,
)
from requests import JSONDecodeError, Response
from typesdef import api_key, url

load_dotenv()


@dataclass
class Book:
    title: str
    author: str


@lru_cache(maxsize=None)
def _check_url_exists() -> url:
    url = os.getenv("BASE_BOOK_URL")
    if url is None:
        raise UrlNotExists
    return url


@lru_cache(maxsize=None)
def _check_api_key_exists() -> api_key:
    api_key = os.getenv("BOOK_API_KEY")
    if api_key is None:
        raise APIKeyNotExists
    return api_key


def _get_googleapi_response(title: str) -> Response:
    url = _check_url_exists()
    url = url.format(title=title)
    api_key = _check_api_key_exists()
    response = requests.get(
        url,
        params={"q": title, "key": api_key, "printType": BOOK_PRINT_TYPE},
        timeout=TIMEOUT,
    )

    if response.status_code != requests.codes.ok:
        raise ApiServiceError
    return response


def _parse_bookapi_response(response: Response) -> list[Book]:
    try:
        open_book_dict = response.json()
    except JSONDecodeError:
        raise ApiServiceError

    return _parse_author_title(open_book_dict)


def _parse_author_title(book_dict: dict) -> list[Book]:
    books = []
    try:
        for i in range(len(book_dict["items"])):
            if "authors" in book_dict["items"][i]["volumeInfo"]:
                author = book_dict["items"][i]["volumeInfo"]["authors"][0]
            else:
                author = "Автор не указан"
            title = book_dict["items"][i]["volumeInfo"]["title"]
            books.append(Book(title, author))
    except KeyError:
        raise BookError
    return books


def get_books(title: str) -> list[Book]:
    response = _get_googleapi_response(title=title)
    books = _parse_bookapi_response(response)
    return books


if __name__ == "__main__":
    books = get_books("Властелин Колец")
    for book in books:
        print(book.author, book.title)
