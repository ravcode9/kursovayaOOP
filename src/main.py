from src.headhunterAPI import HeadHunterAPI
from src.superjobAPI import SuperJobAPI
from vacancies import JSONSaver, Vacancy, filter_vacancies, sort_vacancies, get_top_vacancies, print_vacancies

def get_user_keywords():
    user_keywords_input = input("Введите ключевые слова для фильтрации вакансий (через запятую): ")
    return user_keywords_input.split(",") if user_keywords_input else []

def user_interaction():
    api_choice = input("Выберите API (hh/sj): ").lower()

    if api_choice == 'hh':
        job_api = HeadHunterAPI()
    elif api_choice == 'sj':
        job_api = SuperJobAPI()
    else:
        print("Неверный выбор API.")
        return

    json_saver = JSONSaver()

    search_query = input("Введите поисковый запрос: ")
    vacancies = job_api.get_vacancies(search_query)

    if not vacancies:
        print("Нет вакансий, соответствующих заданным критериям.")
        return

    all_vacancies = [Vacancy(**v) for v in vacancies]

    filter_words = get_user_keywords()
    filtered_vacancies = filter_vacancies(all_vacancies, filter_words=filter_words)

    if not filtered_vacancies:
        print("Нет вакансий, соответствующих заданным критериям.")
        return

    sorted_vacancies = sort_vacancies(filtered_vacancies)
    top_vacancies = get_top_vacancies(sorted_vacancies, top_n=int(input("Введите количество вакансий для вывода: ")))
    print_vacancies(top_vacancies)

    # Сохранение вакансий в JSON-файл
    for vacancy in top_vacancies:
        json_saver.add_vacancy(vacancy)

    print("Вакансии успешно сохранены в JSON-файл.")

if __name__ == "__main__":
    user_interaction()


print('loh')