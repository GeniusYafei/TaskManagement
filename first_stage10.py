"""
first_stage.py

Author: [Yafei Wang z5314432]

Date: [10/11/2023]

This file contains the code used for the first stage implementation of your
proposal. You should modify it so that it contains all the code required for
your MVP.
"""
# Import the required dependencies for making a web app
from flask import Flask, request, session, redirect
import json
import pyhtml as p
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ad6fed241db347651260f46a745d5d96'

USER_LISTS_FILE = './user_lists.json'
USER_TASKLIST_FILE = './user_tasklist.json'


def write_json_file(filename, info_to_save):
    with open(filename, 'w') as file:
        json.dump(info_to_save, file)


def read_json_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)


@app.route('/', methods=["GET", "POST"])
def homepage():
    if session.get("user_logged_in"):
        return redirect("/homepage")
    else:
        return redirect("/login")


@app.route('/login', methods=["GET", "POST"])
def login():
    error_msg = session.get("error_msg", "")
    if "error_msg" in session:
        session.pop("error_msg")
    response = p.html(
        p.head(
            p.title("Task Management"),
            p.link(rel="stylesheet", href="/static/login.css")
        ),
        p.body(
            p.h1("Weclome to the Task Management"),
            p.h2("login"),
            p.p(error_msg),
            p.form(
                p.div(id="login_page")(
                    p.label(for_="uname_id")("Username: "),
                    p.input(type="text", id="uname_id", name="uname"), p.br,
                    p.label(for_="pword_id")("Password: "),
                    p.input(type="password", id="pword_id",
                            name="pword"), p.br,
                    p.input(type="submit", name="create_acc_btn",
                            value="Register", formaction="/create_acc"),
                    p.input(type="submit", name="login_btn",
                            value="Login", formaction="/check_login"))
            )
        )

    )
    return str(response)


@app.route("/create_acc", methods=["GET", "POST"])
def create_acc():
    error_msg = session.get("error_msg", "")
    if "error_msg" in session:
        session.pop("error_msg")
    response = p.html(
        p.head(
            p.title("Task Management"),
            p.link(rel="stylesheet", href="static/login.css")
        ),
        p.body(
            p.h1("Register"),
            p.p(error_msg),
            p.form(
                p.div(id="Register_page")(
                    p.label(for_="uname_id")("Username: "),
                    p.input(type="text", id="uname_id", name="uname"), p.br,
                    p.label(for_="pword_id")("Password: "),
                    p.input(type="password", id="pword_id",
                            name="pword"), p.br,
                    p.input(type="submit", name="create_acc_btn",
                            value="Register Account", formaction="/create_acc_save"))
            )
        )

    )
    return str(response)


@app.route("/create_acc_save", methods=["POST"])
def create_acc_save():
    existing_users = read_json_file(USER_LISTS_FILE)
    uname_entered = request.form.get("uname", "").strip()
    pword_entered = request.form.get("pword", "")
    if not uname_entered:
        session['error_msg'] = "Please enter a username."
        if not pword_entered:
            session['error_msg'] = "Please enter a username or password."
        return redirect("/create_acc")

    if not pword_entered:
        session['error_msg'] = "Please enter a password."
        return redirect("/create_acc")

    if uname_entered in existing_users:
        session['error_msg'] = "This user already exists. Please try a different username."
        return redirect('/create_acc')

    existing_users[uname_entered] = pword_entered
    write_json_file(USER_LISTS_FILE, existing_users)

    tasks = read_json_file(USER_TASKLIST_FILE)
    tasks[uname_entered] = {}
    write_json_file(USER_TASKLIST_FILE, tasks)

    session['user_logged_in'] = True
    session['username'] = uname_entered
    return redirect("/login")


@app.route("/check_login", methods=["POST"])
def check_login():
    uname_entered = request.form["uname"]
    pword_entered = request.form["pword"]

    existing_users = read_json_file(USER_LISTS_FILE)

    if uname_entered in existing_users and pword_entered == existing_users[uname_entered]:
        session['user_logged_in'] = uname_entered
        return redirect("/homepage")
    else:
        session['error_msg'] = "Username or password was incorrect. Please try again."
        return redirect("/login")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop('user_logged_in', None)
    return redirect("/login")

def days_until_deadline(deadline_str):
    print(f"Deadline string: {deadline_str}")
    if not deadline_str:
        return "No deadline"
    deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
    today = datetime.now()
    remaining_days = (deadline - today).days
    print(f"Remaining days: {remaining_days}")
    if remaining_days == -1:
        return p.span("Today!!!!!!", _class = "Today")
    elif remaining_days < 0:
        return p.span("Deadline passed", _class = "Deadline_passed")
    elif 0 < remaining_days <= 3:
        return p.span(f"{remaining_days} days left", _class = "days_3remaining")
    elif 3 < remaining_days <= 7:
        return p.span(f"{remaining_days} days left", _class = "days_7remaining")
    elif 7 < remaining_days <= 15:
        return p.span(f"{remaining_days} days left", _class = "days_15remaining")
    elif 15 < remaining_days <= 30:
        return p.span(f"{remaining_days} days left", _class = "days_30remaining")
    else:
        return p.span(f"{remaining_days} days left", _class = "days_remaining")


