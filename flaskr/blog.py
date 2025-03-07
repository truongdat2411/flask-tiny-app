from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

PER_PAGE = 10

@bp.route('/')
@login_required
def index():
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
    return render_template('blog/index.html', posts=posts, page=page, total_pages=total_pages)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.my_posts'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.my_posts'))


@bp.route('/delete_multiple', methods = ['POST'])
@login_required
def delete_multiple():
    post_ids = request.form.getlist('post_ids')  
    if not post_ids:
        flash('No posts selected for deletion.')
        return redirect(url_for('blog.my_posts'))
    
    db = get_db()
    for post_id in post_ids:
        try:
            post = get_post(post_id, check_author=True)
            db.execute('DELETE FROM post WHERE id = ?', (post_id,))
        except abort:
            flash(f'Error deleting post ID {post_id}. You may not have permission.')
            continue
    
    db.commit()
    flash(f'Successfully deleted {len(post_ids)} posts.')
    return redirect(url_for('blog.my_posts'))

@bp.route('/my-posts')
@login_required
def my_posts():
    db = get_db()
    page = request.args.get('page', 1, type=int)  # Lấy trang hiện tại, mặc định là 1
    offset = (page - 1) * PER_PAGE
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.author_id = ?'
        ' ORDER BY created DESC'
        ' LIMIT ? OFFSET ?',
        (g.user['id'], PER_PAGE, offset)
    ).fetchall()
    total_posts = db.execute('SELECT COUNT(*) FROM post WHERE author_id = ?', (g.user['id'],)).fetchone()[0]
    total_pages = (total_posts + PER_PAGE - 1) // PER_PAGE  # Tính tổng số trang
    return render_template('blog/my_posts.html', posts=posts, page=page, total_pages=total_pages)

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post