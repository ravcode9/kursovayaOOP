from abc import ABC, abstractmethod
import json
from html2text import html2text
class Vacancy:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.title = kwargs.get("name") or kwargs.get("profession", "")
        self.link = kwargs.get("alternate_url") or kwargs.get("link", "")

        # Проверяем наличие ключа "salary" и его значения
        salary_data = kwargs.get("salary")
        self.salary = {
            "from": salary_data.get("from") if salary_data and isinstance(salary_data, dict) else None,
            "to": salary_data.get("to") if salary_data and isinstance(salary_data, dict) else None,
        }

        self.requirements = kwargs.get("snippet", {}).get("requirement", "") or kwargs.get("work", "")
        self.extra_data = kwargs  # Сохраняем дополнительные данные

    def extract_salary(self):
        salary_from = self.salary.get("from")
        salary_to = self.salary.get("to")

        if salary_from is not None and salary_to is not None:
            if salary_from == salary_to:
                return f"от {salary_from}"
            else:
                return f"от {salary_from} до {salary_to}"
        elif salary_from is not None:
            return f"от {salary_from}"
        elif salary_to is not None:
            return f"до {salary_to}"
        else:
            return "зарплата не указана"

    def get_requirements(self):
        requirements = ""
        try:
            snippet_requirements = self.extra_data.get('snippet', {}).get('requirement', '')
            work_requirements = self.extra_data.get('work', '')
            requirements = snippet_requirements or work_requirements
            if requirements is not None:
                return html2text(
                    requirements) or "данные отсутствуют, проверьте информацию о требованиях в вакансии по ссылке"
            else:
                return "данные отсутствуют, проверьте информацию о требованиях в вакансии по ссылке"
        except Exception as e:
            print(f"Ошибка при обработке HTML: {e}")
            return "данные отсутствуют, проверьте информацию о требованиях в вакансии по ссылке"

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
                "salary": vacancy.extract_salary(),
                "requirements": vacancy.get_requirements(),
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
    for vacancy in vacancies:
        filtered_vacancies.extend([v for v in vacancy if word_match(v, filter_words)])
    return filtered_vacancies


def word_match(vacancy, filter_words):
    if isinstance(vacancy, Vacancy):
        vacancy_data = vacancy.extra_data
    else:
        vacancy_data = vacancy

    return any(word.lower() in str(vacancy_data).lower() for word in filter_words)



def sort_vacancies(vacancies):
    return sorted(vacancies, key=lambda v: Vacancy(**v).extract_salary() if isinstance(v, dict) else v.extract_salary(), reverse=True)


def get_top_vacancies(vacancies, top_n):
    return vacancies[:top_n]

def print_vacancies(vacancies):
    for vacancy in vacancies:
        if isinstance(vacancy, Vacancy):
            print(f"Название: {vacancy.title}")
            print(f"Ссылка: {vacancy.link}")
            print(f"Зарплата: {vacancy.extract_salary()}")
            print(f"Требования: {vacancy.get_requirements()}")
        elif isinstance(vacancy, dict):
            print(f"Название: {vacancy.get('title', 'Не указано')}")
            print(f"Ссылка: {vacancy.get('link', 'Не указана')}")
            print(f"Зарплата: {vacancy.get('salary', 'Не указана')}")
            print(f"Требования: {vacancy.get('requirements', 'данные отсутствуют, проверьте информацию о требованиях в вакансии по ссылке')}")
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

    # Вывод вакансий
    all_vacancies = json_saver.vacancies
    filtered_vacancies = filter_vacancies(all_vacancies, filter_words=["python", "experience"])
    sorted_vacancies = sort_vacancies(filtered_vacancies)
    top_vacancies = get_top_vacancies(sorted_vacancies, top_n=3)
    print_vacancies(top_vacancies)