@app.route('/homepage', methods=["GET"])
def view_tasks():
    if not session.get('user_logged_in'):
        return redirect('/login')

    username = session['user_logged_in']
    tasks = read_json_file(USER_TASKLIST_FILE).get(username, {})

    body_content = [p.h1(f"{username}'s Task Management")]

    error_msg = session.pop('error_msg', None)
    if error_msg:
        body_content.append(p.p(error_msg))

    # for list_name, task_list in tasks.items():
    #     task_items = [
    #         p.li(
    #             f"{task['task_name']} (Deadline: {task['task_deadline']}): {task['task_content']}, ",
    #             p.span(days_until_deadline(task['task_deadline']), _class="remaining_days"),
    #             p.a("Edit", href=f"/task_content/{list_name}/{task['task_name']}"),
    #             p.form(
    #                 p.input(type="submit", value="Delete", formaction=f"/delete_task/{list_name}/{task['task_name']}"),
    #                 p.input(type="submit", value="Complete", formaction=f"/completed_task/{list_name}/{task['task_name']}")
    #                 if not task.get('is_completed', False) else p.span("Completed"),
    #                 method="POST"
    #             )
    #         ) for task in task_list
    #     ]
    #     delete_list_form = p.form(
    #         p.input(type="submit", value=f"Delete List '{list_name}'"),
    #         method="POST", action=f"/delete_list/{list_name}"
    #     )
    #     body_content.extend([p.h3(list_name), p.ul(task_items), delete_list_form])

    for list_name, task_list in tasks.items():
        task_items = [
            p.li(
                f"{task['task_name']} (Deadline: {task['task_deadline']}): {task['task_content']}.   ",
                p.span("✔", _class="remaining_check") if task.get('is_completed', False) else p.span(days_until_deadline(task['task_deadline']), _class="remaining_days"),
                p.a("Edit", href=f"/task_content/{list_name}/{task['task_name']}"),
                p.form(
                    p.input(type="submit", value="Delete", _class="delete", formaction=f"/delete_task/{list_name}/{task['task_name']}"),
                    # p.input(type="submit", value="Complete", _class="complete", formaction=f"/completed_task/{list_name}/{task['task_name']}") if not task.get('is_completed', False) else p.span("Completed", _class="completed"),
                p.input(
                    type="submit",
                    value="Completed" if task.get('is_completed', False) else "Complete",
                    _class="completed" if task.get('is_completed', False) else "complete",
                    formaction=f"/toggle_task_completion/{list_name}/{task['task_name']}"
                ),
                method="POST"
            )
        ) for task in task_list
        ]
        delete_list_form = p.form(
            p.input(type="submit", _class="delete_list", value=f"Delete List of '{list_name}'"),
            method="POST", action=f"/delete_list/{list_name}"
        )
        body_content.extend([p.h3(list_name), p.ul(task_items), delete_list_form])



    create_list_form = p.form(
        p.label("List Name:", for_="list_name"),
        p.input(type="text", id="list_name", name="list_name"),
        p.input(type="submit", value="Create List", _class = "btn"),
        method="POST", action="/create_list"
    )
    body_content.append(create_list_form)

    add_task_form = p.form(
        p.label("Select List:", for_="list_name"),
        p.select([p.option(list_name, value=list_name) for list_name in tasks.keys()], name="list_name"),
        p.label("Task Name:", for_="task_name"),
        p.input(type="text", id="task_name", name="task_name"),
        p.label("Task Content:", for_="task_content"),
        p.input(type="text", id="task_content", name="task_content"),
        p.label("Deadline:", for_="task_deadline"),
        p.input(type="date", id="task_deadline", name="task_deadline"), p.br,
        p.input(type="submit", value="Add Task", _class="btn"),
        method="POST", action="/add_task"
    )
    body_content.append(add_task_form)

    logout_form = p.form(
        p.input(type="submit", value="Logout", _class="btn", formaction="/logout"),
        method="POST"
    )
    body_content.append(logout_form)

    response = p.html(
        p.head(p.title("Task Management")),
        p.link(rel="stylesheet", href="/static/homepage.css"),
        p.body(p.div(id="homepage")(body_content))
    )

    return str(response)

@app.route("/create_list", methods=["POST"])
def create_list():
    username = session.get('user_logged_in')
    new_list_name = request.form.get('list_name')
    if not new_list_name:
        return redirect('/homepage')

    tasks = read_json_file(USER_TASKLIST_FILE)
    if username not in tasks:
        tasks[username] = {}
    if new_list_name in tasks[username]:
        return redirect('/homepage')

    tasks[username][new_list_name] = []
    write_json_file(USER_TASKLIST_FILE, tasks)
    return redirect('/homepage')


@app.route('/delete_list/<list_name>', methods=["POST"])
def delete_list(list_name):
    username = session.get('user_logged_in')

    tasks = read_json_file(USER_TASKLIST_FILE)
    if list_name in tasks[username]:
        del tasks[username][list_name]

    write_json_file(USER_TASKLIST_FILE, tasks)
    return redirect('/homepage')


