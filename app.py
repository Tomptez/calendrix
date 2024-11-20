from flask import Flask, render_template, redirect, request, url_for, flash
from flask_table import Col, BoolCol, Table
from pdatabase import get_db, get_options, add_user, create_poodle, get_user
from markupsafe import Markup
from statistics import fmean
from math import ceil
from markupsafe import Markup

app = Flask(__name__, template_folder="templates")
app.secret_key = b'_5#y2L"D6W6bb\n\xec]/'
@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/newpoodle")
def newpoodle():
    title=request.args.get("title", "")
    comment=request.args.get("comment", "")
    error = Markup("<span id='error'> Please provide a title and at least one date </span>") if comment != "" or title != "" else ""
    return render_template("newpoodle.html", title=title, comment=comment, error=error)

@app.route("/submitnewpoodle", methods=["POST"])
def submitnewpoodle():
    title, comment = request.form.get("title", "No title"), request.form.get("comment", "")
    sel = request.form.to_dict(flat=False)
    sel["title"], sel["comment"] = "", ""
    options = []
    for date, times in sel.items():
        for time in times:
            if time != "":
                datestring = f'{date.replace(".","/")}-{time}'
                # Ignore duplicate time entries
                if datestring not in options:
                    options.append(datestring)
    if len(options) == 0 or title == "":
        return redirect(url_for("newpoodle", title=title, comment=comment))
    options.sort(key = lambda x: x.split(", ")[1])
    pid = create_poodle(title, comment, options)
    return redirect(f"/poodle/{pid}")

@app.route("/poodle/<pid>")
def poodle(pid):
    options = get_options(pid)
    
    # Get data
    try:
        items, sum_row, info = get_db(pid)
    except LookupError:
        flash("This poodle does not exist (anymore)")
        return redirect("/")
    
    headday = {}
    headtime = {}
    for o in options.keys():
        date, headtime[o] = o.split("-")
        if date in headday:
            headday[date] += 1
        else:
            headday[date] = 1
    
    # First header row for dates
    header = '<tr id="thday"><th colspan=1></th>'
    for day, count in headday.items():
        header += f'<th colspan={count}>{day}</th>'
    header += '<th colspan=1></th></tr>'
    header = Markup(header)
    
    #  Mean and Max
    lil = [x for x in sum_row.values()][2:]
    maxi = max(lil)
    meani = min(ceil(fmean(lil)), maxi-1)
    
    # Add edit col
    for row in items:
        row["edit"] = Markup(f'<button type="button" class="editbtn" id={row["id"]}>&#128393</button>')
        del row["id"]
        
    # Create "total" row
    lhtml = '<tr>'
    lhtml += f'<td>{sum_row["name"]}</td>'   
    for key in options.keys():
        lhtml += f'<td>{sum_row[key]}</td>'
    lhtml += f'<td></td></tr><tr>'
    
    # Create last row as form for new user input
    lhtml += '<td><form id="form1" method="post"><input type="hidden" name="id" value="1" /></form><input form="form1" type="text" size=12 id="name" name="name" placeholder="Name" required/></td>'   
    for key in options.keys():
        lhtml += f'<td><input form="form1" type="checkbox" name={options[key]} value={True} /></td>'
    lhtml += f'<td><button form="form1" type="submit" formaction="/poodle/{pid}/submituser/new">&#x2714</button></td></tr></form>'
    lhtml = Markup(lhtml)

    # Create table dynamically
    class TableCls(Table):
        table_id = "poodle_tb"
        thead_classes = ["thead_poodle"]

        # One invisible row so table is displayed even if no user exists
        def get_tr_attrs(self, item):
            if item["invisible"] == True:
                return {'class': 'invisible'}
            else:
                return {}

    TableCls.add_column("name", Col(""))
    for k in options.keys():
        TableCls.add_column(k, BoolCol(headtime[k], yes_display='+', no_display='-'))
    TableCls.add_column("edit", Col(""))
    table = TableCls(items)
    
    return render_template("index.html", table=table, lhtml=lhtml, header=header, pid=pid, info=info, max=maxi, mean=meani)

@app.route("/poodle/<pid>/submituser/<uid>", methods=["POST"])
def submituser(pid, uid):
    if request.method == "POST":
        add_user(pid, uid, request.form)
        return redirect(f"/poodle/{pid}")
    else:
        return redirect(f"/poodle/{pid}")

@app.route("/edituser/<pid>/<uid>")
def edituser(pid,uid):
    return redirect(f"/poodle/{pid}")

@app.route("/getrow", methods=["POST"])
def getrow():
    uid = request.values.get("uid")
    user, choices = get_user(uid)
    choices = dict(choices)
    options = get_options(user.post_id)
    lhtml = f'<tr><td><form id={uid} method="post"></form><input form={uid} type="text" size=12 id="name" name="name" value={user.name} required/></td>'
    for o, v in options.items():
        if choices[o] == True:
            lhtml += f'<td><input form={uid} type="checkbox" name={v} value="True" checked/></td>'
        else:
            lhtml += f'<td><input form={uid} type="checkbox" name={v} value="True"></td>'
    
    lhtml += f'<td><button form={uid} type="submit" formaction="/poodle/{user.post_id}/submituser/{uid}">&#x2714</button></td></tr></form>'
    lhtml = Markup(lhtml)
    return lhtml

if __name__ == "__main__":
    app.run(host="localhost", debug="True")
