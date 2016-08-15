from flask import Flask, render_template, request, session, jsonify
import json
import requests
from model import connect_to_db, db, Course, SQLAlchemy
# from SQLAlchemy import func

app = Flask(__name__)

app.secret_key = "SECRET"


@app.route("/")
def index_page():
    """Show an homepage/inital search page."""

    return render_template("index.html")


@app.route("/search")
def show_search_results():
    """Show search results based on user input parameters."""

    phrase = request.args.get("search-phrase")

    try:
        q = db.session.query(Course).filter(Course.title.like('%' + phrase + '%'))
        relevent_courses = q.all()
            # | (func.lower(Course.category.like('%' + phrase + '%'))) | (func.lower(Course.subcategory.like('%' + phrase + '%')))).all()
        session['search-phrase'] = phrase
    except UnicodeEncodeError:
        pass

    return render_template("search.html", courses=relevent_courses)


@app.route("/search/filters.json")
def filter_results_by_price():
    """ Filter resuts based on user input parameters."""

    q = db.session.query(Course.title, Course.description)
    phrase = session['search-phrase']

    price = request.args.get("price")
    languages = request.args.getlist("languages")
    type_course = request.args.get("coursetype")
    certificates = request.args.get("certificates")
    source = request.args.get("source")
    university = request.args.getlist("university")

    args = [((Course.title.like('%' + phrase + '%')) | (Course.category.like('%' + phrase + '%')) | (Course.subcategory.like('%' + phrase + '%')))]

    if price:
        price_arg = Course.price <= price
        args.append(price_arg)
    else:
        price_arg = None

    if languages:
        language_arg = Course.languages.in_(languages)
        args.append(language_arg)
    else:
        language_arg = None

    if type_course == "self":
        type_arg = ((Course.type_course.like('%ondemand%')) | (Course.type_course is None))
        args.append(type_arg)
    elif type_course == "instructor":
        type_arg = Course.type_course.like('%session%')
        print "type arg: ", type_arg
        args.append(type_arg)
    else:
        type_arg = None

    if certificates == "yes":
        certificate_arg = (Course.has_certificates == True)
        args.append(certificate_arg)
    else:
        certificate_arg = None

    if source == "coursera":
        source_arg = (Course.source == "Coursera")
        args.append(source_arg)
    if source == "udemy":
        source_arg = (Course.source == "Udemy")
        args.append(source_arg)
    else:
        source_arg = None

    if university:
        university_arg = Course.partners.name.like('%' + university + '%')
        args.append(university_arg)
    else:
        university_arg = None
    
    
    args = tuple(args)
    # print "args: ", args

    query = q.filter(*args)

    try:
        courses = query.all()
        # print courses
    except UnicodeEncodeError:
        pass

    return jsonify(courses)
    # return render_template("search.html", courses=courses)
    # return json.dumps([dict(course) for course in courses])


# @app.route("/search/filters")
# def filter_results_by_language():
#     """ Filter resuts based on user input parameters."""


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(host="0.0.0.0")