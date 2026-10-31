"""GPA calculator. Run with python3 app.py; no packages required."""
import json
import math
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

GRADES = {'A+': 4, 'A': 4, 'A-': 3.7, 'B+': 3.3, 'B': 3, 'B-': 2.7,
          'C+': 2.3, 'C': 2, 'C-': 1.7, 'D+': 1.3, 'D': 1, 'D-': .7, 'F': 0,
          'P': None, 'W': None, 'I': None}
LEVELS = {'Regular': 0, 'Honors': .5, 'AP / IB': 1}


def summarize(credits, points, unweighted_points):
    """Convert point totals into GPAs, handling an empty semester."""
    return {
        'credits': credits,
        'points': points,
        'gpa': points / credits if credits else None,
        'unweighted': unweighted_points / credits if credits else None,
    }


def calculate_semester(semester):
    """Calculate one semester using credits and optional course bonuses."""
    credits = points = unweighted_points = 0
    for course in semester['courses']:
        grade = course.get('grade', '')
        level = course.get('level', 'Regular')
        if level not in LEVELS or (grade and grade not in GRADES):
            raise ValueError('Choose a valid grade and course level.')

        try:
            hours = float(course['credits'])
        except (ValueError, TypeError, KeyError):
            raise ValueError('Enter valid credits for every course.') from None
        if not math.isfinite(hours) or not 0 <= hours <= 1000:
            raise ValueError('Course credits must be between 0 and 1000.')

        base = GRADES.get(grade)
        if base is None:  # Blank, pass, withdrawal, or incomplete.
            continue
        bonus = 0
        if semester.get('weighted', True) and base > 0:
            bonus = LEVELS[level]

        credits += hours
        points += (base + bonus) * hours
        unweighted_points += base * hours

    return summarize(credits, points, unweighted_points), unweighted_points


def calculate(data):
    """Combine semester totals, rather than averaging semester GPAs."""
    if not isinstance(data.get('semesters'), list):
        raise ValueError('Semesters must be a list.')
    semesters = []
    total_unweighted = 0
    for semester in data['semesters']:
        result, unweighted_points = calculate_semester(semester)
        semesters.append(result)
        total_unweighted += unweighted_points

    overall = summarize(
        sum(semester['credits'] for semester in semesters),
        sum(semester['points'] for semester in semesters),
        total_unweighted,
    )
    return {**overall, 'semesters': semesters}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent / 'static'), **kwargs)

    def do_POST(self):
        if self.path != '/api/calculate':
            self.send_error(404)
            return
        try:
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length <= 1_000_000:
                raise ValueError('Invalid request size.')
            result = calculate(json.loads(self.rfile.read(length)))
            status = 200
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            result, status = {'error': str(exc) or 'Invalid course data.'}, 400
        encoded = json.dumps(result).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    print(f'GPA Calculator: http://127.0.0.1:{args.port}', flush=True)
    try:
        ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
    except KeyboardInterrupt:
        pass
