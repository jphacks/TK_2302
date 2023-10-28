# run.py

from app import app

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, help='port')
    parser.add_argument('-d', '--debug', default=False, help='debug')
    args = parser.parse_args()
    app.run(debug=args.debug, port=args.port)
