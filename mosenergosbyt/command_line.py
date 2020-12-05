from mosenergosbyt import Session, Account, Meter, Measure
import argparse
from datetime import datetime
import json
from sys import argv


def converter(obj):
    if isinstance(obj, Session):
        return None
    if isinstance(obj, datetime):
        return obj.__str__()
    else:
        return obj.__dict__


def toJson(obj):
    return json.dumps(obj, default=lambda o: converter(o), sort_keys=True, indent=4, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Укажите параметры ввода')

    parser.add_argument('-i', '--info', action='store_true',
                        help='Получение информации')
    parser.add_argument('-l', '--login', required=True, type=str,
                        help='логин')
    parser.add_argument('-p', '--password', required=True, type=str,
                        help='пароль')

    parser.add_argument('-u', '--upload', action='store_true',
                        help='Передача показаний')
    parser.add_argument('-m', '--meter', type=str,
                        help='Номер счетчика для передачи (обязательно для upload)')
    parser.add_argument('-d', '--day', 
                        help='дневные показания')
    parser.add_argument('-n', '--night', required=False, default=None,
                        help='ночные показания')
    parser.add_argument('-e', '--evening', required=False, default=None,
                        help='вечерние показания')

    args = parser.parse_args()
    try:
        acc = Account(Session(login=args.login, password=args.password))
        acc.get_info(with_measure=True, indications=True, balance=True)

        if args.info:
            print(toJson(acc.meter_list))
            exit(0)
        elif args.upload:
            if not args.meter:
                print(f'Нужно указать номер счетчика')
                exit(1)
            if not args.day:
                print(f'Нужно указать дневные показания')
                exit(1)
            meter = acc.meter_list.get(args.meter)
            if not meter:
                print(f'Информация о cчетчике <{args.meter}> не найдена')
                exit(1)
            meter.upload_measure(args.day, args.night, args.evening)
    except SystemExit as e:
        pass
    except BaseException as e:
        print(e)
        exit(1)

if __name__ == "__main__":
    main()
