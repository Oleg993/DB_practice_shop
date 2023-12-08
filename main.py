import sqlite3
import hashlib
import time
from datetime import datetime, timedelta

def md5sum(value):
    return hashlib.md5(value.encode()).hexdigest()

with sqlite3.connect('Shop.db') as db:
    cursor = db.cursor()

    # query = """
    # CREATE TABLE IF NOT EXISTS users(
    #     id INTEGER PRIMARY KEY,
    #     name TEXT,
    #     address TEXT,
    #     login VARCHAR(15),
    #     password VARCHAR(20)
    #     );
    #
    # CREATE TABLE IF NOT EXISTS dishes(
    #     id INTEGER PRIMARY KEY,
    #     name TEXT,
    #     price REAL,
    #     spoilage_time DATETIME
    # );
    #
    # CREATE TABLE IF NOT EXISTS orders(
    #     id INTEGER PRIMARY KEY,
    #     user_id INTEGER,
    #     delivery_address TEXT,
    #     total_price REAL,
    #     time_to_delivery DATATIME,
    #     FOREIGN KEY (user_id) REFERENCES users (id)
    # );
    #
    # CREATE TABLE IF NOT EXISTS dishes_in_order(
    #     id INTEGER PRIMARY KEY,
    #     order_id INTEGER,
    #     dish_id INTEGER,
    #     quantity INTEGER,
    #     FOREIGN KEY (order_id) REFERENCES orders (id),
    #     FOREIGN KEY (dish_id) REFERENCES dishes (id)
    # );
    #
    #     CREATE TABLE IF NOT EXISTS stock(
    #     dish_id INTEGER,
    #     availability INTEGER,
    #     spoilage_time DATETIME,
    #     FOREIGN KEY (dish_id) REFERENCES dishes (id)
    # )
    # """
    #
    # cursor.executescript(query)

# будет просить авторизоваться после окончания закупок и ввода exit
# def is_registrated():
#     while True:
#         yes_or_no = input("Do you have an account? (Yes or No): ")
#         if yes_or_no.lower() == 'yes':
#             log_in()
#             break
#         elif yes_or_no.lower() == 'no':
#             print("You need to create an account, please make one.")
#             registration()
#             print("Now you have an account and you can log in")
#             log_in()
#             break
#         else:
#             print('Answer only "Yes" or "No"')

# НЕ будет просить авторизоваться после окончания закупок и ввода exit, но работает с блоком кода, который в самом низу

def is_registrated():
    yes_or_no = input("Do you have an account? (Yes or No): ")
    if yes_or_no.lower() == 'yes':
        return 'Yes'
    elif yes_or_no.lower() == 'no':
        print("You need to create an account, please make one.")
        return 'No'
    else:
        print('Answer only "Yes" or "No"')
        return is_registrated()

def registration():
    name = input("Name: ")
    login = input("Login: ")
    address = input("Address: ")
    password = input("Password: ")

    try:
        db = sqlite3.connect('Shop.db')
        cursor = db.cursor()

        db.create_function("md5", 1, md5sum)

        cursor.execute("SELECT login FROM users WHERE login = ?", [login])
        if cursor.fetchone() is None:
            values = [name, address, login, password]

            cursor.execute("INSERT INTO users(name, address, login, password) VALUES (?, ?, ?, md5(?))", values)
            db.commit()
        else:
            print("The login already exists")
            registration()
    except sqlite3.Error as e:
        print("Error", e)
    finally:
        cursor.close()
        db.close()


def log_in():
    login = input("Login: ")
    password = input("Password: ")

    try:
        db = sqlite3.connect('Shop.db')
        cursor = db.cursor()

        db.create_function("md5", 1, md5sum)

        cursor.execute("SELECT login FROM users WHERE login = ?", [login])
        if cursor.fetchone() is None:
            print("The login doesn't ixist!")
        else:
            cursor.execute("SELECT password FROM users WHERE login = ? AND password = md5(?)", [login, password])
            if cursor.fetchone() is None:
                print("The password is wrong!")
            else:
                get_order(login)
    except sqlite3.Error as e:
        print("Error", e)
    finally:
        cursor.close()
        db.close()


def get_order(login):
    print(f"\nМы рады Вас видеть, {login}! \nСделайте Ваш заказ!")

    try:
        db = sqlite3.connect('Shop.db')
        cursor = db.cursor()

        cursor.execute("SELECT id, name, price FROM dishes")
        dishes = cursor.fetchall()
        for dish in dishes:
            print(f"{dish[1]}, {dish[2]} баксов")

        total_price = 0.0

        cursor.execute("SELECT id, address FROM users WHERE login = ?", [login])
        user = cursor.fetchone()
        user_id = user[0]
        user_address = user[1]

        while True:
            order = input(
                "Выберите продукт, чтобы добавить его в ваши заказы (или напишите 'exit', чтобы завершить заказ): ")
            if order.lower() == "exit":
                break

            quantity = int(input("Укажите желаемое количество: "))
            cursor.execute("SELECT id FROM dishes WHERE name = ?", [order])
            dish_id = cursor.fetchone()

            cursor.execute("SELECT availability FROM stock WHERE dish_id= ?", [dish_id[0]])
            availability = cursor.fetchone()[0]

            if availability >= quantity:
                for dish in dishes:
                    if dish[1].lower() == order.lower():
                        total_price += dish[2] * quantity
                        cursor.execute(
                            "INSERT INTO dishes_in_order(order_id, dish_id, quantity) VALUES ((SELECT MAX(id) FROM orders),?, ?)",
                            [dish[0], quantity])
                        cursor.execute("UPDATE stock SET availability = availability - ? WHERE dish_id= ?", [quantity, dish[0]])

            else:
                print(f"К сожаления, для заказа доступно лишь {availability} единиц выбранного товара.")


        time_to_delivery = datetime.now() + timedelta(hours=1)
        time_to_delivery_rounded = time_to_delivery.replace(second=0, microsecond=0)

        cursor.execute(
            "INSERT INTO orders(user_id, delivery_address, total_price, time_to_delivery) VALUES(?, ?, ?, ?)",
            [user_id, user_address, total_price, time_to_delivery_rounded])

        db.commit()

        print("Заказ успешно создан! Ожидайте доставку в течение часа.")

    except sqlite3.Error as e:
        print("Error", e)

    finally:
        cursor.close()
        db.close()


# можно такой блок добавить и is_registrated изменить, чтобы не просило сразу же авторизоваться после exit
if __name__ == '__main__':
    while True:
        user_status = is_registrated()
        if user_status == 'Yes':
            log_in()
            break
        elif user_status == 'No':
            registration()
            print("Now you have an account and you can log in")
            log_in()
            break
        elif user_status is None:
            continue


is_registrated()
registration()
log_in()