@app.route("/task_content/<list_name>/<task_name>", methods=["GET", "POST"])
def task_content(list_name, task_name):
    username = session.get('user_logged_in')
    if not username:
        return redirect('/login')

    tasks = read_json_file(USER_TASKLIST_FILE)
    user_tasks = tasks.get(username, {})
    user_list = user_tasks.get(list_name, [])

    current_task = None
    for task in user_list:
        if task['task_name'] == task_name:
            current_task = task
            break
    if not current_task:
        return redirect('/homepage')

    if request.method == "POST":
        updated_task_name = request.form.get('task_name')
        updated_task_content = request.form.get('task_content')
        updated_task_deadline = request.form.get('task_deadline')

        for task in user_list:
            if task['task_name'] == task_name:
                task['task_name'] = updated_task_name
                task['task_content'] = updated_task_content
                task['task_deadline'] = updated_task_deadline
                break
        tasks[username][list_name] = user_list
        write_json_file(USER_TASKLIST_FILE, tasks)
        return redirect('/homepage')

    current_task_content = current_task.get('task_content', '')
    current_task_deadline = current_task.get('task_deadline', '')

    response = p.html(
        p.head(
            p.title("Task Management"),
            p.link(rel="stylesheet", href="/static/taskcontent.css")

        ),

        p.body(
            p.h1(f"Edit Task: {task_name}"),
            p.form(method="POST")(
                p.label(for_="task_name")("Task Name: "),
                p.input(type="text", id="task_name",
                        name="task_name", value=task_name), p.br,
                p.label(for_="task_content")("Task Content: "),
                p.input(type="text", id="task_content",
                        name="task_content", value=current_task_content), p.br,
                p.label(for_="task_deadline")("Deadline: "),
                p.input(type="date", id="task_deadline",
                        name="task_deadline", value=current_task_deadline), p.br,
                p.input(type="hidden", name="original_task_name",
                        value=task_name),
                p.input(type="submit", value="Save")
            ),
            p.a("Back to homepage", href="/homepage")
        )
    )
    return str(response)


@app.route('/add_task', methods=["POST"])
def add_task():
    username = session.get('user_logged_in')
    list_name = request.form.get('list_name')
    task_content = request.form.get('task_content')
    task_name = request.form.get('task_name')
    task_deadline = request.form.get('task_deadline')

    tasks = read_json_file(USER_TASKLIST_FILE)
    if not task_name:
        session['error_msg'] = "Please enter a task name."
        return redirect('/homepage')
    user_tasks = tasks.get(username, {})
    # if any(task['task_name'] == task_name for task in user_tasks.get(list_name, [])):
    for task in user_tasks.get(list_name, []):
        if task['task_name'] == task_name:
            session['error_msg'] = "This task name already exists. Please try a different task name."
            return redirect('/homepage')

    # tasks = read_json_file(USER_TASKLIST_FILE)
    if username not in tasks:
        tasks[username] = {}

    if list_name not in tasks[username]:
        tasks[username][list_name] = []
    tasks[username][list_name].append({
        "task_name": task_name,
        "task_content": task_content,
        "task_deadline": task_deadline,
        "is_completed": False
    })

    write_json_file(USER_TASKLIST_FILE, tasks)
    return redirect('/homepage')


@app.route('/delete_task/<list_name>/<task_name>', methods=["POST"])
def delete_task(list_name, task_name):
    username = session.get('user_logged_in')

    tasks = read_json_file(USER_TASKLIST_FILE)
    user_tasks = tasks.get(username, {})
    user_list = user_tasks.get(list_name, [])

    # user_list = [task for task in user_list if task['task_name'] != task_name]
    new_user_list = []
    for task in user_list:
        if task['task_name'] != task_name:
            new_user_list.append(task)
    user_list = new_user_list
    user_tasks[list_name] = user_list
    tasks[username] = user_tasks
    write_json_file(USER_TASKLIST_FILE, tasks)

    return redirect('/homepage')


# @app.route('/completed_task/<list_name>/<task_name>', methods=["POST"])
# def completed_task(list_name, task_name):
#     username = session.get('user_logged_in')

#     tasks = read_json_file(USER_TASKLIST_FILE)
#     user_tasks = tasks.get(username, {})
#     user_list = user_tasks.get(list_name, [])

#     for task in user_list:
#         if task['task_name'] == task_name:
#             task['is_completed'] = True
#             break

#     write_json_file(USER_TASKLIST_FILE, tasks)
#     return redirect('/homepage')

@app.route('/toggle_task_completion/<list_name>/<task_name>', methods=["POST"])
def toggle_task_completion(list_name, task_name):
    username = session.get('user_logged_in')

    tasks = read_json_file(USER_TASKLIST_FILE)
    user_tasks = tasks.get(username, {})
    user_list = user_tasks.get(list_name, [])

    for task in user_list:
        if task['task_name'] == task_name:
            task['is_completed'] = not task['is_completed']
            break

    write_json_file(USER_TASKLIST_FILE, tasks)
    return redirect('/homepage')

if __name__ == "__main__":
    app.run(debug=True)
