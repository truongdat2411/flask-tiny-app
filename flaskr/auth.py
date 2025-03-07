import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        elif user['is_blocked']:
            error = 'This account has been blocked.'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            if user['is_admin']:
                return redirect(url_for('auth.admin'))
            else:
                return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

PER_PAGE = 10  

@bp.route('/admin')
def admin():
    db = get_db()
    page = request.args.get('page', 1, type=int)  # Lấy trang hiện tại, mặc định là 1
    offset = (page - 1) * PER_PAGE
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC '
        'LIMIT ? OFFSET ?',
        (PER_PAGE, offset)
    ).fetchall()
    total_posts = db.execute('SELECT COUNT(*) FROM post').fetchone()[0]
    total_pages = (total_posts + PER_PAGE - 1) // PER_PAGE  # Tính tổng số trang
    return render_template('auth/admin.html', posts=posts, page=page, total_pages=total_pages)


@bp.route('/admin/user_management')
def user_management():
    db = get_db()
    users = db.execute(
        'SELECT u.*, COUNT(p.id) as post_count '
        'FROM user u '
        'LEFT JOIN post p ON u.id = p.author_id '
        'WHERE u.id != ? '
        'GROUP BY u.id', 
        (g.user['id'],)
    ).fetchall()
    return render_template('auth/user_management.html', users=users)
    

@bp.route('/admin/toggle-block/<int:user_id>', methods=['POST'])
def toggle_block(user_id):
    if not g.user['is_admin']:
        return redirect(url_for('index'))
    
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    
    if user:
        db.execute(
            'UPDATE user SET is_blocked = ? WHERE id = ?',
            (not user['is_blocked'], user_id)
        )
        db.commit()
        flash(f'User {user["username"]} has been {"blocked" if not user["is_blocked"] else "unblocked"}.')
    
    return redirect(url_for('auth.admin'))


@bp.route('/admin/delete-post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if not g.user['is_admin']:
        return redirect(url_for('index'))
    
    db = get_db()
    post = db.execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()
    
    if post:
        db.execute('DELETE FROM post WHERE id = ?', (post_id,))
        db.commit()
        flash('Post has been deleted successfully.')
    
    return redirect(url_for('auth.admin'))

@bp.route('/admin/reset-password/<int:user_id>', methods=['POST'])
def reset_password(user_id):
    if not g.user['is_admin']:
        return redirect(url_for('index'))
    
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    
    if user:
        new_password = request.form['new_password']
        db.execute(
            'UPDATE user SET password = ? WHERE id = ?',
            (generate_password_hash(new_password), user_id)
        )
        db.commit()
        flash(f'Password for user {user["username"]} has been reset successfully.')
    
    return redirect(url_for('auth.admin'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view