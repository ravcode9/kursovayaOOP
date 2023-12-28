from abc import ABC, abstractmethod
import json


class Vacancy:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.title = kwargs.get("profession", "")
        self.link = kwargs.get("link", "")
        self.salary = {
            "from": kwargs.get("payment_from", 0),
            "to": kwargs.get("payment_to", 0),
        }
        self.requirements = kwargs.get("work", "")
        self.extra_data = kwargs  # Сохраняем дополнительные данные

    def extract_salary(self):
        try:
            salary_from = self.salary.get("from", 0)
            salary_to = self.salary.get("to", 0)
            salary_values = [int(s) for s in (salary_from, salary_to) if s is not None]
            return sum(salary_values) / len(salary_values) if len(salary_values) > 0 else 0
        except (ValueError, TypeError):
            return 0

    def __lt__(self, other):
        return self.extract_salary() < other.extract_salary()


class AbstractVacancySaver(ABC):
    @abstractmethod
    def add_vacancy(self, vacancy):
        pass

    @abstractmethod
    def get_vacancies_by_salary(self, min_salary):
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy):
        pass


class JSONSaver(AbstractVacancySaver):
    def __init__(self, filename="vacancies.json"):
        self.filename = filename
        self.load_from_file()

    def load_from_file(self):
        try:
            with open(self.filename, 'r') as file:
                self.vacancies = json.load(file)
        except FileNotFoundError:
            self.vacancies = []

    def add_vacancy(self, vacancy):
        self.load_from_file()
        if vacancy.title not in (v.get("title") for v in self.vacancies):
            self.vacancies.append({
                "title": vacancy.title,
                "link": vacancy.link,
                "salary": vacancy.salary,
                "requirements": vacancy.requirements,
            })
            self.save_to_file()

    def get_vacancies_by_salary(self, min_salary):
        return [Vacancy(**v) for v in self.vacancies if Vacancy(**v).extract_salary() >= min_salary]

    def delete_vacancy(self, vacancy):
        self.vacancies = [v for v in self.vacancies if v.get("title") != vacancy.title]
        self.save_to_file()

    def save_to_file(self):
        with open(self.filename, 'w') as file:
            json.dump(self.vacancies, file, ensure_ascii=False, indent=4)


def filter_vacancies(*vacancies, filter_words):
    filtered_vacancies = []
    for platform_vacancies in vacancies:
        filtered_vacancies.extend([v for v in platform_vacancies if word_match(v, filter_words)])
    return filtered_vacancies


def word_match(vacancy, filter_words):
    return any(word.lower() in str(vacancy.extra_data).lower() for word in filter_words)


def sort_vacancies(vacancies):
    return sorted(vacancies, key=lambda v: v.extract_salary(), reverse=True)


def get_top_vacancies(vacancies, top_n):
    return vacancies[:top_n]


def print_vacancies(vacancies):
    for vacancy in vacancies:
        print(f"Название: {vacancy.title}")
        print(f"Ссылка: {vacancy.link}")
        print(f"Зарплата: {vacancy.salary}")
        print(f"Требования: {vacancy.requirements}")
        print("\n")


if __name__ == "__main__":
    # Пример использования
    json_saver = JSONSaver()
    # Добавление вакансии с Superjob.ru (подставьте реальные данные)
    superjob_vacancy = {
        "id": 25746005,
        "profession": "Специалист по согласованиям",
        "link": "https://www.superjob.ru/vakansii/specialist-po-soglasovaniyam-25746005-130520.html",
        "payment_from": 0,
        "payment_to": 0,
        "work": "1. Подготовка, согласование с Комитетами и службами...",
    }
    superjob_instance = Vacancy(**superjob_vacancy)
    json_saver.add_vacancy(superjob_instance)

    # Добавление вакансии с HH.ru (подставьте реальные данные)
    hh_vacancy = {
        "id": 123456,
        "name": "Python Developer",
        "alternate_url": "https://hh.ru/vacancy/123456",
        "salary": {"from": 100000, "to": 150000},
        "snippet": {"requirement": "3+ years of experience with Python"},
    }
    hh_instance = Vacancy(**hh_vacancy)
    json_saver.add_vacancy(hh_instance)

    # Вывод вакансий
    all_vacancies = json_saver.vacancies
    filtered_vacancies = filter_vacancies(all_vacancies, filter_words=["python", "experience"])
    sorted_vacancies = sort_vacancies(filtered_vacancies)
    top_vacancies = get_top_vacancies(sorted_vacancies, top_n=2)
    print_vacancies(top_vacancies)

