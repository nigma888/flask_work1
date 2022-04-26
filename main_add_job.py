from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.add_job import AddJobForm
from data.login_form import LoginForm
from data.users import User
from data.jobs import Jobs
from data.register import RegisterForm
from data.departments import Department
from data.add_department import AddDepartmentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("index.html", jobs=jobs, names=names, title='Work log')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register', form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register', form=form,
                                   message="This user already exists")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            position=form.position.data,
            email=form.email.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/addjob', methods=['GET', 'POST'])
def addjob():
    add_form = AddJobForm()
    if add_form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = Jobs(
            job=add_form.job.data,
            team_leader=add_form.team_leader.data,
            work_size=add_form.work_size.data,
            collaborators=add_form.collaborators.data,
            is_finished=add_form.is_finished.data
        )
        db_sess.add(jobs)
        db_sess.commit()
        return redirect('/')
    return render_template('addjob.html', title='Adding a job', form=add_form)


@app.route('/updatejob/<int:id>', methods=['GET', 'POST'])
@login_required
def updatejob(id):
    update_form = AddJobForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == id, ((Jobs.user == current_user) | (Jobs.user ==
                                                        db_sess.query(User).filter(User.id == 1).first())))\
            .first()

        if job:
            update_form.job.data = job.job
            update_form.team_leader.data = job.team_leader
            update_form.work_size.data = job.work_size
            update_form.collaborators.data = job.collaborators
            update_form.is_finished.data = job.is_finished
        else:
            abort(404)

    if update_form.validate_on_submit():
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == id, Jobs.user == current_user).first()

        if job:
            job.job = update_form.job.data
            job.team_leader = update_form.team_leader.data
            job.work_size = update_form.work_size.data
            job.collaborators = update_form.collaborators.data
            job.is_finished = update_form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('addjob.html', title='редактирование работы', form=update_form)


@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == id,
                                      Jobs.user == current_user
                                      ).first()
    if Jobs:
        db_sess.delete(job)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/departments')
@login_required
def departments():
    db_sess = db_session.create_session()
    departments = db_sess.query(Department).all()
    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template('departments.html', departments=departments, names=names, title='List of Departments')


@app.route('/departments_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def departments_delete(id):
    db_sess = db_session.create_session()
    department = db_sess.query(Department).filter(Department.id == id, Department.user == current_user).first()
    if Department:
        db_sess.delete(department)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/departments')


@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    add_form = AddDepartmentForm()
    if add_form.validate_on_submit():
        db_sess = db_session.create_session()
        department = Department(
            title=add_form.title.data,
            chief=add_form.chief.data,
            members=add_form.members.data,
            email=add_form.email.data,
        )
        db_sess.add(department)
        db_sess.commit()
        return redirect('/departments')
    return render_template('add_department.html', title='Adding a department', form=add_form)


@app.route('/update_department/<int:id>', methods=['GET', 'POST'])
@login_required
def update_department(id):
    update_form = AddDepartmentForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        job = db_sess.query(Department).filter(Department.id == id, ((Department.user == current_user) | (Department.user ==
                                                        db_sess.query(User).filter(User.id == 1).first())))\
            .first()

        if job:
            update_form.title.data = job.title
            update_form.chief.data = job.chief
            update_form.members.data = job.members
            update_form.email.data = job.email
        else:
            abort(404)

    if update_form.validate_on_submit():
        db_sess = db_session.create_session()
        department = db_sess.query(Department).filter(Department.id == id, Department.user == current_user).first()

        if department:
            department.job = update_form.title.data
            department.team_leader = update_form.chief.data
            department.work_size = update_form.members.data
            department.collaborators = update_form.email.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_department.html', title='редактирование департамента', form=update_form)


def main():
    db_session.global_init("db/mars_explorer.sqlite")

    app.run()


if __name__ == '__main__':
    main()
