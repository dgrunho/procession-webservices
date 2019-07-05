from api.db import get_db


def main():
    db = get_db()

    procession_positions = db.get_collection('processionPositions')

    procession_positions.create_index([('date', 1)])
    procession_positions.create_index([('identifier', 1)])
    procession_positions.create_index([('identifier', 1), ('date', 1)])

    agenda_en = db.get_collection('agenda_en')
    agenda_pt = db.get_collection('agenda_pt')

    for agenda in (agenda_en, agenda_pt):
        agenda.create_index([('date', 1)])

    routes = db.get_collection('routes')

    routes.create_index([('name', 1)])


if __name__ == '__main__':
    main()
