import json

from src.config import ACCOUNT_NAME


class Logging:
    def __init__(self, course_tag: str) -> None:
        self.course_tag = course_tag
        self.file_name = f'src\\logs\\{ACCOUNT_NAME}.json'
        self.data = self.load()

    def mark_as_done(self, step: str) -> None:
        self.data[self.course_tag][step] = True

    def verify_if_done(self, step: str) -> bool | str:
        step_done = self.data.get(self.course_tag, {}).get(step, False)

        return step_done

    def load(self) -> dict[str, dict[str, bool | str]]:
        try:
            with open(self.file_name, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return dict[str, dict[str, bool | str]]()

    def dump(self) -> None:
        with open(self.file_name, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4)
