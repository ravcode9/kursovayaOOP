from abc import ABC, abstractmethod
import os
import requests


class AbstractJobAPI(ABC):
    @abstractmethod
    def get_vacancies(self, search_query, **params):
        pass


class SuperJobAPI(AbstractJobAPI):
    API_BASE_URL = "https://api.superjob.ru/2.0/"

    def __init__(self):
        superjob_token = os.getenv("API_SUPERJOB")
        if not superjob_token:
            raise ValueError("API_SUPERJOB token is missing in environment variables.")
        self.api_key = superjob_token

    def get_vacancies(self, search_query, order_field="payment", order_direction="asc", payment_from=None, payment_to=None, **kwargs):
        endpoint = "vacancies/"
        headers = {
            "X-Api-App-Id": self.api_key,
        }
        params = {
            "keyword": search_query,
            "order_field": order_field,
            "order_direction": order_direction,
            "payment_from": payment_from,
            "payment_to": payment_to,
            **kwargs,
        }

        try:
            response = requests.get(f"{self.API_BASE_URL}{endpoint}", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            vacancies = data.get("objects", [])
            return vacancies
        except requests.exceptions.RequestException as e:
            print(f"Error accessing SuperJob API: {e}")
            return []