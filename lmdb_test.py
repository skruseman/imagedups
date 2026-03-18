from pathlib import Path

from user_store import UserStore


def main() -> None:
    db_path = Path("example_lmdb")

    store = UserStore(db_path)

    try:
        store.put_user(
            user_id="1001",
            name="Alice",
            email="alice@example.com",
            tags=["admin", "beta"],
        )

        store.put_users_batch(
            [
                ("1002", "Bob", "bob@example.com", ["staff"]),
                ("1003", "Carol", "carol@example.com", ["trial", "eu"]),
                ("1004", "Dave", "dave@example.com", []),
            ]
        )

        user = store.get_user("1001")
        if user is not None:
            print("Loaded user:")
            print(f"  id={user.user_id}")
            print(f"  name={user.name}")
            print(f"  email={user.email}")
            print(f"  tags={list(user.tags)}")

        print("\nAll users:")
        for rec in store.iter_all_users():
            print(rec.user_id, rec.name, rec.email, list(rec.tags))

        print("\nCount:", store.count_users())

    finally:
        store.close()


if __name__ == "__main__":
    main()