from app.services.cms import CmsClient


def main():
    client = CmsClient()
    # client.login()

    client.logout()


if __name__ == '__main__':
    main()
