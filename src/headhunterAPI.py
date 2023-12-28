from abc import ABC, abstractmethod
import requests


class AbstractJobAPI(ABC):
    @abstractmethod
    def get_vacancies(self, search_query):
        pass


class HeadHunterAPI(AbstractJobAPI):
    API_BASE_URL = "https://api.hh.ru/"

    def get_vacancies(self, search_query):
        endpoint = "vacancies"
        params = {"text": search_query}

        try:
            response = requests.get(f"{self.API_BASE_URL}{endpoint}", params=params)
            response.raise_for_status()
            vacancies = response.json().get("items", [])
            return vacancies
        except requests.exceptions.RequestException as e:
            print(f"Error accessing HeadHunter API: {e}")
            return []
