from services.config import get_settings
from services.query_service import QueryService


def main():
    question = input("Enter your question: ").strip() or "What are the top 5 product categories by revenue?"
    service = QueryService(get_settings())
    sql, df = service.ask(question)

    print("\nGenerated SQL:")
    print(sql)
    print("\nQuery Result:")
    print(df)


if __name__ == "__main__":
    main()
