from config import Config
import argparse
from text_base.search_getter import get_searcher

config = None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database_path")
    parser.add_argument("--index_path")
    parser.add_argument("--test", action="store_true", default=False)

    args = parser.parse_args()

    config = Config(
        database_path=args.database_path,
        index_path=args.index_path,
        test=args.test
    )

    searcher = get_searcher(config)

    print(searcher.find("kek"))

    # do long polling